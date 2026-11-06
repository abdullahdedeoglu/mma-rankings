"""Pre-registered hyperparameter grids (PROTOCOL §6.1) and a parallel runner.

Each configuration is run once over the whole stream. Its predictions (eta per
decisive bout, float32) and a small JSON summary are written to
<out>/<model>/<config>.{eta,json}; finished configurations are skipped, so a run
can be resumed.
"""

from __future__ import annotations

import itertools
import json
import multiprocessing as mp
import os
import time
from array import array
from pathlib import Path

from . import evaluate, models
from .stream import Stream


def _product(**axes) -> list[dict]:
    keys = list(axes)
    return [dict(zip(keys, vals)) for vals in itertools.product(*(axes[k] for k in keys))]


GRIDS: dict[str, list[dict]] = {
    "M0": _product(K=[16, 24, 32, 48, 64, 80, 96, 128, 160, 200, 256]),
    "M1": _product(c=[0, 10, 20, 30, 40, 55, 70, 90], rd0=[150, 200, 250, 300, 350, 450], min_rd=[0, 30, 50, 70]),
    "M2": _product(tau=[0.2, 0.5, 0.8, 1.2], rd0=[150, 200, 250, 300, 350, 450],
                   sigma0=[0.03, 0.06, 0.12, 0.2, 0.3, 0.4]),
    "M3": _product(sigma0=[0.5, 1, 1.5, 2, 3, 4], gamma=[0, 0.05, 0.1, 0.15, 0.2, 0.3],
                   p_draw=[0.005, 0.014, 0.03]),
}
PARAM_COUNT = {"M0": 1, "M1": 3, "M2": 3, "M3": 3}
# Natural grid edges that do not trigger the extension rule (PROTOCOL §6.1, item 5).
NATURAL_EDGES = {("M1", "c", 0), ("M1", "min_rd", 0), ("M3", "gamma", 0)}


def config_id(params: dict) -> str:
    return ",".join(f"{k}={v}" for k, v in params.items())


def parse_id(cid: str) -> dict:
    out = {}
    for part in cid.split(","):
        k, v = part.rsplit("=", 1)
        out[k] = float(v) if "." in v else int(v)
    return out


_ST: Stream | None = None
_MASK = None


def _work(job):
    model, params, outdir = job
    cid = config_id(params)
    t0 = time.time()
    eta = models.run(model, _ST, params)
    summary = evaluate.summarize(_ST, eta, _MASK)
    summary.update({"model": model, "params": params, "seconds": round(time.time() - t0, 1)})
    with open(outdir / f"{cid}.eta", "wb") as fh:
        array("f", eta).tofile(fh)
    (outdir / f"{cid}.json").write_text(json.dumps(summary))
    return model, cid, summary["seconds"]


def run_grid(st: Stream, model_names, out: Path, workers: int | None = None, verbose: bool = True) -> None:
    global _ST, _MASK
    _ST = st
    _MASK = evaluate.primary_mask(st)
    jobs = []
    for m in model_names:
        d = out / m
        d.mkdir(parents=True, exist_ok=True)
        for p in GRIDS[m]:
            if not (d / f"{config_id(p)}.json").exists():
                jobs.append((m, p, d))
    if verbose:
        print(f"{len(jobs)} configurations to run", flush=True)
    if not jobs:
        return
    workers = workers or max(1, (os.cpu_count() or 2) - 1)
    ctx = mp.get_context("fork")  # workers inherit the stream; no reload per process
    with ctx.Pool(workers) as pool:
        for k, (m, cid, sec) in enumerate(pool.imap_unordered(_work, jobs), 1):
            if verbose:
                print(f"[{k}/{len(jobs)}] {m} {cid} {sec}s", flush=True)


def load_summaries(out: Path, model: str) -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text()) for p in sorted((out / model).glob("*.json"))}


def load_eta(out: Path, model: str, cid: str) -> array:
    a = array("f")
    with open(out / model / f"{cid}.eta", "rb") as fh:
        a.frombytes(fh.read())
    return a


def edge_hits(model: str, selection: dict) -> list[str]:
    """Selected configurations on a grid edge (extension rule, PROTOCOL §6.1 item 5)."""
    axes = {k: sorted({p[k] for p in GRIDS[model]}) for k in GRIDS[model][0]}
    hits = set()
    for variant in ("own", "lambda"):
        for Y, row in selection[variant].items():
            params = parse_id(row["config"])
            for k, v in params.items():
                vals = axes[k]
                if len(vals) > 1 and v in (vals[0], vals[-1]) and (model, k, v) not in NATURAL_EDGES:
                    hits.add(f"{variant}: {k}={v} ({'min' if v == vals[0] else 'max'})")
    return sorted(hits)
