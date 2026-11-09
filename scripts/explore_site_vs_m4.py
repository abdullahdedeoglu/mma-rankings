"""Exploratory (not pre-registered): the site's Glicko model, with and without its two extras,
scored on the same bouts and population as the S1 comparison."""
import json
import math
from array import array
from dataclasses import replace

from mmarank import data, engine
from mmarank.config import BUILD_DIR, MODEL, RAW_DIR
from mmarank.research import evaluate, grid, report, stream

OUT = BUILD_DIR / "research" / stream.TAG
st = stream.load()
ds = data.load(RAW_DIR / stream.TAG / "canon.db")
pos = {fid: i for i, fid in enumerate(st.fight_id)}
pops = report.populations(st)
prim = pops["primary"]

flat = {k: 1.0 for k in MODEL.outcome}
variants = {
    "site": MODEL,
    "site_no_method": replace(MODEL, outcome=flat),
    "site_no_promo": replace(MODEL, promo_prior=False),
    "site_plain": replace(MODEL, outcome=flat, promo_prior=False),
}
etas = {}
for name, mp in variants.items():
    res = engine.run(ds, model=mp, snapshots=False)
    eta = array("d", [float("nan")]) * st.n_decisive
    hit = 0
    for p in res.predictions:
        i = pos.get(p.fight_id)
        if i is None:
            continue
        q = min(max(p.p_a, 1e-12), 1 - 1e-12)
        eta[i] = math.log(q / (1 - q))
        hit += 1
    miss = sum(1 for i in prim if math.isnan(eta[i]))
    print(name, "matched", hit, "missing in primary", miss, flush=True)
    etas[name] = eta

sel = {m: json.loads((OUT / f"selection_{m}.json").read_text()) for m in ("M1", "M4")}
etas["M1"] = report.procedure_eta(st, OUT, "M1", "own", sel["M1"])
etas["M4"] = report.procedure_eta(st, OUT, "M4", "own", sel["M4"])

res = {"primary": {}, "secondary": {}, "comparisons": {}}
for k, e in etas.items():
    s = report.summary(st, e, pops)
    res["primary"][k] = s["primary"]
    res["secondary"][k] = {p: round(v["log_loss"], 5) for p, v in s.items()}
    p = s["primary"]
    print(f"{k:16} ll {p['log_loss']:.5f} brier {p['brier']:.5f} acc {p['accuracy']:.4f} "
          f"slope {p['cal_slope']:.3f} int {p['cal_intercept']:.3f}", flush=True)

for a, b in [("site", "M1"), ("site", "site_plain"), ("site_no_method", "site_plain"),
             ("site_no_promo", "site_plain"), ("M4", "site"), ("site_plain", "M1")]:
    c = report.compare(st, etas[a], etas[b], prim, 2000)
    res["comparisons"][f"{a} - {b}"] = c
    print(f"{a} - {b}: {c['mean']:+.5f} event [{c['event_ci'][0]:+.5f}, {c['event_ci'][1]:+.5f}] "
          f"month [{c['month_ci'][0]:+.5f}, {c['month_ci'][1]:+.5f}] brier {c['brier_diff']:+.5f}", flush=True)
(OUT / "explore_site_vs_m4.json").write_text(json.dumps(res, indent=1, default=float))
print("secondary", json.dumps(res["secondary"], indent=1))
