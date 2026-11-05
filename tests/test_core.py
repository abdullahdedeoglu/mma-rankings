import math

import pytest

from mmarank import glicko, methods
from mmarank.data import Bout, drop_near_duplicates
from mmarank.divisions import label_key, parse_label, to_division
from mmarank.engine import _Timeline
from mmarank.config import RULES


# ---------- Glicko-1: worked example from Glickman (1999), glicko.pdf
def test_glicko_paper_example():
    mu, rd = glicko.update(1500, 200, [(1400, 30, 1), (1550, 100, 0), (1700, 300, 0)])
    assert mu == pytest.approx(1464, abs=1)
    assert rd == pytest.approx(151.4, abs=0.5)


def test_glicko_inflation_caps_at_max():
    assert glicko.inflate(50, 0, 35, 350) == 50
    assert glicko.inflate(50, 1000, 35, 350) == 350
    assert glicko.inflate(50, 1, 35, 350) == pytest.approx(math.sqrt(50**2 + 35**2))


def test_win_probability_symmetric():
    p = glicko.win_probability(1600, 80, 1500, 120)
    q = glicko.win_probability(1500, 120, 1600, 80)
    assert p + q == pytest.approx(1.0)
    assert p > 0.5


# ---------- method classification
@pytest.mark.parametrize("raw,cls", [
    ("TKO (Punches)", "KO_TKO"), ("KO/TKO", "KO_TKO"), ("K.O (Punch)", "KO_TKO"),
    ("Submission (Rear-Naked Choke)", "SUB"), ("Decision (Split)", "DEC_SPLIT"),
    ("Decision - Unanimous", "DEC_UNAN"), ("Decision (Majority)", "DEC_MAJ"),
    ("Decision", "DEC_UNSPEC"), ("Draw", "DRAW"), ("DQ", "DQ"),
    ("No Contest", "NC"), ("N/A", "NA"), (None, "MISSING"), ("Overturned", "NA"),
])
def test_classify(raw, cls):
    assert methods.classify(raw) == cls


# ---------- weight classes
def test_parse_basic_and_women():
    assert parse_label("Light Heavyweight Bout").key == "LIGHTHEAVY"
    assert parse_label("Heavyweight").key == "HEAVY"
    p = parse_label("Strikeforce Women's 135 lbs. Title Bout")
    assert p.key == "BANTAM" and p.women and p.title
    assert parse_label("150lb Catchweight").key is None
    assert parse_label("Open Weight Bout").key is None
    assert parse_label("UFC 1 Tournament Title Bout").key is None


def test_pride_and_pre2001_ufc_overrides():
    assert label_key("Middleweight Bout", "PRIDE", "2005-08-28")[0] == "LIGHTHEAVY"
    assert label_key("Welterweight Bout", "PRIDE", "2006-05-05")[0] == "MIDDLE"
    # UFC 16-30 'Lightweight' meant up to 170 lb
    assert label_key("Lightweight Bout", "UFC", "1999-05-07")[0] == "WELTER"
    # ... but retro-fitted title labels keep their modern meaning
    assert label_key("UFC Light Heavyweight Title Bout", "UFC", "1999-05-07")[0] == "LIGHTHEAVY"
    assert label_key("Middleweight Bout", "UFC", "2010-01-01")[0] == "MIDDLE"
    assert label_key("Featherweight Bout", "DREAM", "2010-05-29")[0] == "BANTAM"
    assert label_key("Welterweight", "Pancrase", "2005-01-01")[0] is None


def test_to_division_by_sex():
    assert to_division("BANTAM", "M") == "BW"
    assert to_division("BANTAM", "F") == "W-BW"
    assert to_division("STRAW", "M") is None
    assert to_division("HEAVY", None) == "HW"


# ---------- near-duplicates
def _b(fid, eid, date, a, b, method="Submission (Armbar)", complete=True, draw=False):
    return Bout(fid, eid, date, "X", None, False, methods.classify(method), a, b, draw, complete, method)


def test_near_duplicate_keeps_detailed_record():
    bouts = [_b(1, 10, "1998-03-05", 7, 8, "Submission", complete=False),
             _b(2, 11, "1998-03-15", 7, 8, "Submission (Armbar)")]
    kept, log = drop_near_duplicates(bouts, {})
    assert [b.fight_id for b in kept] == [2]
    assert log[0]["dropped"] == 1


def test_rematch_with_different_winner_is_kept():
    bouts = [_b(1, 10, "2005-01-01", 7, 8), _b(2, 11, "2005-01-20", 8, 7)]
    kept, _ = drop_near_duplicates(bouts, {})
    assert len(kept) == 2


# ---------- division at time T never prefers future labels over past ones
class _DS:
    def __init__(self, bouts):
        self.bouts = bouts


def test_division_uses_past_then_future():
    b1 = _b(1, 1, "2004-01-01", 7, 8); b1.div_key = "LIGHT"
    b2 = _b(2, 2, "2008-01-01", 7, 9); b2.div_key = "WELTER"
    tl = _Timeline(_DS([b1, b2]))
    assert tl.division_key(7, "2005-06-30", RULES) == ("LIGHT", "past")
    assert tl.division_key(7, "2003-06-30", RULES) == ("LIGHT", "future")
    assert tl.division_key(7, "2010-06-30", RULES) == ("WELTER", "past")
    assert tl.division_key(7, "2020-06-30", RULES) == ("WELTER", "old")
