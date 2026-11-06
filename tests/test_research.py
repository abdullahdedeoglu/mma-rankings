"""Research harness (PROTOCOL §6.1): published examples, leakage, lambda, selection."""

import math
import random

import pytest

from mmarank.research import evaluate, grid, models, synthetic
from mmarank.research.stream import from_records

S = models.G2_SCALE
GAMES = [(1400, 30, 1), (1550, 100, 0), (1700, 300, 0)]  # Glickman's worked example


def test_glicko1_paper_example():
    mu, rd = models.glicko1_update(1500, 200, GAMES)
    assert mu == pytest.approx(1464.1, abs=0.1)
    assert rd == pytest.approx(151.4, abs=0.1)


def test_glicko2_paper_example():
    g = [((r - 1500) / S, d / S, s) for r, d, s in GAMES]
    mu, phi, sigma = models.glicko2_update(0.0, 200 / S, 0.06, g, tau=0.5, dt=1.0)
    assert 1500 + S * mu == pytest.approx(1464.06, abs=0.01)
    assert S * phi == pytest.approx(151.52, abs=0.01)
    assert sigma == pytest.approx(0.05999, abs=1e-5)


def test_glicko2_time_generalisation():
    """dt periods add dt * sigma'^2; with tau -> 0 sigma stays put, so phi* = sqrt(phi^2 + dt*sigma^2)."""
    g = [((r - 1500) / S, d / S, s) for r, d, s in GAMES]
    phi, sigma, dt = 200 / S, 0.06, 4.0
    _, new_phi, new_sigma = models.glicko2_update(0.0, phi, sigma, g, tau=1e-4, dt=dt)
    assert new_sigma == pytest.approx(sigma, rel=1e-3)
    v_inv = 0.0
    for mu_j, phi_j, _ in g:
        gj = models._g2(phi_j)
        e = 1 / (1 + math.exp(gj * mu_j))
        v_inv += gj * gj * e * (1 - e)
    expect = 1 / math.sqrt(1 / (phi * phi + dt * sigma * sigma) + v_inv)
    assert new_phi == pytest.approx(expect, rel=1e-4)


def test_trueskill_published_values():
    beta, sigma = 25 / 6, 25 / 3
    eps = models.draw_margin(0.10, beta)
    mw, vw, ml, vl = models.trueskill_win(25, sigma ** 2, 25, sigma ** 2, beta, eps)
    assert (mw, math.sqrt(vw)) == pytest.approx((29.396, 7.171), abs=1e-3)
    assert (ml, math.sqrt(vl)) == pytest.approx((20.604, 7.171), abs=1e-3)
    ma, va, mb, vb = models.trueskill_draw(25, sigma ** 2, 25, sigma ** 2, beta, eps)
    assert (ma, mb) == pytest.approx((25.0, 25.0))
    assert math.sqrt(va) == pytest.approx(6.457, abs=1e-3)


def test_trueskill_binary_probability_symmetric():
    e1 = models.trueskill_eta(1.0, 0.5, 0.0, 0.8, 1.0, 0.05)
    e2 = models.trueskill_eta(0.0, 0.8, 1.0, 0.5, 1.0, 0.05)
    assert e1 == pytest.approx(-e2)
    assert e1 > 0


SMALL = dict(start="2010-01-01", end="2013-12-31", arrivals_per_week=2.0, events_per_week=2, bouts_per_event=5)
PARAMS = {"M0": {"K": 32}, "M1": {"c": 30, "rd0": 300, "min_rd": 30},
          "M2": {"tau": 0.5, "rd0": 300, "sigma0": 0.12}, "M3": {"sigma0": 2, "gamma": 0.1, "p_draw": 0.014}}


@pytest.mark.parametrize("model", sorted(PARAMS))
def test_no_leakage(model):
    """Predictions up to day D are identical whether or not later bouts exist."""
    records, _ = synthetic.generate(3, **SMALL)
    cut = "2012-06-30"
    full = models.run(model, from_records(records), PARAMS[model])
    part_st = from_records([r for r in records if r[0] <= cut])
    part = models.run(model, part_st, PARAMS[model])
    assert len(part) == part_st.n_decisive > 100
    assert list(full[: len(part)]) == list(part)


@pytest.mark.parametrize("model", ["M0", "M1", "M2"])
def test_same_day_order_irrelevant(model):
    """Within a day, bout order changes nothing (one rating period per day)."""
    records, _ = synthetic.generate(4, **SMALL)
    shuffled = [(d, -fid, e, a, b, dr) for d, fid, e, a, b, dr in records]  # reverses order within each day
    p1 = models.run(model, from_records(records), PARAMS[model])
    p2 = models.run(model, from_records(shuffled), PARAMS[model])
    by_fid1 = dict(zip(from_records(records).fight_id, p1))
    by_fid2 = dict(zip((-f for f in from_records(shuffled).fight_id), p2))
    assert by_fid1.keys() == by_fid2.keys()
    for k in by_fid1:
        assert by_fid1[k] == pytest.approx(by_fid2[k], abs=1e-9)


def test_models_beat_coin_flip_on_synthetic():
    """Random pairing (strong signal): every model must learn something."""
    st, oracle = synthetic.stream(5, **SMALL, match_noise=100.0)
    idx = [i for i in range(st.n_decisive) if st.prior_min[i] >= 3]
    for model, params in PARAMS.items():
        eta = models.run(model, st, params)
        assert evaluate.metrics([eta[i] for i in idx])["log_loss"] < math.log(2), model
    assert evaluate.metrics([oracle[i] for i in idx])["log_loss"] < math.log(2)


def test_fit_lambda_recovers_scale():
    rng = random.Random(0)
    etas = []
    for _ in range(40000):
        x = rng.gauss(0, 1.5)
        y = rng.random() < 1 / (1 + math.exp(-0.7 * x))
        etas.append(x if y else -x)  # winner-oriented
    assert evaluate.fit_lambda([etas]) == pytest.approx(0.7, abs=0.03)


def test_calibration_fit_recovers_slope():
    rng = random.Random(1)
    etas, lower = [], []
    for _ in range(40000):
        x = rng.gauss(0, 1.5)
        y = rng.random() < 1 / (1 + math.exp(-0.8 * x))
        etas.append(x if y else -x)
        lower.append(1 if y else 0)  # 'lower-id fighter' = the side x refers to
    fit = evaluate.calibration_fit(etas, lower)
    assert fit["cal_slope"] == pytest.approx(0.8, abs=0.04)
    assert fit["cal_intercept"] == pytest.approx(0.0, abs=0.04)


def test_select_uses_only_past_years():
    """Config A is best before 2010, B from 2010: the 2010 pick must still be A."""
    def summ(per_year):
        return {"per_year": per_year, "lambda": {y: [1.0, sum(v[1] for k, v in per_year.items() if k < y),
                                                     per_year.get(y, [0, 0.0])[1]] for y in (2009, 2010, 2011)},
                "full": {"lambda": 1.0, "loss_own": 0.0, "loss_lambda": 0.0, "n": 1}}
    a = summ({2008: [10, 6.0], 2009: [10, 6.0], 2010: [10, 9.0], 2011: [10, 9.0]})
    b = summ({2008: [10, 7.0], 2009: [10, 7.0], 2010: [10, 5.0], 2011: [10, 5.0]})
    sel = evaluate.select({"A": a, "B": b}, years=(2009, 2010, 2011))
    assert sel["own"][2010]["config"] == "A"
    assert sel["own"][2011]["config"] == "B"  # 2008-10: A 21, B 19
    assert sel["own"][2011]["loss"] == 5.0


# ---------- M4 (TTT)
from mmarank.research import ttt  # noqa: E402

TTT_PARAMS = {"sigma0": 2.0, "gamma": 0.1, "p_draw": 0.014}


def test_ttt_forward_pass_equals_trueskill():
    """Synthetic fighters never fight twice on one day, so the forward pass must be M3 exactly."""
    st = from_records(synthetic.generate(3, **SMALL)[0])
    a = models.run_trueskill(st, **TTT_PARAMS)
    b = ttt.run_filter_only(st, **TTT_PARAMS)
    assert len(a) == len(b)
    assert max(abs(x - y) for x, y in zip(a, b)) < 1e-9


def test_ttt_online_no_leakage():
    records, _ = synthetic.generate(3, **SMALL)
    cut = "2012-06-30"
    full = ttt.run_online(from_records(records), **TTT_PARAMS, refit_every_days=30)
    part = ttt.run_online(from_records([r for r in records if r[0] <= cut]), **TTT_PARAMS, refit_every_days=30)
    assert len(part) > 100
    assert list(full[: len(part)]) == list(part)


def test_ttt_sweeps_converge():
    st = from_records(synthetic.generate(3, **SMALL)[0])
    m = ttt.TTT(st, **TTT_PARAMS)
    for d in range(len(st.day_ord)):
        m.add_day(d)
    changes, prev = [], None
    for _ in range(6):
        m.sweep()
        s = list(m.lik_tau)
        if prev is not None:
            changes.append(max(abs(x - y) for x, y in zip(s, prev)))
        prev = s
    assert all(c2 < c1 for c1, c2 in zip(changes, changes[1:]))
