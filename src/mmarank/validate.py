"""Fail-closed checks. If any fails, the build stops and the last good site stays up."""

from __future__ import annotations

import math
from datetime import date, timedelta

from .data import Dataset
from .engine import RunResult


class ValidationError(RuntimeError):
    pass


def check(ds: Dataset, res: RunResult, today: date | None = None) -> list[str]:
    today = today or date.today()
    problems = []
    if len(ds.bouts) < 300_000:
        problems.append(f"only {len(ds.bouts)} bouts after cleaning (expected > 300k)")
    if ds.report.get("near_duplicates_removed", 0) > 2_000:
        problems.append("suspiciously many near-duplicates removed")
    if ds.report["sex"]["conflict_edges"] > 50:
        problems.append(f"{ds.report['sex']['conflict_edges']} male/female conflicts (expected a handful)")
    if date.fromisoformat(res.last_date) < today - timedelta(days=45):
        problems.append(f"latest bout {res.last_date} is more than 45 days old")
    for f, s in res.states.items():
        if not (math.isfinite(s.mu) and math.isfinite(s.rd)):
            problems.append(f"non-finite rating for fighter {f}")
            break
    last = res.snapshots[max(res.snapshots)]
    if sum(1 for r in last if r["div"]) < 1000:
        problems.append("fewer than 1000 rankable fighters in the latest month")
    return problems
