"""M4: TrueSkill Through Time (Dangauthier et al. 2007; Landfried & Mocskos 2025), 1 vs 1,
using only data before each prediction (PROTOCOL §6, §6.1).

Model: each fighter has one skill variable per day on which they fight (a "node"); consecutive
nodes are linked by Gaussian drift with variance gamma^2 * months. Each bout is a factor
N(perf_A - perf_B; skills, 2 beta^2) truncated by the result (win: d > eps; draw: |d| < eps).
Inference is expectation propagation: a forward pass along time, a backward pass, and the
bout messages are refreshed with the TrueSkill update on the cavity distributions.

A forward pass alone, with at most one bout per fighter per day, is exactly M3 (TrueSkill,
forward only). The backward pass is what makes the history smooth.

State is kept in plain lists so the model can grow day by day (online use): `add_day`
appends the day's nodes and bouts and runs the forward step for that day only; `sweep`
runs one backward + forward pass over everything added so far.
"""

from __future__ import annotations

import math
from array import array

from . import models
from .stream import DAYS_PER_MONTH, Stream


class TTT:
    def __init__(self, st: Stream, sigma0: float, gamma: float, p_draw: float, beta: float = 1.0):
        self.st = st
        self.v0 = sigma0 * sigma0
        self.g2 = gamma * gamma
        self.beta = beta
        self.eps = models.draw_margin(p_draw, beta)
        # nodes
        self.n_player: list[int] = []
        self.n_t: list[int] = []  # day ordinal
        self.n_prev: list[int] = []
        self.n_next: list[int] = []
        self.fwd_pi: list[float] = []
        self.fwd_tau: list[float] = []
        self.bwd_pi: list[float] = []
        self.bwd_tau: list[float] = []
        self.lik_pi: list[float] = []
        self.lik_tau: list[float] = []
        self.day_nodes: list[list[int]] = []  # per added day
        self.last_node = [-1] * st.n_fighters
        # bouts added so far: node of a, node of b, and the two messages
        self.b_na: list[int] = []
        self.b_nb: list[int] = []
        self.ma_pi: list[float] = []
        self.ma_tau: list[float] = []
        self.mb_pi: list[float] = []
        self.mb_tau: list[float] = []
        self.days_added = 0

    # ---------------------------------------------------------------- helpers

    def _drift(self, pi: float, tau: float, dt_months: float, cap: bool) -> tuple[float, float]:
        if pi <= 0.0:
            return 0.0, 0.0  # uniform stays uniform
        var = 1.0 / pi + self.g2 * dt_months
        if cap and var > self.v0:
            var = self.v0
        mu = tau / pi
        return 1.0 / var, mu / var

    def _forward_node(self, k: int) -> None:
        p = self.n_prev[k]
        if p < 0:
            self.fwd_pi[k], self.fwd_tau[k] = 1.0 / self.v0, 0.0
            return
        pi = self.fwd_pi[p] + self.lik_pi[p]
        tau = self.fwd_tau[p] + self.lik_tau[p]
        self.fwd_pi[k], self.fwd_tau[k] = self._drift(pi, tau, (self.n_t[k] - self.n_t[p]) / DAYS_PER_MONTH, True)

    def _backward_node(self, k: int) -> None:
        q = self.n_next[k]
        if q < 0:
            self.bwd_pi[k] = self.bwd_tau[k] = 0.0
            return
        pi = self.bwd_pi[q] + self.lik_pi[q]
        tau = self.bwd_tau[q] + self.lik_tau[q]
        self.bwd_pi[k], self.bwd_tau[k] = self._drift(pi, tau, (self.n_t[q] - self.n_t[k]) / DAYS_PER_MONTH, False)

    def _update_bout(self, j: int) -> None:
        na, nb = self.b_na[j], self.b_nb[j]
        # cavities: node marginal without this bout's message
        pa = self.fwd_pi[na] + self.bwd_pi[na] + self.lik_pi[na] - self.ma_pi[j]
        ta = self.fwd_tau[na] + self.bwd_tau[na] + self.lik_tau[na] - self.ma_tau[j]
        pb = self.fwd_pi[nb] + self.bwd_pi[nb] + self.lik_pi[nb] - self.mb_pi[j]
        tb = self.fwd_tau[nb] + self.bwd_tau[nb] + self.lik_tau[nb] - self.mb_tau[j]
        va, vb = 1.0 / pa, 1.0 / pb
        ma, mb = ta * va, tb * vb
        upd = models.trueskill_draw if self.st.draw[self._bout_index[j]] else models.trueskill_win
        ma2, va2, mb2, vb2 = upd(ma, va, mb, vb, self.beta, self.eps)
        new_pa, new_ta = 1.0 / va2 - pa, ma2 / va2 - ta
        new_pb, new_tb = 1.0 / vb2 - pb, mb2 / vb2 - tb
        self.lik_pi[na] += new_pa - self.ma_pi[j]
        self.lik_tau[na] += new_ta - self.ma_tau[j]
        self.lik_pi[nb] += new_pb - self.mb_pi[j]
        self.lik_tau[nb] += new_tb - self.mb_tau[j]
        self.ma_pi[j], self.ma_tau[j], self.mb_pi[j], self.mb_tau[j] = new_pa, new_ta, new_pb, new_tb

    # ---------------------------------------------------------------- public

    _bout_index: list[int]

    def predict_day(self, d: int) -> list[float]:
        """eta = logit P(winner) for the decisive bouts of stream day d, from what has been added so far
        (days < d must have been added, day d not yet)."""
        st = self.st
        t = st.day_ord[d]
        out = []
        for i in range(st.day_start[d], st.day_start[d + 1]):
            if st.draw[i]:
                continue
            (ma, va), (mb, vb) = self.prior(st.a[i], t), self.prior(st.b[i], t)
            e = models.trueskill_eta(ma, va, mb, vb, self.beta, self.eps)
            out.append(max(min(e, models.ETA_MAX), -models.ETA_MAX))
        return out

    def prior(self, f: int, t: int) -> tuple[float, float]:
        k = self.last_node[f]
        if k < 0:
            return 0.0, self.v0
        pi = self.fwd_pi[k] + self.lik_pi[k] + self.bwd_pi[k]
        tau = self.fwd_tau[k] + self.lik_tau[k] + self.bwd_tau[k]
        var = min(1.0 / pi + self.g2 * (t - self.n_t[k]) / DAYS_PER_MONTH, self.v0)
        return tau / pi, var

    def add_day(self, d: int) -> None:
        """Append stream day d (must be the next day) and run its forward step."""
        assert d == self.days_added
        if not hasattr(self, "_bout_index"):
            self._bout_index = []
        st = self.st
        t = st.day_ord[d]
        nodes: list[int] = []
        node_of: dict[int, int] = {}
        for i in range(st.day_start[d], st.day_start[d + 1]):
            for f in (st.a[i], st.b[i]):
                if f not in node_of:
                    k = len(self.n_player)
                    node_of[f] = k
                    prev = self.last_node[f]
                    self.n_player.append(f)
                    self.n_t.append(t)
                    self.n_prev.append(prev)
                    self.n_next.append(-1)
                    if prev >= 0:
                        self.n_next[prev] = k
                    for lst in (self.fwd_pi, self.fwd_tau, self.bwd_pi, self.bwd_tau, self.lik_pi, self.lik_tau):
                        lst.append(0.0)
                    self.last_node[f] = k
                    nodes.append(k)
            self.b_na.append(node_of[st.a[i]])
            self.b_nb.append(node_of[st.b[i]])
            for lst in (self.ma_pi, self.ma_tau, self.mb_pi, self.mb_tau):
                lst.append(0.0)
            self._bout_index.append(i)
        self.day_nodes.append(nodes)
        self.days_added += 1
        # backward messages of the previous nodes become stale only via the sweep; the new
        # node has no future yet (uniform backward message).
        for k in nodes:
            self._forward_node(k)
        b0 = self.b_first(d)
        for j in range(b0, len(self.b_na)):
            self._update_bout(j)

    def b_first(self, d: int) -> int:
        """Index (in added bouts) of the first bout of day d."""
        return self.st.day_start[d]

    def sweep(self) -> None:
        """One backward pass then one forward pass over everything added so far."""
        st = self.st
        for d in range(self.days_added - 1, -1, -1):
            for k in self.day_nodes[d]:
                self._backward_node(k)
            for j in range(st.day_start[d], st.day_start[d + 1]):
                self._update_bout(j)
        for d in range(self.days_added):
            for k in self.day_nodes[d]:
                self._forward_node(k)
            for j in range(st.day_start[d], st.day_start[d + 1]):
                self._update_bout(j)


def run_filter_only(st: Stream, sigma0: float, gamma: float, p_draw: float, beta: float = 1.0) -> array:
    """Forward pass only (no smoothing): must equal M3 when no fighter has two bouts on one day."""
    m = TTT(st, sigma0, gamma, p_draw, beta)
    eta = array("d")
    for d in range(len(st.day_ord)):
        eta.extend(m.predict_day(d))
        m.add_day(d)
    return eta


def run_online(st: Stream, sigma0: float, gamma: float, p_draw: float, refit_every_days: int = 1,
               beta: float = 1.0, sweeps: int = 1, until_day: int | None = None, timer=None) -> array:
    """M4 as pre-registered when refit_every_days == 1: each day, predict from the current state,
    add the day, then run `sweeps` full backward+forward passes. Larger refit_every_days is the
    approximation the pilot is meant to size (forward-only between refits)."""
    m = TTT(st, sigma0, gamma, p_draw, beta)
    eta = array("d")
    n_days = len(st.day_ord) if until_day is None else until_day
    last_refit = st.day_ord[0]
    for d in range(n_days):
        eta.extend(m.predict_day(d))
        m.add_day(d)
        if st.day_ord[d] - last_refit >= refit_every_days or d == n_days - 1:
            for _ in range(sweeps):
                m.sweep()
            last_refit = st.day_ord[d]
            if timer:
                timer(d, len(m.b_na))
    return eta
