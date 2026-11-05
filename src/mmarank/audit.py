"""Data audit (research phase 1). Descriptive only: no ratings, no predictions.

    uv run python -m mmarank.audit [--db PATH] [--out DIR]

Writes audit.json (all counts) and CSV listings for manual review into
build/audit/<release tag>/. docs/AUDIT.md reports and interprets the numbers.
The rated-bout set comes from data.load(), the same function the ratings use.
"""

from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import random
import re
import sqlite3
import unicodedata
from datetime import date as Date
from pathlib import Path

from . import data, divisions, methods
from .config import BUILD_DIR, RAW_DIR

SEED = 20261105
ADJ = ["FLW", "BW", "FW", "LW", "WW", "MW", "LHW", "HW"]  # men's divisions, light to heavy


def era(d: str) -> str:
    y = int(d[:4])
    return "<2000" if y < 2000 else "2000-09" if y < 2010 else "2010-19" if y < 2020 else "2020+"


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z ]", "", re.sub(r"[-.']", " ", s)).split())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_csv(path: Path, header: list[str], rows) -> int:
    n = 0
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            w.writerow(r)
            n += 1
    return n


# ---------------------------------------------------------------- raw tables
def raw_integrity(db: sqlite3.Connection, last_event: str) -> dict:
    q = lambda sql: db.execute(sql).fetchall()  # noqa: E731
    out: dict = {}
    out["tables"] = {t: q(f"SELECT count(*) FROM {t}")[0][0]
                     for t in ("fighters", "events", "fights", "fight_participants", "odds",
                               "judge_scores", "round_stats", "merged_ids")}
    out["participants_per_fight"] = dict(q(
        "SELECT n, count(*) FROM (SELECT f.fight_id, count(p.fighter_id) n FROM fights f "
        "LEFT JOIN fight_participants p USING(fight_id) GROUP BY 1) GROUP BY n"))
    out["result_pairs"] = {f"{a}/{b}": n for a, b, n in q(
        "SELECT min(p0.result,p1.result), max(p0.result,p1.result), count(*) FROM fight_participants p0 "
        "JOIN fight_participants p1 ON p0.fight_id=p1.fight_id AND p0.corner=0 AND p1.corner=1 GROUP BY 1,2")}
    out["bout_type"] = {str(k): n for k, n in q("SELECT bout_type, count(*) FROM fights GROUP BY 1")}
    out["events_without_date"] = q("SELECT count(*) FROM events WHERE date IS NULL OR date=''")[0][0]
    out["events_after_last_event"] = q(f"SELECT count(*) FROM events WHERE date > '{last_event}'")[0][0]
    out["events_before_1990"] = q("SELECT count(*) FROM events WHERE date < '1990-01-01'")[0][0]
    out["events_per_era"] = dict(collections.Counter(era(d) for (d,) in q(
        "SELECT date FROM events WHERE date IS NOT NULL AND date<>''")))
    # same promotion, same date, more than one event id: possible duplicate events
    out["same_promotion_same_date_event_groups"] = q(
        "SELECT count(*) FROM (SELECT promotion, date FROM events WHERE date IS NOT NULL "
        "GROUP BY 1,2 HAVING count(*)>1)")[0][0]
    out["fighters_without_bouts"] = q(
        "SELECT count(*) FROM fighters WHERE fighter_id NOT IN (SELECT fighter_id FROM fight_participants)")[0][0]
    return out


# ---------------------------------------------------------------- methods
def method_audit(db: sqlite3.Connection, outdir: Path) -> dict:
    rows = db.execute("SELECT method, count(*) FROM fights GROUP BY 1").fetchall()
    by_class: dict[str, list] = collections.defaultdict(list)
    for m, n in rows:
        by_class[methods.classify(m)].append((m, n))
    # suspicious: the class contradicts another finish word in the same string
    sus = []
    for m, n in rows:
        c, s = methods.classify(m), (m or "").lower()
        flag = None
        if c == "SUB" and re.search(r"\bt?ko\b|\bpunch|\bstrike|\belbow|\bkick", s):
            flag = "SUB_but_strikes"
        elif c == "KO_TKO" and "submission" in s:
            flag = "KO_but_submission"
        elif c.startswith("DEC") and re.search(r"\bt?ko\b|submission", s):
            flag = "DEC_but_finish"
        elif c == "OTHER":
            flag = "OTHER"
        if flag:
            sus.append((flag, m, n))
    sus.sort(key=lambda r: (r[0], -r[2]))
    write_csv(outdir / "method_suspicious.csv", ["flag", "method", "fights"], sus)
    write_csv(outdir / "method_classes.csv", ["class", "method", "fights"],
              ((c, m, n) for c in sorted(by_class) for m, n in sorted(by_class[c], key=lambda r: -r[1])))
    flags = collections.Counter()
    for f, _, n in sus:
        flags[f] += n
    return {"distinct_method_strings": len(rows),
            "fights_per_class": {c: sum(n for _, n in v) for c, v in sorted(by_class.items())},
            "suspicious_fights_by_flag": dict(flags),
            "top_suspicious": [{"flag": f, "method": m, "fights": n} for f, m, n in sus[:25]]}


# ---------------------------------------------------------------- rated bouts
def bout_audit(ds: data.Dataset, outdir: Path) -> dict:
    rated = [b for b in ds.bouts if getattr(b, "rated", True)]
    out: dict = {"load_report": {k: v for k, v in ds.report.items() if k != "sex"},
                 "sex_report": ds.report.get("sex")}
    out["rated_bouts"] = len(rated)
    out["rated_per_era"] = dict(collections.Counter(era(b.date) for b in rated))
    cls_era = collections.defaultdict(collections.Counter)
    for b in rated:
        cls_era[era(b.date)][b.method_class] += 1
    out["method_class_by_era"] = {e: dict(c) for e, c in sorted(cls_era.items())}
    sexes = collections.Counter((ds.sex.get(b.a, "?"), ds.sex.get(b.b, "?")) for b in rated)
    out["sex_pairs"] = {f"{a}{b}": n for (a, b), n in sexes.items()}

    # same fighter, more than one rated bout on the same date (tournaments or duplicates)
    day = collections.Counter()
    for b in rated:
        day[(b.a, b.date)] += 1
        day[(b.b, b.date)] += 1
    multi = [(f, d, n) for (f, d), n in day.items() if n > 1]
    out["fighter_days_with_multiple_bouts"] = len(multi)
    out["fighter_days_with_multiple_bouts_by_era"] = dict(collections.Counter(era(d) for _, d, _ in multi))
    out["max_bouts_one_day"] = max((n for *_, n in multi), default=0)

    # near-duplicate merges
    gaps = collections.Counter()
    cross = 0
    for r in ds.duplicates:
        g = (Date.fromisoformat(r["dropped_date"]) - Date.fromisoformat(r["kept_date"])).days
        gaps["0" if g == 0 else "1-7" if abs(g) <= 7 else "8-30"] += 1
        cross += r["kept_promotion"] != r["dropped_promotion"]
    out["near_duplicates"] = {"merged": len(ds.duplicates), "gap_days": dict(gaps),
                              "different_promotion": cross}
    write_csv(outdir / "near_duplicates.csv", list(ds.duplicates[0].keys()) if ds.duplicates else ["none"],
              (list(r.values()) for r in ds.duplicates))
    return out


def fighter_audit(db: sqlite3.Connection, ds: data.Dataset, outdir: Path) -> dict:
    rated = [b for b in ds.bouts if getattr(b, "rated", True)]
    first, last, nb = {}, {}, collections.Counter()
    for b in rated:
        for f in (b.a, b.b):
            first.setdefault(f, b.date)
            last[f] = b.date
            nb[f] += 1
    info = {fid: (name, dob) for fid, name, dob in db.execute("SELECT fighter_id, name, dob FROM fighters")}
    out: dict = {"fighters_with_rated_bouts": len(nb)}
    # probable split identities: same normalised name and same known dob
    groups = collections.defaultdict(list)
    for f in nb:
        name, dob = info.get(f, ("", None))
        if dob:
            groups[(norm_name(name), dob)].append(f)
    dup = [(k, v) for k, v in groups.items() if len(v) > 1 and k[0]]
    out["same_name_same_dob_groups"] = len(dup)
    # same normalised name, unknown dob, both active in overlapping windows (ambiguous: namesakes or splits)
    by_name = collections.defaultdict(list)
    for f in nb:
        by_name[norm_name(info.get(f, ("", None))[0])].append(f)
    overlap = 0
    for name, fs in by_name.items():
        if len(fs) < 2 or not name:
            continue
        fs.sort(key=lambda f: first[f])
        for x, y in zip(fs, fs[1:]):
            if first[y] <= last[x]:
                overlap += 1
    out["same_name_overlapping_careers_pairs"] = overlap
    out["names_shared_by_several_ids"] = sum(1 for fs in by_name.values() if len(fs) > 1)
    write_csv(outdir / "identity_same_name_dob.csv", ["name", "dob", "fighter_ids", "bouts", "first", "last"],
              ((k[0], k[1], " ".join(map(str, v)), " ".join(str(nb[f]) for f in v),
                " ".join(first[f] for f in v), " ".join(last[f] for f in v)) for k, v in dup))
    # implausible ages at bout time (dob known)
    ages = collections.Counter()
    odd = []
    for b in rated:
        for f in (b.a, b.b):
            dob = info.get(f, ("", None))[1]
            if not dob or len(dob) < 10:
                continue
            try:
                a = (Date.fromisoformat(b.date) - Date.fromisoformat(dob)).days / 365.25
            except ValueError:
                ages["unparseable_dob"] += 1
                continue
            if a < 16:
                ages["<16"] += 1
                odd.append((f, info[f][0], dob, b.date, round(a, 1)))
            elif a > 55:
                ages[">55"] += 1
                odd.append((f, info[f][0], dob, b.date, round(a, 1)))
    out["implausible_age_bouts"] = dict(ages)
    write_csv(outdir / "implausible_ages.csv", ["fighter_id", "name", "dob", "bout_date", "age"], odd)
    spans = [(Date.fromisoformat(last[f]) - Date.fromisoformat(first[f])).days / 365.25 for f in nb]
    out["career_span_over_25y"] = sum(s > 25 for s in spans)
    out["bouts_per_fighter"] = {k: sum(1 for n in nb.values() if lo <= n <= hi)
                                for k, (lo, hi) in {"1": (1, 1), "2-4": (2, 4), "5-9": (5, 9),
                                                    "10-29": (10, 29), "30+": (30, 10**6)}.items()}
    return out


# ---------------------------------------------------------------- divisions
def division_audit(ds: data.Dataset, outdir: Path, urls: dict[int, str]) -> dict:
    rated = [b for b in ds.bouts if getattr(b, "rated", True)]
    men = [b for b in rated if not b.draw and ds.sex.get(b.a) == "M" and ds.sex.get(b.b) == "M"]
    div = lambda b: divisions.to_division(b.div_key, "M")  # noqa: E731
    out: dict = {"men_decisive_bouts": len(men)}
    tot, known = collections.Counter(), collections.Counter()
    for b in men:
        tot[era(b.date)] += 1
        known[era(b.date)] += div(b) is not None
    out["division_known_share_by_era"] = {e: round(known[e] / tot[e], 3) for e in sorted(tot)}
    unl = collections.Counter(b.weight_class for b in men if div(b) is None)
    out["top_unassigned_labels"] = unl.most_common(25)

    seq = collections.defaultdict(list)
    for b in men:
        d = div(b)
        if d:
            for f in (b.a, b.b):
                seq[f].append(b)
    rank = {d: i for i, d in enumerate(ADJ)}
    steps = collections.Counter()
    far, flips = [], []
    for f, bs in seq.items():
        for x, y in zip(bs, bs[1:]):
            s = abs(rank[div(x)] - rank[div(y)])
            if s:
                steps[s] += 1
            if s >= 3:
                far.append((f, ds.names.get(f, ""), x.date, x.promotion, x.weight_class, div(x),
                            y.date, y.promotion, y.weight_class, div(y), s))
        for x, y, z in zip(bs, bs[1:], bs[2:]):
            if div(x) == div(z) != div(y):
                flips.append((f, ds.names.get(f, ""), y.date, y.promotion, y.weight_class, div(y), div(x),
                              abs(rank[div(x)] - rank[div(y)])))
    # Who were the opponents? An opponent whose own career sits in the labelled division
    # supports the label; if both opponents of a 3+ step move fit their labels, the
    # fighter id probably joins two different people (identity merge).
    modal = {f: collections.Counter(div(b) for b in bs).most_common(1)[0][0] for f, bs in seq.items()}
    
    def label_fits(f: int, b) -> bool | None:
        o = b.b if b.a == f else b.a
        if len(seq.get(o, ())) < 3:  # too few labelled bouts to say where the opponent belongs
            return None
        return abs(rank[modal[o]] - rank[div(b)]) <= 1

    kinds = collections.Counter()
    far2 = []
    for r in far:
        f = r[0]
        bx = next(b for b in seq[f] if b.date == r[2] and div(b) == r[5])
        by = next(b for b in seq[f] if b.date == r[6] and div(b) == r[9])
        fx, fy = label_fits(f, bx), label_fits(f, by)
        if fx is None or fy is None:
            k = "opponent_unknown"
        else:
            k = "both_labels_fit_opponents" if fx and fy else "one_label_misfits" if fx != fy else "neither_fits"
        kinds[k] += 1
        far2.append(r + (k,))
    far = far2
    out["moves_3plus_by_opponent_check"] = dict(kinds)
    out["consecutive_moves_by_size"] = {str(k): v for k, v in sorted(steps.items())}
    out["moves_3plus_divisions"] = len(far)
    out["aba_flips"] = len(flips)
    out["aba_flips_by_size"] = dict(collections.Counter(r[-1] for r in flips))
    out["aba_middle_label_kind"] = dict(collections.Counter(
        "numeric" if divisions._NUM.search((r[4] or "").lower()) else "named" for r in flips))
    write_csv(outdir / "division_moves_3plus.csv",
              ["fighter_id", "name", "date1", "promotion1", "label1", "div1", "date2", "promotion2", "label2", "div2", "steps",
               "opponent_check"], far)
    rng = random.Random(SEED)
    write_csv(outdir / "division_moves_check_sample.csv",
              ["fighter_id", "name", "date1", "promotion1", "label1", "div1", "date2", "promotion2", "label2", "div2", "steps",
               "opponent_check", "sherdog_url", "verdict(label_error/identity_merge/genuine/unknown)", "note"],
              (r + (urls.get(r[0], ""), "", "") for r in rng.sample(far, min(30, len(far)))))
    write_csv(outdir / "division_aba_flips.csv",
              ["fighter_id", "name", "date", "promotion", "label", "div", "surrounding_div", "steps"], flips)
    return out


def sherdog_urls(db: sqlite3.Connection) -> dict[int, str]:
    out = {}
    for f, sid, name in db.execute(
            "SELECT fighter_id, source_id, name FROM fighter_aliases WHERE source='sherdog' ORDER BY fighter_id, source_id"):
        if f not in out:
            slug = "-".join(unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().split())
            out[f] = f"https://www.sherdog.com/fighter/{slug}-{sid}"
    return out


def division_sample(db: sqlite3.Connection, ds: data.Dataset, outdir: Path, n: int = 200) -> dict:
    """Stratified random fighter-months for the manual division check (PROTOCOL §8).

    A fighter-month = a month with at least one rated men's bout that has a division.
    Strata: 2010-14, 2015-19, 2020+ (equal shares); pre-2010 has ~5 % coverage and is
    reported separately, not sampled."""
    sherdog = sherdog_urls(db)
    rated = [b for b in ds.bouts if getattr(b, "rated", True)]
    cells = collections.defaultdict(list)
    for b in rated:
        d = divisions.to_division(b.div_key, ds.sex.get(b.a))
        if d is None or ds.sex.get(b.a) != "M" or ds.sex.get(b.b) != "M":
            continue
        y = int(b.date[:4])
        stratum = "2010-14" if 2010 <= y < 2015 else "2015-19" if 2015 <= y < 2020 else "2020+" if y >= 2020 else None
        if stratum:
            for f in (b.a, b.b):
                cells[stratum].append((f, b.date[:7], d, b.date, b.promotion, b.weight_class, b.fight_id))
    rng = random.Random(SEED)
    rows = []
    strata = sorted(cells)
    for i, stratum in enumerate(strata):
        per = n // len(strata) + (i < n % len(strata))
        uniq = {}
        for r in cells[stratum]:
            uniq.setdefault((r[0], r[1]), r)
        keys = sorted(uniq)
        for k in rng.sample(keys, per):
            f, month, d, dt, promo, label, fid = uniq[k]
            rows.append((stratum, f, ds.names.get(f, ""), month, d, dt, promo, label, fid,
                         sherdog.get(f, ""), "", ""))
    write_csv(outdir / "division_check_sample.csv",
              ["stratum", "fighter_id", "name", "month", "assigned_div", "bout_date", "promotion", "label",
               "fight_id", "sherdog_url", "external_div", "agrees"], rows)
    return {"sampled": len(rows), "population_fighter_months": {
        s: len({(r[0], r[1]) for r in v}) for s, v in sorted(cells.items())}}


# ---------------------------------------------------------------- side tables
def coverage_audit(db: sqlite3.Connection) -> dict:
    q = lambda sql: db.execute(sql).fetchall()  # noqa: E731
    yr = "substr(e.date,1,4)"
    return {
        "odds_fights_by_year": dict(q(f"SELECT {yr}, count(DISTINCT o.fight_id) FROM odds o JOIN fights f USING(fight_id) "
                                      f"JOIN events e USING(event_id) GROUP BY 1")),
        "odds_sources": dict(q("SELECT source || ':' || book, count(*) FROM odds GROUP BY 1 ORDER BY 2 DESC LIMIT 10")),
        "judge_scores_fights": q("SELECT count(DISTINCT fight_id) FROM judge_scores")[0][0],
        "round_stats_fights": q("SELECT count(DISTINCT fight_id) FROM round_stats")[0][0],
        "complete_cards_share": q("SELECT avg(complete) FROM event_cards")[0][0],
        "events_with_card_info": q("SELECT count(*) FROM event_cards")[0][0],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    dbp = args.db or max(RAW_DIR.glob("db-*/canon.db"))
    tag = dbp.parent.name
    outdir = args.out or BUILD_DIR / "audit" / tag
    outdir.mkdir(parents=True, exist_ok=True)

    db = sqlite3.connect(f"file:{dbp}?mode=ro", uri=True)
    last_event = db.execute("SELECT max(date) FROM events WHERE date <= date('now')").fetchone()[0]
    report: dict = {"release": tag, "sha256": sha256(dbp), "last_event_not_in_future": last_event}
    report["raw"] = raw_integrity(db, last_event)
    report["methods"] = method_audit(db, outdir)
    ds = data.load(dbp)
    report["bouts"] = bout_audit(ds, outdir)
    report["fighters"] = fighter_audit(db, ds, outdir)
    report["divisions"] = division_audit(ds, outdir, sherdog_urls(db))
    report["division_sample"] = division_sample(db, ds, outdir)
    report["coverage"] = coverage_audit(db)
    db.close()
    (outdir / "audit.json").write_text(json.dumps(report, indent=1, ensure_ascii=False, default=str))
    print(outdir / "audit.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
