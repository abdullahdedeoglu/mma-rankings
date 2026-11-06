"""Model-independent bout stream (PROTOCOL §6.1, "Ortak kurallar").

All rated bouts, sorted by (date, fight_id), with fighters mapped to dense
integers so the models can keep state in plain lists. Everything a model needs
is per bout or per day; everything the evaluation needs is per decisive bout
(the bouts that get a prediction), in the same order the models emit them.
"""

from __future__ import annotations

import collections
import hashlib
import sqlite3
from array import array
from dataclasses import dataclass, field
from datetime import date as Date
from pathlib import Path

DAYS_PER_MONTH = 30.4375
TAG = "db-2026-11-04-1837"
SHA256 = "e0ea391fff9ec2f9225407160f4407a499d42173cebbe371e306de2769858cf6"


@dataclass
class Stream:
    # per bout
    a: array  # winner, or first fighter of a draw (dense index)
    b: array
    draw: array  # 1 if draw
    # per day: bouts day_start[d] .. day_start[d+1]-1
    day_start: array
    day_ord: array  # date.toordinal()
    n_fighters: int
    # per decisive bout, in model emission order
    year: array
    event: array
    month: array  # year * 12 + month - 1
    men: array  # both fighters male
    prior_min: array  # min prior rated bouts (draws included) at start of day
    unchecked: array  # pro status unchecked in the source (bout_type NULL)
    lower_won: array  # 1 if the fighter with the lower canon id won (calibration orientation)
    fight_id: array
    meta: dict = field(default_factory=dict)

    @property
    def n_decisive(self) -> int:
        return len(self.year)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def from_records(records, sex: dict | None = None, unchecked_ids: set | None = None) -> Stream:
    """records: iterable of (date_iso, fight_id, event_id, a, b, draw) with canon fighter ids."""
    sex = sex or {}
    unchecked_ids = unchecked_ids or set()
    recs = sorted(records, key=lambda r: (r[0], r[1]))
    dense: dict[int, int] = {}

    def idx(f: int) -> int:
        i = dense.get(f)
        if i is None:
            i = dense[f] = len(dense)
        return i

    st = Stream(array("i"), array("i"), array("b"), array("i"), array("i"), 0,
                array("h"), array("i"), array("i"), array("b"), array("i"), array("b"), array("b"), array("i"))
    n_prior: collections.Counter = collections.Counter()
    i = 0
    while i < len(recs):
        day = recs[i][0]
        j = i
        while j < len(recs) and recs[j][0] == day:
            j += 1
        st.day_start.append(i)
        dt = Date.fromisoformat(day)
        st.day_ord.append(dt.toordinal())
        for d, fid, eid, a, b, draw in recs[i:j]:
            st.a.append(idx(a))
            st.b.append(idx(b))
            st.draw.append(1 if draw else 0)
            if not draw:
                st.year.append(dt.year)
                st.event.append(eid)
                st.month.append(dt.year * 12 + dt.month - 1)
                st.men.append(1 if sex.get(a) == "M" and sex.get(b) == "M" else 0)
                st.prior_min.append(min(n_prior[a], n_prior[b]))
                st.unchecked.append(1 if fid in unchecked_ids else 0)
                st.lower_won.append(1 if a < b else 0)
                st.fight_id.append(fid)
        for _, _, _, a, b, _ in recs[i:j]:
            n_prior[a] += 1
            n_prior[b] += 1
        i = j
    st.day_start.append(len(recs))
    st.n_fighters = len(dense)
    return st


def load(tag: str = TAG, drop_unchecked: bool = False) -> Stream:
    """Real data: the pinned Fight Canon release, loaded with the production cleaning
    (PROTOCOL §2). Works with both the committed and the local data.py."""
    from .. import data
    from ..config import RAW_DIR

    db_path = RAW_DIR / tag / "canon.db"
    digest = sha256(db_path)
    if tag == TAG and digest != SHA256:
        raise SystemExit(f"{db_path}: SHA-256 {digest} does not match the protocol's {SHA256}")
    ds = data.load(db_path)
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    unchecked = {fid for (fid,) in db.execute("SELECT fight_id FROM fights WHERE bout_type IS NULL")}
    db.close()
    rated = [b for b in ds.bouts if getattr(b, "rated", True)]
    if drop_unchecked:
        rated = [b for b in rated if b.fight_id not in unchecked]
    st = from_records(((b.date, b.fight_id, b.event_id, b.a, b.b, b.draw) for b in rated), ds.sex, unchecked)
    st.meta = {"tag": tag, "sha256": digest, "rated_bouts": len(rated), "decisive": st.n_decisive,
               "fighters": st.n_fighters, "drop_unchecked": drop_unchecked}
    return st
