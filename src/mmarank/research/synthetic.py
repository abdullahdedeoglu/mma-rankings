"""Synthetic MMA-like data with known true win probabilities.

Used only to check the harness (no leakage, sensible selection, models beat a
coin flip and approach the oracle). Nothing here is evidence about real MMA.

World: fighters arrive over time with skill ~ N(0, s0^2) on the logit scale,
skill follows a monthly random walk, fighters retire at a constant monthly
rate. Each week a few events pair available fighters with similar (noisily
observed) skill. P(A beats B) = sigmoid(skill_A - skill_B); 1.4% of bouts are
draws regardless of skill.
"""

from __future__ import annotations

import math
import random
from datetime import date as Date, timedelta

from .stream import Stream, from_records


def generate(seed: int = 1, start: str = "1998-01-01", end: str = "2025-12-31", arrivals_per_week: float = 3.0,
             s0: float = 1.0, walk_sd: float = 0.05, retire_rate: float = 0.01, events_per_week: int = 3,
             bouts_per_event: int = 8, match_noise: float = 1.0, draw_rate: float = 0.014):
    rng = random.Random(seed)
    d = Date.fromisoformat(start)
    stop = Date.fromisoformat(end)
    skill: dict[int, float] = {}
    last_fight: dict[int, Date] = {}
    active: list[int] = []
    records = []
    truth = {}  # fight_id -> P(winner wins)
    fid = eid = nf = 0
    week = 0
    while d <= stop:
        week += 1
        # monthly random walk applied weekly (sd scaled), retirements, arrivals
        wsd = walk_sd * math.sqrt(7 / 30.4375)
        for f in active:
            skill[f] += rng.gauss(0.0, wsd)
        active = [f for f in active if rng.random() > retire_rate * 7 / 30.4375]
        growth = 1.0 + 2.0 * min(week / 900.0, 1.0)  # the sport grows
        for _ in range(int(rng.expovariate(1.0 / (arrivals_per_week * growth)) + 0.5)):
            skill[nf] = rng.gauss(0.0, s0)
            active.append(nf)
            nf += 1
        for e in range(events_per_week):
            day = d + timedelta(days=rng.randrange(7))
            free = [f for f in active if (day - last_fight.get(f, Date.min)).days > 60]
            if len(free) < 2:
                continue
            free.sort(key=lambda f: skill[f] + rng.gauss(0.0, match_noise))
            n = min(int(bouts_per_event * growth), len(free) // 2)
            start_i = rng.randrange(max(1, len(free) - 2 * n + 1))
            eid += 1
            for k in range(n):
                a, b = free[start_i + 2 * k], free[start_i + 2 * k + 1]
                fid += 1
                last_fight[a] = last_fight[b] = day
                p = 1.0 / (1.0 + math.exp(-(skill[a] - skill[b])))
                if rng.random() < draw_rate:
                    records.append((day.isoformat(), fid, eid, a, b, True))
                    continue
                if rng.random() < p:
                    records.append((day.isoformat(), fid, eid, a, b, False))
                    truth[fid] = p
                else:
                    records.append((day.isoformat(), fid, eid, b, a, False))
                    truth[fid] = 1.0 - p
        d += timedelta(days=7)
    return records, truth


def stream(seed: int = 1, **kw) -> tuple[Stream, list[float]]:
    """Synthetic stream (everyone male, nothing unchecked) and the oracle eta per decisive bout."""
    records, truth = generate(seed, **kw)
    sex = {r[3]: "M" for r in records} | {r[4]: "M" for r in records}
    st = from_records(records, sex)
    oracle = [math.log(truth[f] / (1.0 - truth[f])) for f in st.fight_id]
    st.meta = {"synthetic_seed": seed, "decisive": st.n_decisive, "fighters": st.n_fighters}
    return st, oracle
