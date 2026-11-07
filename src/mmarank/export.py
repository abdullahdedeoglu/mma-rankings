"""Turn monthly snapshots into ranking lists and static JSON for the site."""

from __future__ import annotations

import json
import shutil
import statistics
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .config import ALGO_NAME, DIVISION_NAMES, MEN_DIVISIONS, MODEL, ORGS, RULES, SITE_SRC, params_hash
from .data import Dataset
from .engine import RunResult


P4P_REF_RANK = RULES.p4p_ref_rank
P4P_MIN_DEPTH = RULES.p4p_min_depth
P4P_WITHIN_WEIGHT = RULES.p4p_within_weight  # see RankingRules for the meaning


def p4p_index(score: float, ref_score: float) -> float:
    """Probability (Elo/Glicko logistic scale) of beating the division's reference fighter."""
    return 1.0 / (1.0 + 10.0 ** (-(score - ref_score) / 400.0))


def lists_for_month(rows: list[dict], names: dict[int, str], size: int = RULES.list_size,
                    nat: dict[int, str] | None = None) -> dict:
    men = [r for r in rows if r["sex"] != "F" and r["div"] in MEN_DIVISIONS]
    men.sort(key=lambda r: -r["score"])

    def fmt(sel: list[dict]) -> list[dict]:
        out = []
        for i, r in enumerate(sel[:size]):
            record = f"{r['w']}-{r['l']}-{r['d']}" + (f" ({r['u']} NC/DQ)" if r.get("u") else "")
            row = {
                "rank": i + 1, "id": r["id"], "name": names.get(r["id"], "?"),
                "score": round(r["score"]), "mu": round(r["mu"]), "rd": round(r["rd"]),
                "penalty": round(r.get("penalty", 0)), "record": record, "last": r["last"],
                "div_src": r["div_src"], "orgs": r["orgs"], "div": r["div"],
            }
            if nat and r["id"] in nat:
                row["nat"] = nat[r["id"]]
            if "p4p" in r:
                row["p4p"] = round(r["p4p"], 3)
            out.append(row)
        return out

    def scope(pool: list[dict]) -> dict:
        per, p4p, refs = {}, [], {}
        for div in MEN_DIVISIONS:
            sel = [r for r in pool if r["div"] == div]
            if sel:
                per[div] = fmt(sel)
            if len(sel) >= P4P_MIN_DEPTH:
                refs[div] = sel[P4P_REF_RANK - 1]["score"]
        if refs:
            med = statistics.median(refs.values())
            w = P4P_WITHIN_WEIGHT
            for div, ref in refs.items():
                sel = [r for r in pool if r["div"] == div][:size]
                p4p += [{**r, "p4p": w * p4p_index(r["score"], ref) + (1 - w) * p4p_index(r["score"], med)}
                        for r in sel]
        if p4p:
            p4p.sort(key=lambda r: -r["p4p"])
            per["P4P"] = fmt(p4p)
        return per

    out = {"global": scope(men), "orgs": {}}
    for org in ORGS:
        per = scope([r for r in men if org in r["orgs"]])
        if per:
            out["orgs"][org] = per
    return out


def fighter_pages(res: RunResult, names: dict[int, str], nat: dict[int, str], fight_log: dict,
                  ids: set[int]) -> dict[int, dict]:
    """Per-fighter data for the site: monthly rating history (months the fighter was
    eligible for a list) and every bout with the rating change it caused."""
    pages = {f: {"id": f, "name": names.get(f, "?"), "nat": nat.get(f), "hist": [], "fights": []} for f in ids}
    for ym in sorted(res.snapshots):
        for r in res.snapshots[ym]:
            if r["id"] in pages:
                pages[r["id"]]["hist"].append([ym, round(r["mu"]), round(r["rd"]), round(r["score"])])
    for f, page in pages.items():
        page["fights"] = [[d, opp, names.get(opp, "?"), result, method, None if dmu is None else round(dmu, 1), promo]
                          for d, _, opp, result, method, dmu, promo in fight_log.get(f, [])]
    return pages


def write_site(ds: Dataset, res: RunResult, release: str, backtest_report: dict, out_dir: Path,
               nat: dict[int, str] | None = None, fight_log: dict | None = None) -> dict:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(SITE_SRC, out_dir)
    data_dir = out_dir / "data" / "months"
    data_dir.mkdir(parents=True)
    months = sorted(res.snapshots)
    org_months: dict[str, list[str]] = {o: [] for o in ORGS}
    listed: set[int] = set()
    for ym in months:
        lists = lists_for_month(res.snapshots[ym], ds.names, nat=nat)
        for scope in (lists["global"], *lists["orgs"].values()):
            for rows in scope.values():
                listed.update(r["id"] for r in rows)
        for o in lists["orgs"]:
            org_months[o].append(ym)
        (data_dir / f"{ym}.json").write_text(json.dumps({"month": ym, **lists}, separators=(",", ":")))
    if fight_log is not None:
        fdir = out_dir / "data" / "fighters"
        fdir.mkdir()
        pages = fighter_pages(res, ds.names, nat or {}, fight_log, listed)
        for f, page in pages.items():
            (fdir / f"{f}.json").write_text(json.dumps(page, separators=(",", ":"), ensure_ascii=False))
        index = sorted(([f, p["name"], p["nat"], p["hist"][-1][0] if p["hist"] else None] for f, p in pages.items()),
                       key=lambda x: x[1])
        (fdir / "index.json").write_text(json.dumps(index, separators=(",", ":"), ensure_ascii=False))
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_release": release,
        "data_through": res.last_date,
        "algorithm": ALGO_NAME,
        "params_hash": params_hash(),
        "params": {"model": asdict(MODEL), "rules": asdict(RULES)},
        "months": months,
        "divisions": {"P4P": "P4P", **{d: DIVISION_NAMES[d] for d in MEN_DIVISIONS}},
        "p4p": {"reference_rank": P4P_REF_RANK, "min_division_depth": P4P_MIN_DEPTH,
                "within_weight": P4P_WITHIN_WEIGHT},
        "orgs": {k: {"name": v[0], "first": org_months[k][0] if org_months[k] else None,
                     "last": org_months[k][-1] if org_months[k] else None} for k, v in ORGS.items()},
        "data_report": ds.report,
        "backtest": backtest_report,
    }
    (out_dir / "data" / "meta.json").write_text(json.dumps(meta, indent=1))
    return meta
