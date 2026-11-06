"""Evaluation (PROTOCOL §3, §4.2, §6.1): log loss, the scale parameter lambda,
nested rolling-origin selection, secondary metrics and the clustered bootstrap.

Predictions are kept as eta = logit P(actual winner wins), one per decisive
bout, so the log loss of a bout is log(1 + exp(-lambda * eta)).
"""

from __future__ import annotations

import collections
import math
import random
from array import array

from .stream import Stream

EVAL_YEARS = tuple(range(2008, 2026))
ETA_CLIP = math.log((1 - 1e-6) / 1e-6)  # probabilities clipped to [1e-6, 1 - 1e-6]
SEED = 20261105


def bout_loss(x: float) -> float:
    """-log sigmoid(x), with the protocol's clipping."""
    x = max(min(x, ETA_CLIP), -ETA_CLIP)
    return math.log1p(math.exp(-x))


def _sig(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def fit_lambda(groups, start: float = 1.0) -> float:
    """ML scale for p = sigmoid(lambda * eta), all outcomes 'winner won'.
    groups: iterable of eta sequences (pooled). Newton's method on a convex loss."""
    lam = start
    for _ in range(50):
        grad = hess = 0.0
        for etas in groups:
            for e in etas:
                s = _sig(-lam * e)
                grad -= e * s
                hess += e * e * s * (1.0 - s)
        if hess <= 0:
            break
        step = grad / hess
        lam -= step
        if abs(step) < 1e-7:
            break
    return lam


def primary_mask(st: Stream, min_prior: int = 3) -> array:
    return array("b", (1 if st.men[i] and st.prior_min[i] >= min_prior else 0 for i in range(st.n_decisive)))


def by_year(st: Stream, eta, mask) -> dict[int, list[float]]:
    out: dict[int, list[float]] = collections.defaultdict(list)
    yr = st.year
    for i in range(st.n_decisive):
        if mask[i]:
            out[yr[i]].append(eta[i])
    return out


def summarize(st: Stream, eta, mask, years=EVAL_YEARS) -> dict:
    """Everything the selection step needs from one configuration (small; JSON-able)."""
    groups = by_year(st, eta, mask)
    per_year = {y: [len(v), sum(bout_loss(e) for e in v)] for y, v in sorted(groups.items())}
    lam_rows = {}
    lam = 1.0
    for Y in years:
        window = [groups[y] for y in groups if y < Y]
        if not window:
            continue
        lam = fit_lambda(window, lam)
        train = sum(bout_loss(lam * e) for g in window for e in g)
        test = sum(bout_loss(lam * e) for e in groups.get(Y, ()))
        lam_rows[Y] = [lam, train, test]
    full_groups = [groups[y] for y in years if y in groups]
    lam_full = fit_lambda(full_groups, lam)
    full = {"lambda": lam_full,
            "loss_own": sum(per_year[y][1] for y in years if y in per_year),
            "loss_lambda": sum(bout_loss(lam_full * e) for g in full_groups for e in g),
            "n": sum(per_year[y][0] for y in years if y in per_year)}
    return {"per_year": per_year, "lambda": lam_rows, "full": full}


def select(summaries: dict[str, dict], years=EVAL_YEARS) -> dict:
    """Nested rolling-origin selection over one model's grid.
    summaries: config_id -> summarize(...) output (JSON keys may be strings)."""
    def py(s, y):
        return s["per_year"].get(y) or s["per_year"].get(str(y))

    def lr(s, y):
        return s["lambda"].get(y) or s["lambda"].get(str(y))

    out = {"own": {}, "lambda": {}}
    for Y in years:
        best_own = best_lam = None
        for cid, s in summaries.items():
            train = sum(v[1] for k, v in s["per_year"].items() if int(k) < Y)
            if best_own is None or train < best_own[1]:
                best_own = (cid, train)
            row = lr(s, Y)
            if row and (best_lam is None or row[1] < best_lam[1]):
                best_lam = (cid, row[1])
        test_own = py(summaries[best_own[0]], Y)
        n = test_own[0] if test_own else 0
        out["own"][Y] = {"config": best_own[0], "n": n, "loss": test_own[1] if test_own else 0.0}
        row = lr(summaries[best_lam[0]], Y)
        out["lambda"][Y] = {"config": best_lam[0], "lambda": row[0], "n": n, "loss": row[2]}
    for v in ("own", "lambda"):
        n = sum(r["n"] for r in out[v].values())
        out[v + "_total"] = {"n": n, "log_loss": sum(r["loss"] for r in out[v].values()) / n if n else float("nan")}
    best_full = min(summaries, key=lambda c: summaries[c]["full"]["loss_own"])
    best_full_l = min(summaries, key=lambda c: summaries[c]["full"]["loss_lambda"])
    f, fl = summaries[best_full]["full"], summaries[best_full_l]["full"]
    out["full_sequence"] = {"own": {"config": best_full, "log_loss": f["loss_own"] / f["n"]},
                            "lambda": {"config": best_full_l, "lambda": fl["lambda"],
                                       "log_loss": fl["loss_lambda"] / fl["n"]}}
    return out


# ---------------------------------------------------------------- secondary metrics

def metrics(etas, lower_won=None) -> dict:
    """etas: logit P(winner). lower_won (optional): orientation for the calibration fit."""
    n = len(etas)
    if not n:
        return {"n": 0}
    ll = sum(bout_loss(e) for e in etas) / n
    brier = sum((1.0 - _sig(e)) ** 2 for e in etas) / n
    acc = sum(1.0 if e > 0 else 0.5 if e == 0 else 0.0 for e in etas) / n
    out = {"n": n, "log_loss": ll, "brier": brier, "accuracy": acc}
    if lower_won is not None:
        out.update(calibration_fit(etas, lower_won))
    return out


def calibration_fit(etas, lower_won) -> dict:
    """Logistic regression of y on x = logit P(lower-id fighter wins): intercept, slope (Newton)."""
    xs = [e if lw else -e for e, lw in zip(etas, lower_won)]
    ys = list(lower_won)
    a, b = 0.0, 1.0
    for _ in range(50):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, y in zip(xs, ys):
            p = _sig(a + b * x)
            r = y - p
            w = p * (1.0 - p)
            g0 += r
            g1 += r * x
            h00 += w
            h01 += w * x
            h11 += w * x * x
        det = h00 * h11 - h01 * h01
        if det <= 0:
            break
        da = (h11 * g0 - h01 * g1) / det
        db = (h00 * g1 - h01 * g0) / det
        a += da
        b += db
        if abs(da) + abs(db) < 1e-9:
            break
    return {"cal_intercept": a, "cal_slope": b}


def reliability(etas, bins: int = 10) -> list[dict]:
    """Favourite's predicted vs observed win rate (symmetrised)."""
    buckets = [[0, 0.0, 0.0] for _ in range(bins)]
    for e in etas:
        p = _sig(e)
        fav_p, fav_won = (p, 1.0) if e > 0 else (1.0 - p, 0.0) if e < 0 else (0.5, 0.5)
        i = min(int((fav_p - 0.5) / 0.5 * bins), bins - 1)
        buckets[i][0] += 1
        buckets[i][1] += fav_p
        buckets[i][2] += fav_won
    return [{"bin": f"{0.5 + i * 0.05:.2f}", "n": n, "predicted": sp / n, "observed": sw / n}
            for i, (n, sp, sw) in enumerate(buckets) if n]


# ---------------------------------------------------------------- clustered bootstrap

def cluster_bootstrap(diffs, clusters, B: int = 2000, seed: int = SEED) -> dict:
    """Mean per-bout difference with a percentile CI, resampling whole clusters."""
    sums: dict = collections.defaultdict(float)
    cnts: dict = collections.Counter()
    for d, c in zip(diffs, clusters):
        sums[c] += d
        cnts[c] += 1
    keys = list(sums)
    S = [sums[k] for k in keys]
    N = [cnts[k] for k in keys]
    C = len(keys)
    rng = random.Random(seed)
    stats = []
    for _ in range(B):
        idx = [int(rng.random() * C) for _ in range(C)]
        stats.append(sum(S[i] for i in idx) / sum(N[i] for i in idx))
    stats.sort()
    mean = sum(S) / sum(N)
    return {"mean": mean, "lo": stats[int(0.025 * B)], "hi": stats[int(0.975 * B) - 1],
            "clusters": C, "n": sum(N), "B": B}
