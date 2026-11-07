"use strict";

const TR_MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
  "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
const METHOD = { KO_TKO: "KO/TKO", SUB: "SUB", DEC_UNAN: "UD", DEC_SPLIT: "SD", DEC_MAJ: "MD", DEC_TECH: "TD",
  DEC_UNSPEC: "DEC", DRAW: "Berabere", OTHER: "Diğer", NC: "NC", DQ: "DQ", MISSING: "?", NA: "?" };
const RESULT = { W: "G", L: "M", D: "B", NC: "NC" };
const TIE_BAND = 0.05; // "başa baş": neighbours whose win probability is within 50 % ± 5 points
const $ = (id) => document.getElementById(id);
const cache = new Map();
let meta = null;
let index = null; // [[id, name, nat, last listed month]]
const state = { month: null, scope: "global", div: "HW" };
let fighterView = null; // fighter id while a profile is open
let lastFocus = null;

async function getJSON(url) {
  if (!cache.has(url)) cache.set(url, fetch(url).then((r) => {
    if (!r.ok) throw new Error(`${url}: ${r.status}`);
    return r.json();
  }));
  return cache.get(url);
}

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const monthName = (ym) => `${TR_MONTHS[+ym.slice(5, 7) - 1]} ${ym.slice(0, 4)}`;
const monthShort = (ym) => `${TR_MONTHS[+ym.slice(5, 7) - 1].slice(0, 3)} ${ym.slice(0, 4)}`;
const fmtDate = (iso) => `${+iso.slice(8, 10)} ${TR_MONTHS[+iso.slice(5, 7) - 1].slice(0, 3)} ${iso.slice(0, 4)}`;
const pad = (n) => String(n).padStart(2, "0");
const signed = (x) => (x > 0 ? `+${x}` : x < 0 ? `−${-x}` : "0");
const flag = (code, cls = "flag") => code
  ? `<img class="${cls}" src="flags/${esc(code)}.svg" alt="" width="28" height="20" loading="lazy" decoding="async">`
  : `<span class="${cls} none" aria-hidden="true"></span>`;
const listHash = () => `#${state.month}/${state.scope}/${state.div}`;

// Glicko-1 win probability, the same formula as the rating engine (glicko.py)
const Q = Math.LN10 / 400;
function winProb(muA, rdA, muB, rdB) {
  const rd = Math.hypot(rdA, rdB);
  const g = 1 / Math.sqrt(1 + 3 * Q * Q * rd * rd / (Math.PI * Math.PI));
  return 1 / (1 + 10 ** (-g * (muA - muB) / 400));
}

/* ---------- routing ---------- */

function readHash() {
  const h = location.hash.replace(/^#/, "");
  const m = h.match(/^f\/(\d+)$/);
  if (m) { fighterView = +m[1]; return; }
  fighterView = null;
  const [month, scope, div] = h.split("/");
  if (month && meta.months.includes(month)) state.month = month;
  if (scope && (scope === "global" || meta.orgs[scope])) state.scope = scope;
  if (div && meta.divisions[div]) state.div = div;
}

function route() {
  readHash();
  closeSheet();
  $("search-results").hidden = true;
  if (fighterView) {
    $("list-view").hidden = true;
    $("profile-view").hidden = false;
    renderProfile(fighterView).catch(showError);
  } else {
    const fromProfile = !$("profile-view").hidden;
    $("profile-view").hidden = true;
    $("list-view").hidden = false;
    if (fromProfile) window.scrollTo(0, 0);
    renderList().catch(showError);
  }
}

function go(hash) {
  if (location.hash === hash) route(); else location.hash = hash;
}

/* ---------- list ---------- */

function listsOf(data, scope) {
  return scope === "global" ? data.global : (data.orgs[scope] || {});
}

function renderControls() {
  const sel = $("month");
  if (!sel.options.length) {
    sel.replaceChildren(...[...meta.months].reverse().map((m) => new Option(monthName(m), m)));
  }
  sel.value = state.month;
  const i = meta.months.indexOf(state.month);
  $("prev").disabled = i <= 0;
  $("next").disabled = i >= meta.months.length - 1;
  const scopes = [["global", "Global"]];
  for (const [k, o] of Object.entries(meta.orgs)) {
    if (o.first && o.first <= state.month && o.last >= state.month) scopes.push([k, o.name]);
  }
  if (!scopes.some(([k]) => k === state.scope)) state.scope = "global";
  $("scope").replaceChildren(...scopes.map(([v, l]) => new Option(l, v, false, v === state.scope)));
}

function renderTabs(lists) {
  $("divisions").replaceChildren(...Object.entries(meta.divisions).map(([code, name]) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = name;
    b.setAttribute("aria-pressed", String(code === state.div));
    b.disabled = !(lists[code] && lists[code].length);
    b.addEventListener("click", () => { state.div = code; go(listHash()); });
    return b;
  }));
  const nav = $("divisions"), on = nav.querySelector('[aria-pressed="true"]');
  if (on && nav.scrollWidth > nav.clientWidth) nav.scrollLeft = on.offsetLeft - nav.offsetLeft - (nav.clientWidth - on.offsetWidth) / 2;
}

function axisFor(rows) {
  let lo = Infinity, hi = -Infinity;
  for (const r of rows) {
    lo = Math.min(lo, r.mu - 2 * r.rd, r.score);
    hi = Math.max(hi, r.mu + 2 * r.rd);
  }
  const span = hi - lo;
  const step = span > 900 ? 300 : span > 450 ? 200 : 100;
  lo = Math.floor(lo / step) * step;
  hi = Math.ceil(hi / step) * step;
  const ticks = [];
  for (let t = lo; t <= hi; t += step) ticks.push(t);
  return { lo, hi, ticks, x: (v) => Math.max(0, Math.min(100, ((v - lo) / (hi - lo)) * 100)) };
}

function barHTML(r, ax) {
  const a = ax.x(r.mu - 2 * r.rd), b = ax.x(r.mu + 2 * r.rd);
  return `<span class="track" title="μ ${r.mu} ± ${r.rd} · aralık ${r.mu - 2 * r.rd}–${r.mu + 2 * r.rd} · sıralama puanı ${r.score}">` +
    `<i class="iv" style="left:${a}%;width:${b - a}%"></i><i class="sc" style="left:${ax.x(r.score)}%"></i>` +
    `<i class="mu" style="left:${ax.x(r.mu)}%"></i></span>`;
}

function tieGroups(rows) {
  // index -> "s" | "m" | "e" for runs of neighbours that are a toss-up
  const pair = rows.slice(0, -1).map((r, i) => Math.abs(winProb(r.mu, r.rd, rows[i + 1].mu, rows[i + 1].rd) - 0.5) < TIE_BAND);
  const out = {};
  pair.forEach((p, i) => {
    if (!p) return;
    if (!out[i]) out[i] = "s";
    out[i + 1] = "e";
    if (out[i] === "e") out[i] = "m";
  });
  return out;
}

function deltaHTML(r, prevRanks) {
  if (!prevRanks) return `<em class="d">–</em>`;
  const p = prevRanks.get(r.id);
  if (p === undefined) return `<em class="d new">yeni</em>`;
  const d = p - r.rank;
  if (d > 0) return `<em class="d up" title="Geçen ay ${p}.">▲${d}</em>`;
  if (d < 0) return `<em class="d down" title="Geçen ay ${p}.">▼${-d}</em>`;
  return `<em class="d">–</em>`;
}

// "37-11-0 (1 NC/DQ)" -> "37-11"; draws only when there are any; the full record stays in the tooltip
function shortRecord(rec) {
  const m = rec.match(/^(\d+)-(\d+)-(\d+)/);
  return m ? `${m[1]}-${m[2]}${+m[3] ? `-${m[3]}` : ""}` : esc(rec);
}

let currentRows = [];

async function renderList() {
  renderControls();
  history.replaceState(null, "", listHash());
  const i = meta.months.indexOf(state.month);
  const prevMonth = i > 0 ? meta.months[i - 1] : null;
  const [data, prev] = await Promise.all([
    getJSON(`data/months/${state.month}.json`),
    prevMonth ? getJSON(`data/months/${prevMonth}.json`).catch(() => null) : null,
  ]);
  const lists = listsOf(data, state.scope);
  if (!(lists[state.div] && lists[state.div].length)) {
    const first = Object.keys(meta.divisions).find((d) => lists[d] && lists[d].length);
    if (first) state.div = first;
    history.replaceState(null, "", listHash());
  }
  renderTabs(lists);
  const rows = lists[state.div] || [];
  currentRows = rows;
  const prevList = prev && listsOf(prev, state.scope)[state.div];
  const prevRanks = prevList ? new Map(prevList.map((r) => [r.id, r.rank])) : null;

  const scopeName = state.scope === "global" ? "" : `${meta.orgs[state.scope].name} · `;
  $("list-title").innerHTML = `${esc(scopeName)}${esc(meta.divisions[state.div])} <span class="dim">· ${monthName(state.month)}</span>`;
  document.title = `${meta.divisions[state.div]} · ${monthName(state.month)} · MMA Rankings`;
  $("list-note").textContent = state.month === meta.months[meta.months.length - 1]
    ? `Son güncelleme: ${fmtDate(meta.data_through)}` : `${monthName(state.month)} sonu itibarıyla`;

  const isP4P = state.div === "P4P";
  $("h-score").textContent = isP4P ? "Endeks" : "Puan";
  $("h-murd").textContent = isP4P ? "Puan" : "μ ± RD";
  const ax = axisFor(rows);
  $("axis").innerHTML = ax.ticks.map((t) => `<span style="left:${ax.x(t)}%">${t}</span>`).join("");
  const ties = isP4P ? {} : tieGroups(rows);

  $("rows").replaceChildren(...rows.map((r, k) => {
    const li = document.createElement("li");
    li.className = "row" + (k === 0 ? " top" : "") + (ties[k] ? ` tie tie-${ties[k]}` : "");
    li.style.setProperty("--i", k);
    const future = r.div_src === "future" ? ' <span class="mark" title="Sıklet, dövüşçünün sonraki bir maçından çıkarıldı">≈</span>' : "";
    const idle = r.penalty > 0
      ? `<span class="tag idle" title="12 aydan uzun süredir maç yok: sıralama puanından ${r.penalty} düşüldü">inaktif −${r.penalty}</span>` : "";
    const div = isP4P ? `<span class="tag">${esc(meta.divisions[r.div])}</span>` : "";
    const orgs = state.scope === "global" && r.orgs.length && k > 0 ? `<span class="tag">${r.orgs.map((o) => esc(meta.orgs[o].name)).join(" · ")}</span>` : "";
    const main = isP4P ? `%${(r.p4p * 100).toFixed(1).replace(".", ",")}` : r.score;
    const second = isP4P ? r.score : `${r.mu} ± ${r.rd}`;
    const tieLabel = ties[k] === "s" ? `<span class="tie-label">[ başa baş ]</span>` : "";
    li.innerHTML = `<a class="row-in" href="#f/${r.id}" data-id="${r.id}">
      <span class="c-rank"><b>${pad(r.rank)}</b>${deltaHTML(r, prevRanks)}</span>
      <span class="c-name">${flag(r.nat)}<span class="nm" lang="en">${esc(r.name)}${future}</span>${div}${idle}${orgs}</span>
      <span class="c-bar">${barHTML(r, ax)}</span><span class="c-tie">${tieLabel}</span>
      <span class="c-score">${main}</span>
      <span class="c-meta"><span class="c-murd">${second}</span><span class="c-rec" title="${esc(r.record)}">${shortRecord(r.record)}</span><span class="c-last">${monthShort(r.last)}</span></span>
    </a>`;
    return li;
  }));
  $("empty").hidden = rows.length > 0;
  $("legend").hidden = rows.length === 0;
}

/* ---------- charts ---------- */

function segments(hist) {
  // split the monthly history where months are missing (fighter off the lists)
  const segs = [];
  let cur = [];
  let prev = null;
  for (const h of hist) {
    const m = +h[0].slice(0, 4) * 12 + +h[0].slice(5, 7);
    if (prev !== null && m !== prev + 1) { segs.push(cur); cur = []; }
    cur.push(h);
    prev = m;
  }
  if (cur.length) segs.push(cur);
  return segs;
}

function chartSVG(hist, fights, width, height, opts = {}) {
  const pad = { l: opts.compact ? 36 : 46, r: 12, t: 12, b: 26 };
  const mi = (ym) => +ym.slice(0, 4) * 12 + +ym.slice(5, 7) - 1;
  const t0 = mi(hist[0][0]), t1 = Math.max(mi(hist[hist.length - 1][0]), t0 + 1);
  let lo = Infinity, hi = -Infinity;
  for (const [, mu, rd] of hist) { lo = Math.min(lo, mu - 2 * rd); hi = Math.max(hi, mu + 2 * rd); }
  const step = hi - lo > 800 ? 200 : hi - lo > 300 ? 100 : 50;
  lo = Math.floor(lo / step) * step; hi = Math.ceil(hi / step) * step;
  const X = (ym) => pad.l + ((mi(ym) - t0) / (t1 - t0)) * (width - pad.l - pad.r);
  const Y = (v) => pad.t + (1 - (v - lo) / (hi - lo)) * (height - pad.t - pad.b);
  let grid = "";
  const ySteps = (hi - lo) / step > 6 ? step * 2 : step;
  for (let v = lo; v <= hi; v += ySteps) grid += `<line x1="${pad.l}" x2="${width - pad.r}" y1="${Y(v)}" y2="${Y(v)}"/><text x="${pad.l - 8}" y="${Y(v) + 4}" text-anchor="end">${v}</text>`;
  const y0 = Math.floor(t0 / 12), y1 = Math.floor(t1 / 12);
  const yStep = Math.max(1, Math.ceil((y1 - y0 + 1) / (opts.compact ? 4 : 8)));
  let xax = "";
  for (let y = y0; y <= y1; y += yStep) {
    const x = X(`${y}-01`);
    if (x >= pad.l - 1) xax += `<text x="${x}" y="${height - 6}" text-anchor="middle">${y}</text>`;
  }
  let band = "", line = "";
  for (const s of segments(hist)) {
    const up = s.map((h) => `${X(h[0]).toFixed(1)},${Y(h[1] + 2 * h[2]).toFixed(1)}`);
    const dn = s.map((h) => `${X(h[0]).toFixed(1)},${Y(h[1] - 2 * h[2]).toFixed(1)}`).reverse();
    band += `<polygon class="band" points="${up.concat(dn).join(" ")}"/>`;
    line += `<polyline class="line" points="${s.map((h) => `${X(h[0]).toFixed(1)},${Y(h[1]).toFixed(1)}`).join(" ")}"/>`;
  }
  const byMonth = new Map(hist.map((h) => [h[0], h]));
  let dots = "";
  for (const f of fights) {
    const h = byMonth.get(f[0].slice(0, 7));
    if (h && f[5] !== null) dots += `<circle class="fight" cx="${X(h[0]).toFixed(1)}" cy="${Y(h[1]).toFixed(1)}" r="${opts.compact ? 2.4 : 3.2}"/>`;
  }
  return {
    svg: `<svg class="chart" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" role="img" aria-label="Puan geçmişi">
      <g class="grid">${grid}</g><g class="xax">${xax}</g>${band}${line}${dots}<line class="hover-line" x1="0" x2="0" y1="${pad.t}" y2="${height - pad.b}" visibility="hidden"/></svg>`,
    X, Y, pad,
  };
}

function attachTooltip(wrap, hist, fights, ch) {
  const svg = wrap.querySelector("svg");
  const tip = document.createElement("div");
  tip.className = "tip";
  tip.hidden = true;
  wrap.appendChild(tip);
  const hl = svg.querySelector(".hover-line");
  const fightsByMonth = new Map();
  for (const f of fights) if (f[5] !== null) fightsByMonth.set(f[0].slice(0, 7), f);
  const xs = hist.map((h) => ch.X(h[0]));
  svg.addEventListener("pointermove", (e) => {
    const r = svg.getBoundingClientRect();
    const x = (e.clientX - r.left) * (svg.viewBox.baseVal.width / r.width);
    let k = 0;
    for (let j = 1; j < xs.length; j++) if (Math.abs(xs[j] - x) < Math.abs(xs[k] - x)) k = j;
    const h = hist[k];
    const f = fightsByMonth.get(h[0]);
    hl.setAttribute("x1", xs[k]); hl.setAttribute("x2", xs[k]); hl.setAttribute("visibility", "visible");
    tip.hidden = false;
    tip.style.left = `${(xs[k] / svg.viewBox.baseVal.width) * 100}%`;
    tip.style.top = `${(ch.Y(h[1]) / svg.viewBox.baseVal.height) * 100}%`;
    tip.textContent = `${monthShort(h[0])} · μ ${h[1]} ± ${h[2]}` +
      (f ? ` · ${RESULT[f[3]]} · ${METHOD[f[4]] || f[4]} · ${signed(Math.round(f[5]))} · ${f[2]}` : "");
  });
  svg.addEventListener("pointerleave", () => { tip.hidden = true; hl.setAttribute("visibility", "hidden"); });
}

/* ---------- bottom sheet ---------- */

async function openSheet(id, trigger) {
  const r = currentRows.find((x) => x.id === id);
  if (!r) { go(`#f/${id}`); return; }
  lastFocus = trigger;
  const sheet = $("sheet");
  sheet.hidden = false;
  document.body.style.overflow = "hidden";
  $("sheet-body").innerHTML = `<p class="note">Yükleniyor…</p>`;
  const p = await getJSON(`data/fighters/${id}.json`);
  const hist = p.hist.slice(-96);
  const last3 = p.fights.filter((f) => f[3] !== "NC").slice(-3).reverse();
  const isP4P = state.div === "P4P";
  $("sheet-body").innerHTML = `
    <div class="sh-name" id="sheet-name">${p.nat ? flag(p.nat) : ""}<span lang="en">${esc(p.name)}</span></div>
    <div class="sh-stats">
      <div><div class="lbl">${isP4P ? "Endeks" : "Puan"}</div><div class="big">${isP4P ? `%${(r.p4p * 100).toFixed(1).replace(".", ",")}` : r.score}</div></div>
      <div class="side">μ ${r.mu} ± ${r.rd}<br>Rekor ${shortRecord(r.record)}</div>
    </div>
    <div class="sh-h">Puan geçmişi</div>
    <div class="chart-wrap" id="sheet-chart"></div>
    <div class="sh-h">Son 3 maç</div>
    <ul class="fights-mini">${last3.map((f) => `<li><span>${RESULT[f[3]]}</span>·<span>${METHOD[f[4]] || f[4]}</span>·<span>${monthShort(f[0])}</span>` +
      `<span class="${f[5] > 0 ? "pos" : f[5] < 0 ? "neg" : ""}">${f[5] === null ? "" : signed(Math.round(f[5]))}</span></li>`).join("")}</ul>
    <a class="btn" href="#f/${id}">Profili aç →</a>`;
  if (hist.length > 1) {
    const box = $("sheet-chart");
    const ch = chartSVG(hist, p.fights, Math.max(260, box.clientWidth), 170, { compact: true });
    box.innerHTML = ch.svg;
    attachTooltip(box, hist, p.fights, ch);
  }
  sheet.querySelector(".sheet-close").focus();
}

function closeSheet() {
  const sheet = $("sheet");
  if (sheet.hidden) return;
  sheet.hidden = true;
  document.body.style.overflow = "";
  if (lastFocus) lastFocus.focus();
}

/* ---------- profile ---------- */

async function findInLists(id) {
  // the fighter's row in the selected month's lists (global first, then organisations)
  const data = await getJSON(`data/months/${state.month}.json`);
  for (const [scope, lists] of [["global", data.global], ...Object.entries(data.orgs)]) {
    for (const [div, rows] of Object.entries(lists)) {
      if (div === "P4P") continue;
      const r = rows.find((x) => x.id === id);
      if (r) return { scope, div, row: r, rows };
    }
  }
  return null;
}

async function renderProfile(id) {
  const view = $("profile-view");
  view.innerHTML = `<p class="note crumb">Yükleniyor…</p>`;
  const [p, at] = await Promise.all([getJSON(`data/fighters/${id}.json`), findInLists(id)]);
  await loadIndex();
  const known = new Map(index.map((x) => [x[0], x]));
  document.title = `${p.name} · MMA Rankings`;
  const last = p.hist[p.hist.length - 1];
  const r = at && at.row;
  let delta = "";
  if (at) {
    const i = meta.months.indexOf(state.month);
    if (i > 0) {
      const prev = await getJSON(`data/months/${meta.months[i - 1]}.json`).catch(() => null);
      const pl = prev && listsOf(prev, at.scope)[at.div];
      const pr = pl && pl.find((x) => x.id === id);
      delta = pr ? (pr.rank > r.rank ? `<span class="d up">▲${pr.rank - r.rank} bu ay</span>` : pr.rank < r.rank ? `<span class="d down">▼${r.rank - pr.rank} bu ay</span>` : "")
        : `<span class="d new">listeye yeni girdi</span>`;
    }
  }
  const scopeName = at ? (at.scope === "global" ? "Global" : meta.orgs[at.scope].name) : "";
  const lastFight = p.fights.length ? p.fights[p.fights.length - 1] : null;
  const recent = p.fights.filter((f) => f[0] >= `${+state.month.slice(0, 4) - 2}${state.month.slice(4)}`);
  const promos = [...new Set(recent.map((f) => f[6]))].slice(0, 3);
  const listLink = at ? `#${state.month}/${at.scope}/${at.div}` : listHash();
  view.innerHTML = `
    <div class="crumb"><a href="${listLink}">Sıralamalar</a> / ${at ? `<a href="${listLink}">${esc(meta.divisions[at.div])}</a> / ` : ""}<b>${esc(p.name)}</b></div>
    <div class="p-head">
      <div class="p-rank${r ? "" : " unranked"}">${r ? pad(r.rank) : "—"}</div>
      <div>
        <div class="p-label">${r ? `${esc(meta.divisions[at.div])} · ${esc(scopeName)} · ${monthName(state.month)}` : `${monthName(state.month)} listelerinde yok`}</div>
        <div class="p-name"><span lang="en">${esc(p.name)}</span> ${p.nat ? flag(p.nat) : ""} ${delta}</div>
        <div class="p-stats">
          <div><span class="lbl">Puan</span><span class="val big">${r ? r.score : last ? last[3] : "—"}</span></div>
          <div><span class="lbl nt">μ ± RD</span><span class="val dim">${r ? `${r.mu} ± ${r.rd}` : last ? `${last[1]} ± ${last[2]}` : "—"}</span></div>
          <div><span class="lbl">Rekor</span><span class="val" title="${r ? esc(r.record) : ""}">${r ? shortRecord(r.record) : recordOf(p.fights)}</span></div>
          <div><span class="lbl">Son maç</span><span class="val">${lastFight ? monthShort(lastFight[0]) : "—"}</span></div>
          ${promos.length ? `<div><span class="lbl">Organizasyonlar</span><span class="val">${promos.map(esc).join(", ")}</span></div>` : ""}
        </div>
        ${r ? "" : `<p class="note">Puan ve μ ± RD, dövüşçünün listelere girebildiği son aya (${last ? monthName(last[0]) : "—"}) aittir.</p>`}
      </div>
    </div>
    <div class="p-main">
      <section>
        <h2 class="sec-h"><span class="br">[</span> puan geçmişi <span class="br">]</span></h2>
        <div class="chart-wrap" id="p-chart"></div>
        <p class="legend note"><span><i class="lg-bar"></i> μ</span><span><i class="lg-bar" style="height:8px;opacity:.35"></i> μ ± 2·RD</span><span><i class="lg-dot"></i> maç</span></p>
      </section>
      <section>
        <h2 class="sec-h"><span class="br">[</span> maç geçmişi <span class="br">]</span></h2>
        <div class="fights-wrap"><table class="fights">
          <thead><tr><th>Tarih</th><th>Rakip</th><th>Sonuç</th><th>Yöntem</th><th>Puan</th></tr></thead>
          <tbody>${[...p.fights].reverse().map((f) => {
            const o = known.get(f[1]);
            const name = o ? `<a href="#f/${f[1]}">${esc(f[2])}</a>` : esc(f[2]);
            return `<tr><td title="${esc(f[0])} · ${esc(f[6])}">${monthShort(f[0])}</td><td class="opp" lang="en">${flag(o && o[2])}${name}</td><td><span class="res ${f[3]}">${RESULT[f[3]]}</span></td>` +
              `<td>${METHOD[f[4]] || esc(f[4])}</td>` +
              `<td class="${f[5] > 0 ? "pos" : f[5] < 0 ? "neg" : ""}">${f[5] === null ? "" : signed(Math.round(f[5]))}</td></tr>`;
          }).join("")}</tbody>
        </table></div>
      </section>
    </div>
    ${r ? `<section><h2 class="sec-h"><span class="br">[</span> benzer seviyede <span class="br">]</span></h2><div class="similar" id="similar"></div></section>` : ""}`;
  drawProfileChart(p);
  if (r) {
    const near = at.rows.filter((x) => x.id !== id).sort((a, b) => Math.abs(a.score - r.score) - Math.abs(b.score - r.score)).slice(0, 3)
      .sort((a, b) => a.rank - b.rank);
    const ax = axisFor([r, ...near]);
    $("similar").innerHTML = near.map((x) => `<a class="sim" href="#f/${x.id}">
      <div class="sim-top">${flag(x.nat)}<span lang="en">${pad(x.rank)} · ${esc(x.name)}</span><span>${x.score}</span></div>
      <div class="note">μ ${x.mu} ± ${x.rd} · kazanma olasılığı %${Math.round(winProb(r.mu, r.rd, x.mu, x.rd) * 100)}</div>
      ${barHTML(x, ax)}</a>`).join("");
  }
  window.scrollTo(0, 0);
}

function recordOf(fights) {
  const n = { W: 0, L: 0, D: 0 };
  for (const f of fights) if (f[3] in n && f[5] !== undefined) n[f[3]] += 1;
  return `${n.W}-${n.L}-${n.D}`;
}

function drawProfileChart(p) {
  const box = $("p-chart");
  if (!box) return;
  if (p.hist.length < 2) { box.innerHTML = `<p class="note">Grafik için yeterli ay yok.</p>`; return; }
  const w = Math.max(300, box.clientWidth);
  const ch = chartSVG(p.hist, p.fights, w, Math.min(380, Math.max(220, w * 0.48)));
  box.innerHTML = ch.svg;
  attachTooltip(box, p.hist, p.fights, ch);
}

/* ---------- search ---------- */

const norm = (s) => s.toLocaleLowerCase("tr").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/ı/g, "i");

async function loadIndex() {
  if (!index) index = (await getJSON("data/fighters/index.json")).map((x) => [...x, norm(x[1])]);
  return index;
}

function setupSearch() {
  const input = $("search"), list = $("search-results");
  let hits = [], sel = -1;
  const draw = () => {
    list.hidden = hits.length === 0;
    list.innerHTML = hits.map((x, k) => `<li><a href="#f/${x[0]}" role="option" aria-selected="${k === sel}">${flag(x[2])}<span>${esc(x[1])}</span>` +
      `<small>${x[3] ? monthShort(x[3]) : ""}</small></a></li>`).join("");
  };
  input.addEventListener("focus", loadIndex);
  input.addEventListener("input", async () => {
    const q = norm(input.value.trim());
    if (q.length < 2) { hits = []; draw(); return; }
    await loadIndex();
    hits = index.filter((x) => x[4].includes(q))
      .sort((a, b) => (b[4].startsWith(q) - a[4].startsWith(q)) || String(b[3]).localeCompare(String(a[3])))
      .slice(0, 8);
    sel = -1;
    draw();
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      sel = (sel + (e.key === "ArrowDown" ? 1 : -1) + hits.length) % hits.length;
      draw();
    } else if (e.key === "Enter" && hits.length) {
      go(`#f/${hits[Math.max(sel, 0)][0]}`);
      input.value = ""; hits = []; draw(); input.blur();
    } else if (e.key === "Escape") {
      hits = []; draw();
    }
  });
  list.addEventListener("click", () => { input.value = ""; hits = []; draw(); });
  document.addEventListener("click", (e) => { if (!e.target.closest(".search")) { hits = []; draw(); } });
}

/* ---------- meta + init ---------- */

function renderMeta() {
  const t = meta.backtest.periods.test;
  const fmt = (x) => x.toLocaleString("tr-TR", { maximumFractionDigits: 3 });
  let html = `Veri sürümü <code>${meta.data_release}</code> · algoritma <code>${meta.algorithm}</code> ` +
    `· parametre özeti <code>${meta.params_hash}</code> · üretildi ${meta.generated_at.slice(0, 10)}.<br>` +
    `Test dönemi (2021+) tahmin başarısı, iki dövüşçünün de en az 3 önceki maçı olan ${t.both_3plus_prior.n.toLocaleString("tr-TR")} maçta: ` +
    `isabet %${fmt(t.both_3plus_prior.accuracy * 100)}, log loss ${fmt(t.both_3plus_prior.log_loss)} (yazı-tura: 0,693).`;
  if (t.odds_subset_market) {
    html += ` Bahis oranı olan ${t.odds_subset_model.n.toLocaleString("tr-TR")} maçta model isabeti %${fmt(t.odds_subset_model.accuracy * 100)}, ` +
      `bahis piyasası %${fmt(t.odds_subset_market.accuracy * 100)}.`;
  }
  $("meta").innerHTML = html;
}

function showError(err) {
  document.querySelector("main").insertAdjacentHTML("afterbegin",
    `<p class="note wrap">Veri yüklenemedi: ${esc(String(err))}</p>`);
}

async function init() {
  meta = await getJSON("data/meta.json");
  state.month = meta.months[meta.months.length - 1];
  readHash();
  renderMeta();
  setupSearch();
  const step = (k) => {
    const i = meta.months.indexOf(state.month) + k;
    if (i >= 0 && i < meta.months.length) { state.month = meta.months[i]; go(listHash()); }
  };
  $("prev").addEventListener("click", () => step(-1));
  $("next").addEventListener("click", () => step(1));
  $("month").addEventListener("change", (e) => { state.month = e.target.value; go(listHash()); });
  $("scope").addEventListener("change", (e) => { state.scope = e.target.value; go(listHash()); });
  $("home").addEventListener("click", (e) => { e.preventDefault(); go(listHash()); });
  $("nav-list").addEventListener("click", (e) => { e.preventDefault(); go(listHash()); });
  document.querySelector('a[href="#yontem"]').addEventListener("click", (e) => {
    e.preventDefault();
    $("yontem").scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  });
  // a row opens the summary sheet; ctrl/cmd-click still opens the profile link
  $("rows").addEventListener("click", (e) => {
    const a = e.target.closest(".row-in");
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
    e.preventDefault();
    openSheet(+a.dataset.id, a).catch(showError);
  });
  $("sheet").addEventListener("click", (e) => { if (e.target.closest("[data-close]")) closeSheet(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeSheet(); });
  let rt;
  window.addEventListener("resize", () => {
    clearTimeout(rt);
    rt = setTimeout(() => { if (fighterView) getJSON(`data/fighters/${fighterView}.json`).then(drawProfileChart); }, 150);
  });
  window.addEventListener("hashchange", route);
  route();
}

init().catch(showError);
