"""Load a Fight Canon release into clean, rating-ready bouts.

Pipeline: read -> filter (pro, decided) -> classify method -> drop near-duplicates
-> infer sex -> attach division keys. Every dropped bout is counted in a report
so nothing disappears silently.
"""

from __future__ import annotations

import collections
import csv
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import date as Date
from pathlib import Path

from . import divisions, methods
from .config import EXTERNAL_DIR, ORGS, RULES


@dataclass
class Bout:
    fight_id: int
    event_id: int
    date: str
    promotion: str
    weight_class: str | None
    title: bool
    method_class: str
    a: int  # winner, or first fighter of a draw
    b: int
    draw: bool
    card_complete: bool
    method_raw: str | None
    div_key: str | None = None
    women_label: bool = False

    @property
    def org(self) -> str | None:
        return _ORG_BY_LABEL.get(self.promotion)


_ORG_BY_LABEL = {label: key for key, (_, labels) in ORGS.items() for label in labels}


@dataclass
class Dataset:
    bouts: list[Bout]
    names: dict[int, str]
    sex: dict[int, str]
    report: dict = field(default_factory=dict)
    sex_conflicts: list = field(default_factory=list)
    duplicates: list = field(default_factory=list)


def _connect(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?mode=ro", uri=True)


def read_bouts(db: sqlite3.Connection, report: dict) -> list[Bout]:
    rows = db.execute(
        """
        SELECT f.fight_id, f.event_id, e.date, e.promotion, f.weight_class, f.title_fight,
               f.method, f.overturned, f.no_contest, f.bout_type,
               COALESCE(c.complete, 0),
               p0.fighter_id, p0.result, p1.fighter_id, p1.result
        FROM fights f
        JOIN events e USING(event_id)
        JOIN fight_participants p0 ON p0.fight_id = f.fight_id AND p0.corner = 0
        JOIN fight_participants p1 ON p1.fight_id = f.fight_id AND p1.corner = 1
        LEFT JOIN event_cards c ON c.event_id = f.event_id
        """
    ).fetchall()
    out: list[Bout] = []
    drop = collections.Counter()
    for (fid, eid, d, promo, wc, title, method, overturned, nc, btype, complete,
         f0, r0, f1, r1) in rows:
        if btype not in (None, "pro"):
            drop["not_pro"] += 1
            continue
        if not d:
            drop["no_date"] += 1
            continue
        if f0 == f1:
            drop["self_fight"] += 1
            continue
        mc = methods.classify(method)
        if overturned or nc or r0 == "NC" or mc in methods.EXCLUDED:
            drop[f"excluded_{'NC' if (overturned or nc or r0 == 'NC') else mc}"] += 1
            continue
        if {r0, r1} == {"W", "L"}:
            a, b = (f0, f1) if r0 == "W" else (f1, f0)
            draw = False
            if mc == "DRAW":
                mc = "OTHER"
        elif r0 == r1 == "D":
            a, b, draw, mc = f0, f1, True, "DRAW"
        else:
            drop["bad_result"] += 1
            continue
        out.append(Bout(fid, eid, d, promo, wc, bool(title), mc, a, b, draw, bool(complete), method))
    report["read"] = len(rows)
    report["dropped"] = dict(drop)
    return out


def _detail_score(b: Bout) -> tuple:
    raw = b.method_raw or ""
    return (b.card_complete, "(" in raw, len(raw), b.org is not None, -b.fight_id)


def drop_near_duplicates(bouts: list[Bout], report: dict) -> tuple[list[Bout], list]:
    """Same two fighters, same outcome, different events within N days -> one bout.

    Keeps the most detailed record (complete card, detailed method). Pairs with a
    different outcome are kept: they are more likely real rematches.
    """
    window = RULES.dedup_window_days
    by_pair: dict[tuple, list[Bout]] = collections.defaultdict(list)
    for b in bouts:
        by_pair[(min(b.a, b.b), max(b.a, b.b))].append(b)
    removed: set[int] = set()
    log = []
    for group in by_pair.values():
        if len(group) < 2:
            continue
        group.sort(key=lambda x: x.date)
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                x, y = group[i], group[j]
                if x.fight_id in removed or y.fight_id in removed or x.event_id == y.event_id:
                    continue
                gap = (Date.fromisoformat(y.date) - Date.fromisoformat(x.date)).days
                if gap > window:
                    break
                same = (x.draw and y.draw) or (not x.draw and not y.draw and x.a == y.a)
                if not same:
                    continue
                keep, drop = (x, y) if _detail_score(x) >= _detail_score(y) else (y, x)
                removed.add(drop.fight_id)
                log.append({"kept": keep.fight_id, "kept_date": keep.date,
                            "dropped": drop.fight_id, "dropped_date": drop.date,
                            "kept_promotion": keep.promotion, "dropped_promotion": drop.promotion})
    report["near_duplicates_removed"] = len(removed)
    return [b for b in bouts if b.fight_id not in removed], log


def infer_sex(db: sqlite3.Connection, bouts: list[Bout], wikidata_csv: Path | None) -> tuple[dict, list, dict]:
    """Seeds (Fight Canon sex, Wikidata via Sherdog id, women's labels), then
    breadth-first propagation over opponents: in MMA, women fight women."""
    seed: dict[int, str] = {f: s for f, s in db.execute("SELECT fighter_id, sex FROM fighters") if s in ("M", "F")}
    n_canon = len(seed)
    n_wd = 0
    if wikidata_csv and wikidata_csv.exists():
        wd = {}
        with open(wikidata_csv, newline="") as fh:
            for r in csv.DictReader(fh):
                lab = r.get("sexLabel", "")
                if lab in ("male", "female"):
                    wd[r["sherdog"].strip()] = "M" if lab == "male" else "F"
        for fid, sid in db.execute("SELECT fighter_id, source_id FROM fighter_aliases WHERE source='sherdog'"):
            m = re.search(r"(\d+)$", sid)
            if m and m.group(1) in wd and fid not in seed:
                seed[fid] = wd[m.group(1)]
                n_wd += 1
    n_label = 0
    for b in bouts:
        if b.women_label:
            for f in (b.a, b.b):
                if f not in seed:
                    seed[f] = "F"
                    n_label += 1
    adj = collections.defaultdict(set)
    for b in bouts:
        adj[b.a].add(b.b)
        adj[b.b].add(b.a)
    sex = dict(seed)
    frontier = list(seed)
    conflicts = set()
    while frontier:
        nxt = []
        for x in frontier:
            for y in adj[x]:
                if y not in sex:
                    sex[y] = sex[x]
                    nxt.append(y)
                elif sex[y] != sex[x]:
                    conflicts.add((min(x, y), max(x, y)))
        frontier = nxt
    stats = {"seed_fight_canon": n_canon, "seed_wikidata": n_wd, "seed_women_label": n_label,
             "labelled_after_propagation": len(sex), "female": sum(v == "F" for v in sex.values()),
             "conflict_edges": len(conflicts)}
    return sex, sorted(conflicts), stats


def load(canon_db: Path, wikidata_csv: Path | None = EXTERNAL_DIR / "wikidata_sherdog_sex.csv") -> Dataset:
    report: dict = {}
    db = _connect(canon_db)
    bouts = read_bouts(db, report)
    for b in bouts:
        b.div_key, b.women_label = divisions.label_key(b.weight_class, b.promotion, b.date)
    bouts, dup_log = drop_near_duplicates(bouts, report)
    sex, conflicts, sex_stats = infer_sex(db, bouts, wikidata_csv)
    report["sex"] = sex_stats
    names = dict(db.execute("SELECT fighter_id, name FROM fighters"))
    bouts.sort(key=lambda x: (x.date, x.fight_id))
    report["bouts"] = len(bouts)
    report["method_classes"] = dict(collections.Counter(b.method_class for b in bouts))
    report["with_division_key"] = sum(b.div_key is not None for b in bouts)
    db.close()
    return Dataset(bouts, names, sex, report, conflicts, dup_log)
