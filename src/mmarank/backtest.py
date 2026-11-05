"""Walk-forward evaluation. Every prediction is made before the bout, from bouts
strictly earlier in time, so the whole run is one long out-of-sample test.

Splits: parameters are tuned on <= TRAIN_END, compared on VALID, reported on TEST.
"""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .engine import Prediction

TRAIN_END = "2015-12-31"
VALID = ("2016-01-01", "2020-12-31")
TEST_START = "2021-01-01"
EPS = 1e-6


@dataclass
class Metrics:
    n: int
    log_loss: float
    brier: float
    accuracy: float

    def row(self) -> dict:
        return {"n": self.n, "log_loss": round(self.log_loss, 4), "brier": round(self.brier, 4),
                "accuracy": round(self.accuracy, 4)}


def metrics(probs: list[float]) -> Metrics:
    """probs = model probability assigned to the ACTUAL winner."""
    n = len(probs)
    if n == 0:
        return Metrics(0, float("nan"), float("nan"), float("nan"))
    ll = -sum(math.log(min(max(p, EPS), 1 - EPS)) for p in probs) / n
    brier = sum((1 - p) ** 2 for p in probs) / n
    # ties at exactly 0.5 count as half right
    acc = sum(1.0 if p > 0.5 else 0.5 if p == 0.5 else 0.0 for p in probs) / n
    return Metrics(n, ll, brier, acc)


def select(preds: list[Prediction], start: str = "", end: str = "9999", min_prior: int = 0,
           promotions: set[str] | None = None) -> list[Prediction]:
    return [p for p in preds if start <= p.date <= end and min(p.n_a, p.n_b) >= min_prior
            and (promotions is None or p.promotion in promotions)]


def calibration(preds: list[Prediction], bins: int = 10) -> list[dict]:
    """Reliability table, symmetrised: each bout counted from the favourite's side."""
    buckets = [[0, 0.0, 0.0] for _ in range(bins)]
    for p in preds:
        fav_p = max(p.p_a, 1 - p.p_a)
        # exact 0.5 (e.g. two debutants): no favourite, counts as half a win
        fav_won = 1.0 if p.p_a > 0.5 else 0.5 if p.p_a == 0.5 else 0.0
        i = min(int((fav_p - 0.5) / 0.5 * bins), bins - 1)
        buckets[i][0] += 1
        buckets[i][1] += fav_p
        buckets[i][2] += fav_won
    out = []
    for i, (n, sp, sw) in enumerate(buckets):
        if n:
            out.append({"bin": f"{0.5 + i * 0.5 / bins:.2f}-{0.5 + (i + 1) * 0.5 / bins:.2f}",
                        "n": n, "predicted": round(sp / n, 3), "observed": round(sw / n, 3)})
    return out


def _implied(american: int | None) -> float | None:
    if american is None or american == 0:
        return None
    return 100 / (american + 100) if american > 0 else -american / (-american + 100)


def odds_probs(canon_db: Path) -> dict[int, dict[int, float]]:
    """Vig-free closing probabilities: fight_id -> {fighter_id: p}. Uses the
    midpoint of the lowest and highest close across books."""
    db = sqlite3.connect(f"file:{canon_db}?mode=ro", uri=True)
    raw: dict[int, dict[int, float]] = {}
    for fid, fr, lo, hi, close in db.execute(
            "SELECT fight_id, fighter_id, close_low, close_high, close FROM odds WHERE book='all'"):
        ps = [x for x in (_implied(lo), _implied(hi)) if x is not None] or \
             [x for x in (_implied(close),) if x is not None]
        if ps:
            raw.setdefault(fid, {})[fr] = sum(ps) / len(ps)
    db.close()
    out = {}
    for fid, d in raw.items():
        if len(d) == 2:
            s = sum(d.values())
            out[fid] = {k: v / s for k, v in d.items()}
    return out


def report(preds: list[Prediction], odds: dict[int, dict[int, float]] | None = None) -> dict:
    periods = {"train": ("", TRAIN_END), "valid": VALID, "test": (TEST_START, "9999")}
    out: dict = {"periods": {}}
    for name, (s, e) in periods.items():
        sel = select(preds, s, e)
        sel3 = select(preds, s, e, min_prior=3)
        out["periods"][name] = {
            "all": metrics([p.p_a for p in sel]).row(),
            "both_3plus_prior": metrics([p.p_a for p in sel3]).row(),
        }
    if odds:
        both = [p for p in preds if p.fight_id in odds and p.a in odds[p.fight_id]]
        for name, (s, e) in periods.items():
            sel = [p for p in both if s <= p.date <= e]
            out["periods"][name]["odds_subset_model"] = metrics([p.p_a for p in sel]).row()
            out["periods"][name]["odds_subset_market"] = metrics([odds[p.fight_id][p.a] for p in sel]).row()
    eras = [("1993", "1999-12-31"), ("2000", "2004-12-31"), ("2005", "2009-12-31"),
            ("2010", "2014-12-31"), ("2015", "2019-12-31"), ("2020", "9999")]
    out["by_era"] = {s[:4] + "-" + e[:4]: metrics([p.p_a for p in select(preds, s, e)]).row() for s, e in eras}
    out["by_prior_fights"] = {
        f"min_prior>={k}": metrics([p.p_a for p in preds if min(p.n_a, p.n_b) >= k and (k == 10 or min(p.n_a, p.n_b) < nxt)]).row()
        for k, nxt in [(0, 1), (1, 3), (3, 10), (10, 10**9)]
    }
    out["calibration_test"] = calibration(select(preds, TEST_START))
    out["baseline_coin_flip_log_loss"] = round(math.log(2), 4)
    return out
