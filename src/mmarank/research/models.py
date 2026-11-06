"""Candidate models M0–M3 (PROTOCOL §6, §6.1).

Every runner walks the stream day by day and, for each decisive bout, emits
eta = logit P(actual winner wins) computed from the state at the start of that
day. `unc` (optional) is the combined pre-fight uncertainty on the Glicko scale
(sqrt(RD_A^2 + RD_B^2)), used for the uncertainty bands of §3.

Binary outcomes only (win 1, loss 0, draw 0.5); finish method, debut priors and
the like are hypotheses for later (§7).
"""

from __future__ import annotations

import math
from array import array
from statistics import NormalDist

from .stream import DAYS_PER_MONTH, Stream

LN10_400 = math.log(10) / 400.0
PI2 = math.pi ** 2
G2_SCALE = 173.7178  # Glicko-2 scale factor (Glickman 2001)
ETA_MAX = 50.0


# ---------------------------------------------------------------- M0 Elo

def run_elo(st: Stream, K: float, unc: array | None = None) -> array:
    r = [0.0] * st.n_fighters
    eta = array("d")
    a_, b_, dr = st.a, st.b, st.draw
    for d in range(len(st.day_ord)):
        i0, i1 = st.day_start[d], st.day_start[d + 1]
        delta: dict[int, float] = {}
        for i in range(i0, i1):
            a, b = a_[i], b_[i]
            diff = r[a] - r[b]
            e = 1.0 / (1.0 + 10.0 ** (-diff / 400.0))
            s = 0.5 if dr[i] else 1.0
            if not dr[i]:
                eta.append(diff * LN10_400)
                if unc is not None:
                    unc.append(0.0)
            delta[a] = delta.get(a, 0.0) + K * (s - e)
            delta[b] = delta.get(b, 0.0) - K * (s - e)
        for f, x in delta.items():
            r[f] += x
    return eta


# ---------------------------------------------------------------- M1 Glicko-1

def glicko1_update(mu: float, rd: float, games, min_rd: float = 0.0) -> tuple[float, float]:
    """One rating period (Glickman 1999). games = [(opp_mu, opp_rd, score)]."""
    q = LN10_400
    d_inv = 0.0
    tot = 0.0
    for mu_j, rd_j, s in games:
        gj = 1.0 / math.sqrt(1.0 + 3.0 * q * q * rd_j * rd_j / PI2)
        e = 1.0 / (1.0 + 10.0 ** (-gj * (mu - mu_j) / 400.0))
        d_inv += q * q * gj * gj * e * (1.0 - e)
        tot += gj * (s - e)
    denom = 1.0 / (rd * rd) + d_inv
    return mu + (q / denom) * tot, max(math.sqrt(1.0 / denom), min_rd)


def run_glicko1(st: Stream, c: float, rd0: float, min_rd: float, unc: array | None = None) -> array:
    n = st.n_fighters
    mu = [1500.0] * n
    rd = [rd0] * n
    last = [-1] * n
    c2 = c * c
    q = LN10_400
    eta = array("d")
    a_, b_, dr = st.a, st.b, st.draw
    for d in range(len(st.day_ord)):
        t = st.day_ord[d]
        i0, i1 = st.day_start[d], st.day_start[d + 1]
        pre: dict[int, tuple[float, float]] = {}
        for i in range(i0, i1):
            for f in (a_[i], b_[i]):
                if f not in pre:
                    r = rd[f]
                    if last[f] >= 0:
                        r = min(math.sqrt(r * r + c2 * (t - last[f]) / DAYS_PER_MONTH), rd0)
                    pre[f] = (mu[f], r)
        games: dict[int, list] = {}
        for i in range(i0, i1):
            a, b = a_[i], b_[i]
            ma, ra = pre[a]
            mb, rb = pre[b]
            if dr[i]:
                s = 0.5
            else:
                s = 1.0
                comb2 = ra * ra + rb * rb
                g = 1.0 / math.sqrt(1.0 + 3.0 * q * q * comb2 / PI2)
                eta.append(g * q * (ma - mb))
                if unc is not None:
                    unc.append(math.sqrt(comb2))
            games.setdefault(a, []).append((mb, rb, s))
            games.setdefault(b, []).append((ma, ra, 1.0 - s))
        for f, gl in games.items():
            m, r = pre[f]
            mu[f], rd[f] = glicko1_update(m, r, gl, min_rd)
            last[f] = t
    return eta


# ---------------------------------------------------------------- M2 Glicko-2 (continuous time)

def _g2(phi: float) -> float:
    return 1.0 / math.sqrt(1.0 + 3.0 * phi * phi / PI2)


def glicko2_update(mu: float, phi: float, sigma: float, games, tau: float, dt: float = 1.0,
                   phi_cap: float = math.inf, eps: float = 1e-6) -> tuple[float, float, float]:
    """One update on the Glicko-2 scale (Glickman 2001, steps 3-7), generalised to
    dt periods since the last update (PROTOCOL §6.1). games = [(opp_mu, opp_phi, score)].
    The added variance is dt * sigma'^2; phi* = sqrt(phi^2 + dt * sigma'^2) is capped at phi_cap."""
    v_inv = 0.0
    tot = 0.0
    for mu_j, phi_j, s in games:
        gj = _g2(phi_j)
        e = 1.0 / (1.0 + math.exp(-gj * (mu - mu_j)))
        v_inv += gj * gj * e * (1.0 - e)
        tot += gj * (s - e)
    v = 1.0 / v_inv
    delta = v * tot
    # Volatility by the Illinois algorithm, on x = ln(dt * sigma'^2).
    a = math.log(dt * sigma * sigma)
    phi2 = phi * phi
    d2 = delta * delta
    t2 = tau * tau

    def f(x: float) -> float:
        ex = math.exp(x)
        return ex * (d2 - phi2 - v - ex) / (2.0 * (phi2 + v + ex) ** 2) - (x - a) / t2

    A = a
    if d2 > phi2 + v:
        B = math.log(d2 - phi2 - v)
    else:
        k = 1
        while f(a - k * tau) < 0:
            k += 1
        B = a - k * tau
    fA, fB = f(A), f(B)
    while abs(B - A) > eps:
        C = A + (A - B) * fA / (fB - fA)
        fC = f(C)
        if fC * fB <= 0:
            A, fA = B, fB
        else:
            fA /= 2.0
        B, fB = C, fC
    var_add = math.exp(A)  # = dt * sigma'^2
    new_sigma = math.sqrt(var_add / dt)
    phi_star = min(math.sqrt(phi2 + var_add), phi_cap)
    new_phi = 1.0 / math.sqrt(1.0 / (phi_star * phi_star) + 1.0 / v)
    return mu + new_phi * new_phi * tot, new_phi, new_sigma


def run_glicko2(st: Stream, tau: float, rd0: float, sigma0: float, unc: array | None = None) -> array:
    n = st.n_fighters
    phi0 = rd0 / G2_SCALE
    mu = [0.0] * n
    phi = [phi0] * n
    sig = [sigma0] * n
    last = [-1] * n
    min_dt = 1.0 / DAYS_PER_MONTH
    eta = array("d")
    a_, b_, dr = st.a, st.b, st.draw
    for d in range(len(st.day_ord)):
        t = st.day_ord[d]
        i0, i1 = st.day_start[d], st.day_start[d + 1]
        pre: dict[int, tuple[float, float, float]] = {}  # (mu, phi before the bout, dt)
        for i in range(i0, i1):
            for f in (a_[i], b_[i]):
                if f not in pre:
                    if last[f] >= 0:
                        dt = max((t - last[f]) / DAYS_PER_MONTH, min_dt)
                        p = min(math.sqrt(phi[f] ** 2 + dt * sig[f] ** 2), phi0)
                    else:
                        dt, p = min_dt, phi0
                    pre[f] = (mu[f], p, dt)
        games: dict[int, list] = {}
        for i in range(i0, i1):
            a, b = a_[i], b_[i]
            ma, pa, _ = pre[a]
            mb, pb, _ = pre[b]
            if dr[i]:
                s = 0.5
            else:
                s = 1.0
                comb = math.sqrt(pa * pa + pb * pb)
                eta.append(_g2(comb) * (ma - mb))
                if unc is not None:
                    unc.append(comb * G2_SCALE)
            games.setdefault(a, []).append((mb, pb, s))
            games.setdefault(b, []).append((ma, pa, 1.0 - s))
        for f, gl in games.items():
            m, _, dt = pre[f]
            mu[f], phi[f], sig[f] = glicko2_update(m, phi[f], sig[f], gl, tau, dt, phi0)
            last[f] = t
    return eta


# ---------------------------------------------------------------- M3 TrueSkill (forward only, 1 vs 1)

_N = NormalDist()
_SQRT2 = math.sqrt(2.0)
_INV_SQRT_2PI = 1.0 / math.sqrt(2.0 * math.pi)


def _pdf(x: float) -> float:
    return _INV_SQRT_2PI * math.exp(-0.5 * x * x)


def _cdf(x: float) -> float:
    return 0.5 * math.erfc(-x / _SQRT2)


def _log_cdf(x: float) -> float:
    if x > -30.0:
        return math.log(_cdf(x))
    # asymptotic: log Phi(x) ~ -x^2/2 - log(-x) - log(sqrt(2 pi))
    return -0.5 * x * x - math.log(-x) - 0.5 * math.log(2.0 * math.pi)


def _v_win(x: float) -> float:
    if x < -30.0:
        return -x
    return _pdf(x) / _cdf(x)


def draw_margin(p_draw: float, beta: float = 1.0) -> float:
    """Herbrich et al. (2006): epsilon = sqrt(2) * beta * Phi^-1((1 + p_draw) / 2) for 1 vs 1."""
    return _SQRT2 * beta * _N.inv_cdf((1.0 + p_draw) / 2.0)


def trueskill_win(mw: float, vw: float, ml: float, vl: float, beta: float, eps: float):
    """Winner (mean, variance), loser (mean, variance) -> updated values."""
    c = math.sqrt(2.0 * beta * beta + vw + vl)
    t = (mw - ml) / c
    e = eps / c
    v = _v_win(t - e)
    w = v * (v + t - e)
    return (mw + vw / c * v, vw * (1.0 - vw / (c * c) * w),
            ml - vl / c * v, vl * (1.0 - vl / (c * c) * w))


def trueskill_draw(ma: float, va: float, mb: float, vb: float, beta: float, eps: float):
    c = math.sqrt(2.0 * beta * beta + va + vb)
    t = (ma - mb) / c
    e = eps / c
    den = _cdf(e - t) - _cdf(-e - t)
    if den < 1e-300:  # extreme mismatch: fall back to the limiting values
        v = -(t - e) if t > 0 else -(t + e)
        w = 1.0
    else:
        v = (_pdf(-e - t) - _pdf(e - t)) / den
        w = v * v + ((e - t) * _pdf(e - t) + (e + t) * _pdf(e + t)) / den
    return (ma + va / c * v, va * (1.0 - va / (c * c) * w),
            mb - vb / c * v, vb * (1.0 - vb / (c * c) * w))


def trueskill_eta(ma: float, va: float, mb: float, vb: float, beta: float, eps: float) -> float:
    """logit P(A wins | not a draw) = log Phi((d - eps)/c) - log Phi((-d - eps)/c)."""
    c = math.sqrt(2.0 * beta * beta + va + vb)
    d = ma - mb
    return _log_cdf((d - eps) / c) - _log_cdf((-d - eps) / c)


def run_trueskill(st: Stream, sigma0: float, gamma: float, p_draw: float, beta: float = 1.0,
                  unc: array | None = None) -> array:
    n = st.n_fighters
    v0 = sigma0 * sigma0
    g2 = gamma * gamma
    eps = draw_margin(p_draw, beta)
    mu = [0.0] * n
    var = [v0] * n
    last = [-1] * n
    eta = array("d")
    a_, b_, dr = st.a, st.b, st.draw
    to_glicko = 400.0 / math.log(10) / beta  # beta-units -> Glicko-like points, for the bands only

    def prior(f: int, t: int) -> float:
        if last[f] < 0 or last[f] == t:
            return var[f]
        return min(var[f] + g2 * (t - last[f]) / DAYS_PER_MONTH, v0)

    for d in range(len(st.day_ord)):
        t = st.day_ord[d]
        i0, i1 = st.day_start[d], st.day_start[d + 1]
        for i in range(i0, i1):  # predictions: start-of-day state
            if not dr[i]:
                a, b = a_[i], b_[i]
                va, vb = prior(a, t), prior(b, t)
                eta.append(max(min(trueskill_eta(mu[a], va, mu[b], vb, beta, eps), ETA_MAX), -ETA_MAX))
                if unc is not None:
                    unc.append(math.sqrt(va + vb) * to_glicko)
        for i in range(i0, i1):  # updates: sequential in fight_id order
            a, b = a_[i], b_[i]
            va, vb = prior(a, t), prior(b, t)
            upd = trueskill_draw if dr[i] else trueskill_win
            mu[a], var[a], mu[b], var[b] = upd(mu[a], va, mu[b], vb, beta, eps)
            last[a] = last[b] = t
    return eta


# ---------------------------------------------------------------- registry

def run_ttt(st: Stream, sigma0: float, gamma: float, p_draw: float, beta: float = 1.0,
            unc: array | None = None) -> array:
    """M4 as pre-registered: each day, predict, add the day, one backward+forward sweep (PROTOCOL §6.1)."""
    from .ttt import run_online
    if unc is not None:
        raise NotImplementedError("uncertainty bands for M4 are not implemented")
    return run_online(st, sigma0, gamma, p_draw, refit_every_days=1, beta=beta)


RUNNERS = {"M0": run_elo, "M1": run_glicko1, "M2": run_glicko2, "M3": run_trueskill, "M4": run_ttt}


def run(model: str, st: Stream, params: dict, unc: array | None = None) -> array:
    return RUNNERS[model](st, **params, unc=unc)
