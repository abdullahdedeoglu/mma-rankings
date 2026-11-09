"""Data the redesigned site needs: per-fight rating changes, fighter pages, flags."""

import sqlite3

import pytest

from mmarank import countries, engine, methods
from mmarank.data import Bout
from mmarank.export import fighter_pages, lists_for_month


def _b(fid, date, a, b, method="Submission (Armbar)", draw=False, rated=True):
    bout = Bout(fid, fid, date, "UFC", None, False, methods.classify(method), a, b, draw, True, method)
    bout.rated = rated
    return bout


class _DS:
    def __init__(self, bouts):
        self.bouts = bouts
        self.sex = {}


def test_fight_log_matches_rating_changes():
    bouts = [_b(1, "2020-01-01", 1, 2), _b(2, "2020-03-01", 3, 1, "KO"),
             _b(3, "2020-05-01", 1, 4, "No Contest", rated=False)]
    log: dict = {}
    res = engine.run(_DS(bouts), snapshots=False, fight_log=log)
    plain = engine.run(_DS(bouts), snapshots=False)
    assert res.states[1].mu == pytest.approx(plain.states[1].mu)  # logging changes nothing
    first, second, nc = log[1]
    assert first[:5] == ["2020-01-01", 1, 2, "W", "SUB"] and first[5] > 0
    assert second[:5] == ["2020-03-01", 2, 3, "L", "KO_TKO"] and second[5] < 0
    assert nc[3] == "NC" and nc[5] is None and nc[6] == "UFC"
    assert log[2][0][3] == "L"


def test_same_day_bouts_put_the_change_on_the_last_one():
    bouts = [_b(1, "2000-01-01", 1, 2), _b(2, "2000-01-01", 1, 3)]
    log: dict = {}
    engine.run(_DS(bouts), snapshots=False, fight_log=log)
    assert log[1][0][5] is None and log[1][1][5] > 0


def test_fighter_pages_history_and_fights():
    class Res:
        snapshots = {"2020-01": [{"id": 1, "mu": 1600.4, "rd": 80.2, "score": 1440.0}],
                     "2020-02": [{"id": 1, "mu": 1610.0, "rd": 82.0, "score": 1446.0}, {"id": 9, "mu": 1, "rd": 1, "score": 1}]}
    log = {1: [["2020-01-15", 5, 2, "W", "KO_TKO", 12.34, "UFC"]]}
    pages = fighter_pages(Res(), {1: "A", 2: "B"}, {1: "br"}, log, {1})
    assert set(pages) == {1}
    assert pages[1]["hist"] == [["2020-01", 1600, 80, 1440], ["2020-02", 1610, 82, 1446]]
    assert pages[1]["fights"] == [["2020-01-15", 2, "B", "W", "KO_TKO", 12.3, "UFC"]]
    assert pages[1]["nat"] == "br"


def test_lists_carry_country_codes():
    rows = [{"id": i, "sex": "M", "div": "LW", "score": 2000 - i, "mu": 2100, "rd": 50, "w": 1, "l": 0, "d": 0,
             "last": "2026-01-01", "div_src": "past", "orgs": []} for i in range(3)]
    out = lists_for_month(rows, {0: "A", 1: "B", 2: "C"}, nat={0: "us", 2: "gb-eng"})
    lw = out["global"]["LW"]
    assert [r.get("nat") for r in lw] == ["us", None, "gb-eng"]


def test_country_names_and_wikidata_fallback(tmp_path):
    assert countries.from_text("United States") == "us"
    assert countries.from_text(" england ") == "gb-eng"
    assert countries.from_text("Dagestan") == "ru"
    assert countries.from_text("N/A") is None and countries.from_text(None) is None
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE fighters (fighter_id INTEGER, nationality TEXT)")
    db.execute("CREATE TABLE fighter_aliases (fighter_id INTEGER, source TEXT, source_id TEXT)")
    db.executemany("INSERT INTO fighters VALUES (?, ?)", [(1, "Brazil"), (2, None), (3, "uni")])
    db.executemany("INSERT INTO fighter_aliases VALUES (?, 'sherdog', ?)", [(1, "a-1"), (2, "b-22"), (3, "c-33")])
    csv = tmp_path / "c.csv"
    csv.write_text("sherdog,country\n1,US\n22,AM\n")
    got = countries.load(db, csv, tmp_path / "none.csv")
    assert got == {1: "br", 2: "am"}  # Fight Canon first, Wikidata only where it has nothing
    manual = tmp_path / "m.csv"
    manual.write_text("sherdog,nationality,name,checked\n22,Russia,B,2026-11-09\n33,Georgia,C,2026-11-09\n")
    got = countries.load(db, csv, manual)
    assert got == {1: "br", 2: "ru", 3: "ge"}  # the hand-read Sherdog field comes before Wikidata
