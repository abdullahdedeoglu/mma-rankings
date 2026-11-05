"""Command line: `mmarank build`, `mmarank backtest`, `mmarank tune`, `mmarank latest-tag`."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from . import backtest, data, engine, export, fetch, validate
from .config import BUILD_DIR


def _db(args) -> tuple[Path, str]:
    if args.db:
        p = Path(args.db)
        return p, p.parent.name
    path = fetch.fetch(args.tag)
    return path, path.parent.name


def cmd_build(args) -> int:
    t0 = time.time()
    db, release = _db(args)
    print(f"[build] release {release}")
    ds = data.load(db)
    print(f"[build] {len(ds.bouts)} bouts loaded ({time.time() - t0:.0f}s)")
    res = engine.run(ds)
    print(f"[build] {len(res.snapshots)} monthly snapshots, data through {res.last_date} ({time.time() - t0:.0f}s)")
    problems = validate.check(ds, res)
    if problems and not args.force:
        print("[build] VALIDATION FAILED:\n  - " + "\n  - ".join(problems), file=sys.stderr)
        return 2
    bt = backtest.report(res.predictions, backtest.odds_probs(db))
    out = Path(args.out)
    export.write_site(ds, res, release, bt, out)
    (out / "data" / "duplicates_removed.json").write_text(json.dumps(ds.duplicates, indent=0))
    (out / "data" / "sex_conflicts.json").write_text(json.dumps(
        [{"a": a, "a_name": ds.names.get(a), "b": b, "b_name": ds.names.get(b)} for a, b in ds.sex_conflicts], indent=1))
    print(f"[build] site written to {out} ({time.time() - t0:.0f}s)")
    return 0


def cmd_backtest(args) -> int:
    db, _ = _db(args)
    ds = data.load(db)
    res = engine.run(ds, snapshots=False)
    print(json.dumps(backtest.report(res.predictions, backtest.odds_probs(db)), indent=1))
    return 0


def cmd_tune(args) -> int:
    from . import tune
    db, _ = _db(args)
    res = tune.grid(data.load(db))
    print(json.dumps(res[:5], indent=1))
    return 0


def cmd_latest_tag(args) -> int:
    print(fetch.latest_tag())
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mmarank")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("build", cmd_build), ("backtest", cmd_backtest), ("tune", cmd_tune)]:
        p = sub.add_parser(name)
        p.add_argument("--tag", help="Fight Canon release tag (default: latest)")
        p.add_argument("--db", help="use a local canon.db instead of downloading")
        p.set_defaults(fn=fn)
        if name == "build":
            p.add_argument("--out", default=str(BUILD_DIR / "site"))
            p.add_argument("--force", action="store_true", help="publish even if validation fails")
    sub.add_parser("latest-tag").set_defaults(fn=cmd_latest_tag)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
