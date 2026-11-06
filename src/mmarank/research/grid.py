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


# Pre-registered axes (PROTOCOL §6.1, v0.9).
AXES: dict[str, dict[str, list]] = {
    "M0": {"K": [16, 24, 32, 48, 64, 80, 96, 128, 160, 200, 256]},
    "M1": {"c": [0, 10, 20, 30, 40, 55, 70, 90], "rd0": [150, 200, 250, 300, 350, 450], "min_rd": [0, 30, 50, 70]},
    "M2": {"tau": [0.2, 0.5, 0.8, 1.2], "rd0": [150, 200, 250, 300, 350, 450],
           "sigma0": [0.03, 0.06, 0.12, 0.2, 0.3, 0.4]},
    "M3": {"sigma0": [0.5, 1, 1.5, 2, 3, 4], "gamma": [0, 0.05, 0.1, 0.15, 0.2, 0.3], "p_draw": [0.005, 0.014, 0.03]},
    # M4 (protocol v0.10): the same pre-registered axes as M3, without M3's result-driven extensions.
    "M4": {"sigma0": [0.5, 1, 1.5, 2, 3, 4], "gamma": [0, 0.05, 0.1, 0.15, 0.2, 0.3], "p_draw": [0.005, 0.014, 0.03]},
}
# Extensions made by the grid-edge rule (§6.1 item 5), one list per round; logged in EXPERIMENTS.md.
EXTENSIONS: list[dict[str, dict[str, list]]] = [
    # round 1 (2026-11-06, E2.1)
    {"M1": {"rd0": [550]}, "M2": {"tau": [1.6], "rd0": [550]}, "M3": {"p_draw": [0.046]}},
    # round 2 (2026-11-06, E2.1)
    {"M2": {"tau": [2.0]}, "M3": {"p_draw": [0.062]}},
    # round 3 (2026-11-06, E2.1): last one allowed for p_draw
    {"M3": {"p_draw": [0.078]}},
]
MAX_EXTENSIONS = 3


def axes(model: str) -> dict[str, list]:
    ax = {k: list(v) for k, v in AXES[model].items()}
    for rnd in EXTENSIONS:
        for k, vals in rnd.get(model, {}).items():
            ax[k] = sorted(set(ax[k]) | set(vals))
    return ax


GRIDS: dict[str, list[dict]] = {m: _product(**axes(m)) for m in AXES}
PARAM_COUNT = {"M0": 1, "M1": 3, "M2": 3, "M3": 3, "M4": 3}
# Natural grid edges that do not trigger the extension rule (PROTOCOL §6.1, item 5).
NATURAL_EDGES = {("M1", "c", 0), ("M1", "min_rd", 0), ("M3", "gamma", 0), ("M4", "gamma", 0)}


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
    """Selected configurations on a grid edge (extension rule, PROTOCOL §6.1 item 5).
    Each hit says the next value by the last step, or why the axis cannot be extended."""
    ax = axes(model)
    n_ext = {k: sum(k in rnd.get(model, {}) for rnd in EXTENSIONS) for k in ax}
    hits = set()
    for variant in ("own", "lambda"):
        for Y, row in selection[variant].items():
            for k, v in parse_id(row["config"]).items():
                vals = ax[k]
                if len(vals) < 2 or v not in (vals[0], vals[-1]) or (model, k, v) in NATURAL_EDGES:
                    continue
                side = "min" if v == vals[0] else "max"
                nxt = round(2 * vals[0] - vals[1], 6) if side == "min" else round(2 * vals[-1] - vals[-2], 6)
                if nxt <= 0:
                    note = "stuck (next value <= 0)"
                elif n_ext[k] >= MAX_EXTENSIONS:
                    note = "stuck (3 extensions used)"
                else:
                    note = f"extend to {nxt}"
                hits.add(f"{variant}: {k}={v} ({side}) -> {note}")
    return sorted(hits)
