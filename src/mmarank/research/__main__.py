"""uv run python -m mmarank.research <command>

  grid MODEL...  [--synthetic SEED] [--out DIR] [--workers N]   run pre-registered grids
  select MODEL... [--out DIR]                                    nested selection summary
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..config import BUILD_DIR
from . import evaluate, grid, stream, synthetic


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="mmarank.research")
    ap.add_argument("command", choices=["grid", "select"])
    ap.add_argument("models", nargs="+", choices=sorted(grid.GRIDS))
    ap.add_argument("--synthetic", type=int, default=None, help="use synthetic data with this seed")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--workers", type=int, default=None)
    a = ap.parse_args(argv)
    out = a.out or BUILD_DIR / "research" / (f"synthetic-{a.synthetic}" if a.synthetic is not None else stream.TAG)
    if a.command == "grid":
        st = synthetic.stream(a.synthetic)[0] if a.synthetic is not None else stream.load()
        print(json.dumps(st.meta), flush=True)
        grid.run_grid(st, a.models, out, a.workers)
    else:
        for m in a.models:
            sel = evaluate.select(grid.load_summaries(out, m))
            sel["edge_hits"] = grid.edge_hits(m, sel)
            (out / f"selection_{m}.json").write_text(json.dumps(sel, indent=1))
            print(m, "nested own", round(sel["own_total"]["log_loss"], 5),
                  "lambda", round(sel["lambda_total"]["log_loss"], 5),
                  "| full", {k: round(v["log_loss"], 5) for k, v in sel["full_sequence"].items()},
                  "| edges", sel["edge_hits"])


if __name__ == "__main__":
    main()
