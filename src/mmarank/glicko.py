"""Glicko-1 (Glickman 1999), allowing fractional outcomes s in [0, 1].

Reference: http://www.glicko.net/glicko/glicko.pdf
"""

from __future__ import annotations

import math

Q = math.log(10) / 400.0
_PI2 = math.pi**2


def g(rd: float) -> float:
    return 1.0 / math.sqrt(1.0 + 3.0 * Q * Q * rd * rd / _PI2)


def expected(mu: float, mu_j: float, rd_j: float) -> float:
    return 1.0 / (1.0 + 10.0 ** (-g(rd_j) * (mu - mu_j) / 400.0))


def win_probability(mu_a: float, rd_a: float, mu_b: float, rd_b: float) -> float:
    """P(A beats B) accounting for both players' uncertainty (Glickman 1999, eq. for E)."""
    return expected(mu_a, mu_b, math.sqrt(rd_a * rd_a + rd_b * rd_b))


def inflate(rd: float, months: float, c: float, max_rd: float) -> float:
    if months <= 0:
        return rd
    return min(math.sqrt(rd * rd + c * c * months), max_rd)


def update(mu: float, rd: float, games: list[tuple[float, float, float]], min_rd: float = 0.0) -> tuple[float, float]:
    """One rating period. games = [(opp_mu, opp_rd, score)]."""
    if not games:
        return mu, rd
    d_inv = 0.0
    delta = 0.0
    for mu_j, rd_j, s in games:
        gj = g(rd_j)
        e = expected(mu, mu_j, rd_j)
        d_inv += Q * Q * gj * gj * e * (1.0 - e)
        delta += gj * (s - e)
    denom = 1.0 / (rd * rd) + d_inv
    new_mu = mu + (Q / denom) * delta
    new_rd = max(math.sqrt(1.0 / denom), min_rd)
    return new_mu, new_rd
