"""Turn monthly snapshots into ranking lists and static JSON for the site."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import ALGO_NAME, DIVISION_NAMES, MEN_DIVISIONS, MODEL, ORGS, RULES, SITE_SRC, params_hash
from .data import Dataset
from .engine import RunResult


def lists_for_month(rows: list[dict], names: dict[int, str], size: int = RULES.list_size) -> dict:
    men = [r for r in rows if r["sex"] != "F" and r["div"] in MEN_DIVISIONS]
    men.sort(key=lambda r: -r["score"])

    def fmt(sel: list[dict]) -> list[dict]:
        return [{
            "rank": i + 1, "id": r["id"], "name": names.get(r["id"], "?"),
            "score": round(r["score"]), "mu": round(r["mu"]), "rd": round(r["rd"]),
            "record": f"{r['w']}-{r['l']}-{r['d']}", "last": r["last"],
            "div_src": r["div_src"], "orgs": r["orgs"],
        } for i, r in enumerate(sel[:size])]

    out = {"global": {}, "orgs": {}}
    for div in MEN_DIVISIONS:
        out["global"][div] = fmt([r for r in men if r["div"] == div])
    for org in ORGS:
        per = {}
        for div in MEN_DIVISIONS:
            sel = [r for r in men if r["div"] == div and org in r["orgs"]]
            if sel:
                per[div] = fmt(sel)
        if per:
            out["orgs"][org] = per
    return out


def write_site(ds: Dataset, res: RunResult, release: str, backtest_report: dict, out_dir: Path) -> dict:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(SITE_SRC, out_dir)
    data_dir = out_dir / "data" / "months"
    data_dir.mkdir(parents=True)
    months = sorted(res.snapshots)
    org_months: dict[str, list[str]] = {o: [] for o in ORGS}
    for ym in months:
        lists = lists_for_month(res.snapshots[ym], ds.names)
        for o in lists["orgs"]:
            org_months[o].append(ym)
        (data_dir / f"{ym}.json").write_text(json.dumps({"month": ym, **lists}, separators=(",", ":")))
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_release": release,
        "data_through": res.last_date,
        "algorithm": ALGO_NAME,
        "params_hash": params_hash(),
        "params": {"model": asdict(MODEL), "rules": asdict(RULES)},
        "months": months,
        "divisions": {d: DIVISION_NAMES[d] for d in MEN_DIVISIONS},
        "orgs": {k: {"name": v[0], "first": org_months[k][0] if org_months[k] else None,
                     "last": org_months[k][-1] if org_months[k] else None} for k, v in ORGS.items()},
        "data_report": ds.report,
        "backtest": backtest_report,
    }
    (out_dir / "data" / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta
