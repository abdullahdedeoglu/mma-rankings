"""Normalise free-text finish methods ('TKO (Punches)', 'Decision - Unanimous', ...)."""

from __future__ import annotations

# Classes that are excluded from rating updates.
EXCLUDED = {"NC", "DQ", "MISSING", "NA"}


def classify(method: str | None) -> str:
    if method is None or not method.strip():
        return "MISSING"
    s = method.strip().lower()
    if s in {"n/a", "na", "other", "overturned"} or "overturned" in s:
        return "NA"
    if "no contest" in s or s.startswith("nc"):
        return "NC"
    if "dq" in s or "disqualif" in s:
        return "DQ"
    if "draw" in s or s.startswith("drew"):
        return "DRAW"
    if "decision" in s or s.startswith("dec") or s.startswith("points"):
        if "split" in s:
            return "DEC_SPLIT"
        if "majority" in s:
            return "DEC_MAJ"
        if "unanim" in s:
            return "DEC_UNAN"
        if "technical" in s:
            return "DEC_TECH"
        return "DEC_UNSPEC"
    if "submission" in s or s.startswith("sub") or "tapout" in s or "choke" in s or "armbar" in s:
        return "SUB"
    if "ko" in s or "k.o" in s or "stoppage" in s or "retire" in s or "punch" in s:
        return "KO_TKO"
    return "OTHER"
