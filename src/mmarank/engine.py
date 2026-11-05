"""Chronological rating engine with leak-free monthly snapshots.

Bouts are processed date by date. All bouts on the same date use ratings as they
stood before that date (one Glicko rating period per date), so the order of
bouts within a card never matters. Before each date, every month-end that has
passed is snapshotted; a snapshot therefore only ever sees bouts dated on or
before that month-end.
"""

from __future__ import annotations

import bisect
import collections
from dataclasses import dataclass, field
from datetime import date as Date

from . import glicko
from .config import MODEL, RULES, ModelParams, RankingRules
from .data import Bout, Dataset
from .divisions import to_division

DAYS_PER_MONTH = 30.4375


def _months_between(d0: str, d1: str) -> float:
    return (Date.fromisoformat(d1) - Date.fromisoformat(d0)).days / DAYS_PER_MONTH


def _month_end(ym: str) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    nxt = Date(y + (m == 12), 1 if m == 12 else m + 1, 1)
    return Date.fromordinal(nxt.toordinal() - 1).isoformat()


def _next_month(ym: str) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    return f"{y + (m == 12):04d}-{1 if m == 12 else m + 1:02d}"


def _shift_years(d: str, years: int) -> str:
    return f"{int(d[:4]) - years:04d}{d[4:]}"


def _shift_months(d: str, months: int) -> str:
    y, m = int(d[:4]), int(d[5:7]) - months
    while m <= 0:
        m += 12
        y -= 1
    return f"{y:04d}-{m:02d}{d[7:]}"


@dataclass
class FighterState:
    mu: float
    rd: float
    last: str  # date of last rating update
    w: int = 0
    l: int = 0
    d: int = 0

    @property
    def n(self) -> int:
        return self.w + self.l + self.d


@dataclass
class Prediction:
    date: str
    fight_id: int
    a: int  # actual winner
    b: int
    p_a: float  # pre-fight probability that a wins
    n_a: int
    n_b: int
    promotion: str
    method_class: str


@dataclass
class RunResult:
    snapshots: dict[str, list[dict]]  # 'YYYY-MM' -> eligible fighter rows
    predictions: list[Prediction]
    states: dict[int, FighterState]
    last_date: str
    stats: dict = field(default_factory=dict)


class _Timeline:
    """Static per-fighter lookups: labelled divisions and Big-9 org appearances."""

    def __init__(self, ds: Dataset):
        self.div: dict[int, list[tuple[str, str]]] = collections.defaultdict(list)
        self.org: dict[int, list[tuple[str, str]]] = collections.defaultdict(list)
        for b in ds.bouts:
            for f in (b.a, b.b):
                if b.div_key:
                    self.div[f].append((b.date, b.div_key))
                if b.org:
                    self.org[f].append((b.date, b.org))
        for v in self.div.values():
            v.sort()
        for v in self.org.values():
            v.sort()

    def division_key(self, f: int, t: str, rules: RankingRules) -> tuple[str | None, str]:
        labels = self.div.get(f)
        if not labels:
            return None, "none"
        i = bisect.bisect_right(labels, (t, "￿"))
        past = labels[:i]
        lo = _shift_years(t, rules.division_lookback_years)
        recent = [k for d, k in past if d >= lo][-rules.division_last_n:]
        if recent:
            counts = collections.Counter(recent)
            top = max(counts.values())
            for k in reversed(recent):  # most recent among the most frequent
                if counts[k] == top:
                    return k, "past"
        if i < len(labels):
            return labels[i][1], "future"
        return past[-1][1], "old"

    def orgs_at(self, f: int, t: str, rules: RankingRules) -> list[str]:
        apps = self.org.get(f)
        if not apps:
            return []
        lo = _shift_months(t, rules.org_window_months)
        i = bisect.bisect_right(apps, (t, "￿"))
        j = bisect.bisect_left(apps, (lo, ""))
        return sorted({o for _, o in apps[j:i]})


def run(ds: Dataset, model: ModelParams = MODEL, rules: RankingRules = RULES,
        snapshots: bool = True, until: str | None = None) -> RunResult:
    states: dict[int, FighterState] = {}
    preds: list[Prediction] = []
    snaps: dict[str, list[dict]] = {}
    timeline = _Timeline(ds) if snapshots else None
    active: dict[int, str] = {}  # fighter -> last bout date (pruned lazily)

    by_date: dict[str, list[Bout]] = collections.defaultdict(list)
    for b in ds.bouts:
        if until and b.date > until:
            continue
        by_date[b.date].append(b)
    dates = sorted(by_date)
    if not dates:
        raise ValueError("no bouts to rate")

    next_snap = rules.first_published_month

    def state_at(f: int, t: str) -> FighterState:
        s = states.get(f)
        if s is None:
            s = FighterState(model.initial_rating, model.initial_rd, t)
            states[f] = s
        return s

    def snapshot(ym: str) -> None:
        t = min(_month_end(ym), dates[-1])  # current month: as of the latest bout
        cutoff = _shift_months(t, rules.active_months)
        rows = []
        for f in list(active):
            if active[f] < cutoff:
                del active[f]
                continue
            s = states[f]
            if s.n < rules.min_fights:
                continue
            sex = ds.sex.get(f)
            key, src = timeline.division_key(f, t, rules)
            div = to_division(key, sex)
            rd = glicko.inflate(s.rd, _months_between(s.last, t), model.c, model.initial_rd)
            rows.append({
                "id": f, "mu": s.mu, "rd": rd, "score": s.mu - model.display_k * rd,
                "w": s.w, "l": s.l, "d": s.d, "last": active[f], "sex": sex,
                "div": div, "div_src": src, "orgs": timeline.orgs_at(f, t, rules),
            })
        snaps[ym] = rows

    for day in dates:
        if snapshots:
            while _month_end(next_snap) < day:
                snapshot(next_snap)
                next_snap = _next_month(next_snap)
        bouts = by_date[day]
        # Pre-period ratings with RD inflated to today.
        pre: dict[int, tuple[float, float]] = {}
        for b in bouts:
            for f in (b.a, b.b):
                if f not in pre:
                    s = state_at(f, day)
                    rd = glicko.inflate(s.rd, _months_between(s.last, day), model.c, model.initial_rd)
                    pre[f] = (s.mu, rd)
        games: dict[int, list[tuple[float, float, float]]] = collections.defaultdict(list)
        for b in bouts:
            (mu_a, rd_a), (mu_b, rd_b) = pre[b.a], pre[b.b]
            if b.draw:
                sa = 0.5
            else:
                sa = model.outcome.get(b.method_class, 1.0)
                preds.append(Prediction(day, b.fight_id, b.a, b.b,
                                        glicko.win_probability(mu_a, rd_a, mu_b, rd_b),
                                        states[b.a].n, states[b.b].n, b.promotion, b.method_class))
            games[b.a].append((mu_b, rd_b, sa))
            games[b.b].append((mu_a, rd_a, 1.0 - sa))
        for f, gl in games.items():
            mu, rd = pre[f]
            new_mu, new_rd = glicko.update(mu, rd, gl, model.min_rd)
            s = states[f]
            s.mu, s.rd, s.last = new_mu, new_rd, day
            active[f] = day
        for b in bouts:
            if b.draw:
                states[b.a].d += 1
                states[b.b].d += 1
            else:
                states[b.a].w += 1
                states[b.b].l += 1

    last = dates[-1]
    if snapshots:
        final_month = last[:7]
        while next_snap <= final_month:
            snapshot(next_snap)
            next_snap = _next_month(next_snap)
    return RunResult(snaps, preds, states, last, {"dates": len(dates), "fighters": len(states)})
