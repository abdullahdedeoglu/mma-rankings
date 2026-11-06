"""Comparison report for the nested-selected procedures (PROTOCOL §3, §5, §6.1).

A "procedure" is model + variant (own formula or lambda) + the nested selection:
in each test year it uses the configuration (and lambda) chosen on earlier years.
"""

from __future__ import annotations

import json
import math
from array import array
from pathlib import Path

from . import evaluate, grid
from .stream import Stream

NAN = float("nan")


def procedure_eta(st: Stream, out: Path, model: str, variant: str, selection: dict) -> array:
    """eta per decisive bout for test years (NaN elsewhere), using each year's selected config."""
    eta = array("d", [NAN]) * st.n_decisive
    cache: dict[str, array] = {}
    rows = selection[variant]
    for i in range(st.n_decisive):
        y = st.year[i]
        row = rows.get(str(y)) or rows.get(y)
        if row is None:
            continue
        cid = row["config"]
        if cid not in cache:
            cache[cid] = grid.load_eta(out, model, cid)
        lam = row.get("lambda", 1.0) if variant == "lambda" else 1.0
        eta[i] = lam * cache[cid][i]
    return eta


def populations(st: Stream, years=evaluate.EVAL_YEARS) -> dict[str, list[int]]:
    y0, y1 = years[0], years[-1]
    test = [i for i in range(st.n_decisive) if y0 <= st.year[i] <= y1]
    prim = [i for i in test if st.men[i] and st.prior_min[i] >= 3]
    pops = {"primary": prim, "all": test}
    for lo, hi, name in ((0, 0, "exp_0"), (1, 2, "exp_1-2"), (3, 9, "exp_3-9"), (10, 10 ** 9, "exp_10+")):
        pops[name] = [i for i in test if st.men[i] and lo <= st.prior_min[i] <= hi]
    for lo, hi in ((2008, 2009), (2010, 2014), (2015, 2019), (2020, 2025)):
        pops[f"primary_{lo}-{hi}"] = [i for i in prim if lo <= st.year[i] <= hi]
    pops["primary_checked_only"] = [i for i in prim if not st.unchecked[i]]
    return pops


def compare(st: Stream, eta_a, eta_b, idx, B: int = 2000) -> dict:
    """Paired per-bout log-loss difference a - b (negative: a better), two cluster schemes."""
    la = [evaluate.bout_loss(eta_a[i]) for i in idx]
    lb = [evaluate.bout_loss(eta_b[i]) for i in idx]
    diffs = [x - y for x, y in zip(la, lb)]
    brier = sum((1 - evaluate._sig(eta_a[i])) ** 2 - (1 - evaluate._sig(eta_b[i])) ** 2 for i in idx) / len(idx)
    ev = evaluate.cluster_bootstrap(diffs, [st.event[i] for i in idx], B)
    mo = evaluate.cluster_bootstrap(diffs, [st.month[i] for i in idx], B)
    sd = math.sqrt(sum((d - ev["mean"]) ** 2 for d in diffs) / (len(diffs) - 1))
    return {"mean": ev["mean"], "event_ci": [ev["lo"], ev["hi"]], "month_ci": [mo["lo"], mo["hi"]],
            "brier_diff": brier, "sd_per_bout": sd, "n": len(idx), "events": ev["clusters"], "months": mo["clusters"]}


def summary(st: Stream, eta, pops) -> dict:
    out = {}
    for name, idx in pops.items():
        if idx:
            out[name] = evaluate.metrics([eta[i] for i in idx], [st.lower_won[i] for i in idx])
    return out


def save(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=1, default=float))


COMPARISONS = [  # (a, b): a - b, negative means a is better
    ("M0/own", "M1/own"), ("M2/own", "M1/own"), ("M3/own", "M1/own"),
    ("M0/lambda", "M0/own"), ("M1/lambda", "M1/own"), ("M2/lambda", "M2/own"), ("M3/lambda", "M3/own"),
    ("M3/lambda", "M1/own"),
]


def run_s1(st: Stream, out: Path, models=("M0", "M1", "M2", "M3"), B: int = 2000, verbose: bool = True) -> dict:
    sel = {m: json.loads((out / f"selection_{m}.json").read_text()) for m in models}
    etas = {f"{m}/{v}": procedure_eta(st, out, m, v, sel[m]) for m in models for v in ("own", "lambda")}
    pops = populations(st)
    res = {"populations": {k: len(v) for k, v in pops.items()}, "procedures": {}, "comparisons": {}}
    for name, eta in etas.items():
        res["procedures"][name] = summary(st, eta, pops)
        if verbose:
            p = res["procedures"][name]["primary"]
            print(name, {k: round(v, 5) for k, v in p.items() if k != "n"}, flush=True)
    for a, b in COMPARISONS:
        c = compare(st, etas[a], etas[b], pops["primary"], B)
        c["checked_only"] = compare(st, etas[a], etas[b], pops["primary_checked_only"], 200)
        res["comparisons"][f"{a} - {b}"] = c
        if verbose:
            print(f"{a} - {b}: {c['mean']:+.5f} event {[round(x, 5) for x in c['event_ci']]} "
                  f"month {[round(x, 5) for x in c['month_ci']]} brier {c['brier_diff']:+.5f}", flush=True)
    save(out / "report_s1.json", res)
    return res
