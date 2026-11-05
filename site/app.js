"use strict";

const TR_MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
  "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
const $ = (id) => document.getElementById(id);
const cache = new Map();
let meta = null;
const state = { month: null, scope: "global", div: "HW" };

async function getJSON(url) {
  if (!cache.has(url)) cache.set(url, fetch(url).then((r) => {
    if (!r.ok) throw new Error(`${url}: ${r.status}`);
    return r.json();
  }));
  return cache.get(url);
}

function readHash() {
  const [month, scope, div] = location.hash.replace(/^#/, "").split("/");
  if (month && meta.months.includes(month)) state.month = month;
  if (scope && (scope === "global" || meta.orgs[scope])) state.scope = scope;
  if (div && meta.divisions[div]) state.div = div;
}

function writeHash() {
  history.replaceState(null, "", `#${state.month}/${state.scope}/${state.div}`);
}

function fillSelect(sel, items, value) {
  sel.replaceChildren(...items.map(([v, label]) => {
    const o = document.createElement("option");
    o.value = v; o.textContent = label; o.selected = v === value;
    return o;
  }));
}

function renderControls() {
  const years = [...new Set(meta.months.map((m) => m.slice(0, 4)))];
  const y = state.month.slice(0, 4);
  fillSelect($("year"), years.map((v) => [v, v]).reverse(), y);
  const months = meta.months.filter((m) => m.startsWith(y));
  fillSelect($("month"), months.map((m) => [m, TR_MONTHS[+m.slice(5) - 1]]), state.month);
  const scopes = [["global", "Global (tüm organizasyonlar)"]];
  for (const [k, o] of Object.entries(meta.orgs)) {
    if (o.first && o.first <= state.month && o.last >= state.month) scopes.push([k, o.name]);
  }
  if (!scopes.some(([k]) => k === state.scope)) state.scope = "global";
  fillSelect($("scope"), scopes, state.scope);
}

function renderTabs(lists) {
  const nav = $("divisions");
  nav.replaceChildren(...Object.entries(meta.divisions).map(([code, name]) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = name;
    b.setAttribute("aria-pressed", String(code === state.div));
    b.disabled = !(lists[code] && lists[code].length);
    b.addEventListener("click", () => { state.div = code; render(); });
    return b;
  }));
}

function fmtDate(iso) {
  const [y, m, d] = iso.split("-");
  return `${+d} ${TR_MONTHS[+m - 1].slice(0, 3)} ${y}`;
}

async function render() {
  renderControls();
  writeHash();
  const data = await getJSON(`data/months/${state.month}.json`);
  const lists = state.scope === "global" ? data.global : (data.orgs[state.scope] || {});
  if (!(lists[state.div] && lists[state.div].length)) {
    const first = Object.keys(meta.divisions).find((d) => lists[d] && lists[d].length);
    if (first) state.div = first;
  }
  renderTabs(lists);
  const rows = lists[state.div] || [];
  const scopeName = state.scope === "global" ? "Global" : meta.orgs[state.scope].name;
  const monthName = `${TR_MONTHS[+state.month.slice(5) - 1]} ${state.month.slice(0, 4)}`;
  $("list-title").textContent = `${scopeName} · ${meta.divisions[state.div]} · ${monthName}`;
  $("list-note").textContent = state.month === meta.months[meta.months.length - 1]
    ? `Veri ${fmtDate(meta.data_through)} tarihine kadar.` : `${monthName} sonu itibarıyla, yalnızca o tarihe kadarki maçlarla.`;
  const tbody = document.querySelector("#table tbody");
  tbody.replaceChildren(...rows.map((r) => {
    const tr = document.createElement("tr");
    const future = r.div_src === "future"
      ? ' <span class="mark" title="Sıklet, dövüşçünün sonraki bir maçından çıkarıldı">≈</span>' : "";
    const orgs = state.scope === "global" ? r.orgs.map((o) => `<span class="tag">${meta.orgs[o].name}</span>`).join("") : "";
    tr.innerHTML = `
      <td class="num">${r.rank}</td>
      <td class="name">${escapeHtml(r.name)}${future}${orgs}</td>
      <td class="num"><strong>${r.score}</strong></td>
      <td class="num hide-sm">${r.mu} ± ${r.rd}</td>
      <td class="num">${r.record}</td>
      <td class="hide-sm">${fmtDate(r.last)}</td>`;
    return tr;
  }));
  $("empty").hidden = rows.length > 0;
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

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

async function init() {
  meta = await getJSON("data/meta.json");
  state.month = meta.months[meta.months.length - 1];
  readHash();
  renderMeta();
  $("year").addEventListener("change", (e) => {
    const ms = meta.months.filter((m) => m.startsWith(e.target.value));
    const sameMonth = ms.find((m) => m.slice(5) === state.month.slice(5));
    state.month = sameMonth || ms[ms.length - 1];
    render();
  });
  $("month").addEventListener("change", (e) => { state.month = e.target.value; render(); });
  $("scope").addEventListener("change", (e) => { state.scope = e.target.value; render(); });
  window.addEventListener("hashchange", () => { readHash(); render(); });
  render();
}

init().catch((err) => {
  document.querySelector("main").insertAdjacentHTML("afterbegin",
    `<p class="note">Veri yüklenemedi: ${escapeHtml(String(err))}</p>`);
});
