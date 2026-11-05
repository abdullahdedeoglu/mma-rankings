"""Grid search of model parameters on the TRAIN period only (<= 2015).

Objective: log loss on bouts where both fighters have >= 3 prior rated bouts
(the bouts rankings are about). Validation-period scores are printed alongside
so over-fitting to the training years is visible.
"""

from __future__ import annotations

import itertools
from dataclasses import replace

from . import backtest, engine
from .config import MODEL, ModelParams
from .data import Dataset

DECISION_SCHEMES = {
    "flat": {"DEC_UNAN": 1.0, "DEC_UNSPEC": 1.0, "DEC_TECH": 1.0, "DEC_MAJ": 1.0, "DEC_SPLIT": 1.0},
    "fightmatrix": {"DEC_UNAN": 0.9, "DEC_UNSPEC": 0.8, "DEC_TECH": 0.8, "DEC_MAJ": 0.6, "DEC_SPLIT": 0.55},
    "mild": {"DEC_UNAN": 0.95, "DEC_UNSPEC": 0.9, "DEC_TECH": 0.9, "DEC_MAJ": 0.75, "DEC_SPLIT": 0.65},
}


def score(ds: Dataset, model: ModelParams) -> dict:
    preds = engine.run(ds, model=model, snapshots=False).predictions
    tr = backtest.select(preds, "", backtest.TRAIN_END, min_prior=3)
    va = backtest.select(preds, *backtest.VALID, min_prior=3)
    return {"train": backtest.metrics([p.p_a for p in tr]).log_loss,
            "valid": backtest.metrics([p.p_a for p in va]).log_loss}


def grid(ds: Dataset, cs=(10, 20, 35, 50), rds=(250, 350), schemes=tuple(DECISION_SCHEMES)) -> list[dict]:
    out = []
    for c, rd, sch in itertools.product(cs, rds, schemes):
        outcome = dict(MODEL.outcome)
        outcome.update(DECISION_SCHEMES[sch])
        m = replace(MODEL, c=float(c), initial_rd=float(rd), outcome=outcome)
        r = score(ds, m)
        row = {"c": c, "initial_rd": rd, "decisions": sch, **{k: round(v, 5) for k, v in r.items()}}
        print(row, flush=True)
        out.append(row)
    out.sort(key=lambda r: r["train"])
    return out
