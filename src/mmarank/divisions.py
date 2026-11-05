"""Turn a bout's free-text weight class into a canonical division.

Two steps:
1. parse_label(): label text -> a sex-neutral key such as 'MIDDLE' (or None for
   open weight, catchweight, tournaments without a division, ...).
2. apply overrides for promotions/eras whose names meant other limits
   (PRIDE, DREAM, pre-2001 UFC, ...), from mappings/weight_class_overrides.csv.
3. to_division(): key + fighter sex -> canonical division code ('LHW', 'W-BW').

Rule of thumb: when unsure, return None. An unassigned bout still counts for
ratings; it just doesn't place the fighter in a division.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from functools import lru_cache

from .config import MAPPINGS_DIR, MEN_DIVISIONS, WOMEN_DIVISIONS

# Order matters: longer names first.
_NAMES = [
    ("super heavyweight", "SUPERHEAVY"),
    ("light heavyweight", "LIGHTHEAVY"),
    ("heavyweight", "HEAVY"),
    ("middleweight", "MIDDLE"),
    ("welterweight", "WELTER"),
    ("lightweight", "LIGHT"),
    ("featherweight", "FEATHER"),
    ("bantamweight", "BANTAM"),
    ("flyweight", "FLY"),
    ("strawweight", "STRAW"),
    ("atomweight", "ATOM"),
]
_LIMITS = {  # used for numeric labels like "Women's 135 lbs."
    "HEAVY": 265, "LIGHTHEAVY": 205, "MIDDLE": 185, "WELTER": 170, "LIGHT": 155,
    "FEATHER": 145, "BANTAM": 135, "FLY": 125, "STRAW": 115, "ATOM": 105,
}
_NUM = re.compile(r"(\d{2,3}(?:\.\d)?)\s*(lbs?|kg)\b")
_MEN = {
    "SUPERHEAVY": "HW", "HEAVY": "HW", "LIGHTHEAVY": "LHW", "MIDDLE": "MW",
    "WELTER": "WW", "LIGHT": "LW", "FEATHER": "FW", "BANTAM": "BW", "FLY": "FLW",
}
_WOMEN = {"FEATHER": "W-FW", "BANTAM": "W-BW", "FLY": "W-FLW", "STRAW": "W-SW", "ATOM": "W-ATW"}

assert set(_MEN.values()) == set(MEN_DIVISIONS)
assert set(_WOMEN.values()) == set(WOMEN_DIVISIONS)


@dataclass(frozen=True)
class Parsed:
    key: str | None  # e.g. 'MIDDLE'
    women: bool  # label itself says women's
    title: bool


def parse_label(label: str | None) -> Parsed:
    if not label or not label.strip():
        return Parsed(None, False, False)
    s = label.lower()
    women = "women" in s
    title = "title" in s or "championship" in s
    if "catch" in s or "open weight" in s or "openweight" in s or "pound for pound" in s:
        return Parsed(None, women, title)
    for name, key in _NAMES:
        if name in s:
            return Parsed(key, women, title)
    m = _NUM.search(s)
    if m:
        lbs = float(m.group(1)) * (2.20462 if m.group(2) == "kg" else 1.0)
        key = min(_LIMITS, key=lambda k: abs(_LIMITS[k] - lbs))
        return Parsed(key, women, title)
    return Parsed(None, women, title)


@dataclass(frozen=True)
class Override:
    promotion: str
    date_from: str
    date_to: str
    parsed: str
    maps_to: str
    scope: str


@lru_cache(maxsize=1)
def load_overrides() -> tuple[Override, ...]:
    with open(MAPPINGS_DIR / "weight_class_overrides.csv", newline="") as fh:
        return tuple(
            Override(r["promotion"], r["date_from"], r["date_to"], r["parsed"], r["maps_to"], r["scope"])
            for r in csv.DictReader(fh)
        )


def label_key(label: str | None, promotion: str, date: str) -> tuple[str | None, bool]:
    """Sex-neutral division key for one bout, after overrides. Returns (key, women_label)."""
    p = parse_label(label)
    if p.key is None:
        return None, p.women
    key = p.key
    for o in load_overrides():
        if o.promotion != promotion:
            continue
        if o.date_from and date < o.date_from:
            continue
        if o.date_to and date >= o.date_to:
            continue
        if o.parsed not in ("*", p.key):
            continue
        if o.scope == "non_title" and p.title:
            continue
        if o.maps_to == "IGNORE":
            return None, p.women
        key = o.maps_to
        break
    return key, p.women


def to_division(key: str | None, sex: str | None) -> str | None:
    if key is None:
        return None
    if sex == "F":
        return _WOMEN.get(key)
    return _MEN.get(key)
