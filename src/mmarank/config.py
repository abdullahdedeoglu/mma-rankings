"""Paths and model parameters. Every number that shapes a ranking lives here.

Changing any value in MODEL changes ALGO_VERSION's parameter hash, so published
snapshots always say exactly which settings produced them.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"  # one folder per Fight Canon release tag (gitignored)
EXTERNAL_DIR = DATA_DIR / "external"  # small committed side data (Wikidata)
MAPPINGS_DIR = Path(__file__).resolve().parent / "mappings"
BUILD_DIR = ROOT / "build"
SITE_SRC = ROOT / "site"

FIGHT_CANON_REPO = "Jadevit/fight-canon-db"
ALGO_NAME = "glicko1-mov"


@dataclass(frozen=True)
class ModelParams:
    # Glicko-1
    initial_rating: float = 1500.0
    initial_rd: float = 350.0
    min_rd: float = 30.0
    # RD growth per 30 days of inactivity: RD_t = sqrt(RD^2 + c^2 * months)
    c: float = 35.0
    # Outcome value for the WINNER by method class (loser gets 1 - value)
    outcome: dict = field(
        default_factory=lambda: {
            "KO_TKO": 1.0,
            "SUB": 1.0,
            "DEC_UNAN": 0.9,
            "DEC_UNSPEC": 0.8,
            "DEC_TECH": 0.8,
            "DEC_MAJ": 0.6,
            "DEC_SPLIT": 0.55,
            "OTHER": 0.9,  # e.g. 'Could Not Continue'
        }
    )
    # Ranking score = mu - display_k * RD - inactivity penalty.
    # The penalty is a RANKING choice, not part of the prediction model: after
    # `inactivity_grace_months` without a bout (NC/DQ count as bouts here), the
    # score drops `inactivity_penalty` points per further month.
    display_k: float = 2.0
    inactivity_grace_months: float = 12.0
    inactivity_penalty: float = 20.0
    # Debut prior (empirical Bayes, leak-free): a fighter's first rating is the mean
    # rating of established fighters (>= 3 bouts) who fought in the same promotion
    # in the previous `promo_window_months`, shrunk towards `initial_rating` with
    # weight `promo_prior_k`, minus `debut_offset`.
    promo_prior: bool = True
    promo_prior_k: float = 10.0
    promo_window_months: int = 24
    debut_offset: float = 100.0  # newcomers start below a promotion's established fighters


@dataclass(frozen=True)
class RankingRules:
    first_published_month: str = "1997-01"
    min_fights: int = 3
    active_months: int = 24  # must have fought within this window
    org_window_months: int = 18  # org list membership window
    division_lookback_years: int = 3
    division_last_n: int = 3
    list_size: int = 15
    dedup_window_days: int = 30
    # P4P index = W * P(beat own division's #ref) + (1 - W) * P(beat the median division's #ref).
    # W = 1: pure within-division dominance (rewards champions of shallow divisions).
    # W < 1: partly trusts the global scale (penalises shallow divisions, although
    # scores across divisions are only weakly comparable). A judgement call, not a fact.
    p4p_ref_rank: int = 5
    p4p_min_depth: int = 10  # a division needs this many ranked fighters to take part
    p4p_within_weight: float = 1.0


MODEL = ModelParams()
RULES = RankingRules()

# Canonical divisions (upper limit in lbs). Men's lists only in the MVP.
MEN_DIVISIONS = {
    "HW": 265,
    "LHW": 205,
    "MW": 185,
    "WW": 170,
    "LW": 155,
    "FW": 145,
    "BW": 135,
    "FLW": 125,
}
WOMEN_DIVISIONS = {"W-FW": 145, "W-BW": 135, "W-FLW": 125, "W-SW": 115, "W-ATW": 105}
DIVISION_NAMES = {
    "HW": "Heavyweight",
    "LHW": "Light Heavyweight",
    "MW": "Middleweight",
    "WW": "Welterweight",
    "LW": "Lightweight",
    "FW": "Featherweight",
    "BW": "Bantamweight",
    "FLW": "Flyweight",
    "W-FW": "Women's Featherweight",
    "W-BW": "Women's Bantamweight",
    "W-FLW": "Women's Flyweight",
    "W-SW": "Women's Strawweight",
    "W-ATW": "Women's Atomweight",
}

# The "Big 9" promotions that get their own filtered lists.
# key -> (display name, Fight Canon promotion labels)
ORGS = {
    "UFC": ("UFC", ["UFC"]),
    "PRIDE": ("PRIDE", ["PRIDE"]),
    "WEC": ("WEC", ["WEC"]),
    "SF": ("Strikeforce", ["Strikeforce"]),
    "BELLATOR": ("Bellator", ["Bellator MMA", "Bellator"]),
    "PFL": ("PFL", ["Professional Fighters League"]),
    "ONE": ("ONE", ["ONE FC"]),
    "RIZIN": ("RIZIN", ["Rizin Fighting Federation"]),
    "DREAM": ("DREAM", ["DREAM"]),
}


def params_hash(model: ModelParams = MODEL, rules: RankingRules = RULES) -> str:
    blob = json.dumps({"model": asdict(model), "rules": asdict(rules)}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:10]
