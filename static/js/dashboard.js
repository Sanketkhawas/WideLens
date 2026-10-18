/* WideLens dashboard controller */
(function () {
  const $ = id => document.getElementById(id);
  const inr = v => v == null ? '–' : v >= 1e7 ? `₹${(v / 1e7).toFixed(2)} Cr` : v >= 1e5 ? `₹${(v / 1e5).toFixed(2)} L` : `₹${Math.round(v).toLocaleString('en-IN')}`;
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let S, R, sel = 0, timer, seq = 0;
  let weights, radius, econ;

  const ECON_FIELDS = [
    ['capture_rate', 'Capture rate (share of catchment spend won)', 0.01, 1, 0.01],
    ['coverage', 'File covers this share of real sales', 0.01, 1, 0.01],
    ['contribution', 'Contribution margin before rent', 0.01, 0.9, 0.01],
    ['sqft', 'Store size (sq ft)', 100, 20000, 100],
    ['fitout_per_sqft', 'Fit-out cost (₹/sq ft)', 0, 20000, 100],
    ['deposit_months', 'Rent deposit (months)', 0, 36, 1],
  ];

  async function boot() {
    try {
      const r = await fetch('/api/analysis');
      if (!r.ok) { location.href = '/upload'; return; }
      S = await r.json();
      weights = Object.fromEntries(Object.entries(S.defaults.weights).map(([k, v]) => [k, Math.round(v * 100)]));
      radius = S.defaults.radius; econ = { ...S.defaults.econ };
      $('subtitle').textContent = `${S.filename} · ${S.kpis.customers.toLocaleString('en-IN')} customers` + (S.kpis.period_from ? ` · sales ${S.kpis.period_from} – ${S.kpis.period_to}` : '');
      WLMap.init(S);
      buildControls();
      staticCharts();
      await rerank();
    } catch (e) { $('loading').textContent = 'Something went wrong loading the analysis. Try re-uploading your file.'; console.error(e); return; }
    $('loading').classList.add('hide');
  }

  function staticCharts() {
    const k = S.kpis;
    $('notes').innerHTML = S.notes.map(n => `<li>${esc(n)}</li>`).join('');
    WLCharts.forecast(S); WLCharts.areas(S); WLCharts.segments(S); WLCharts.categories(S); WLCharts.age(S);
  }

  function buildControls() {
    $('sliders').innerHTML = Object.keys(S.factor_labels).map(k => `
      <div class="sl"><label>${S.factor_labels[k]}<b id="v_${k}">${weights[k]}</b></label>
      <input type="range" min="0" max="100" value="${weights[k]}" data-k="${k}"></div>`).join('') +
      `<div class="sl"><label>Catchment radius (km)<b id="v_radius">${radius}</b></label><input type="range" min="1" max="8" step="0.5" value="${radius}" id="radius"></div>`;
    $('sliders').querySelectorAll('input[data-k]').forEach(el => el.oninput = () => { weights[el.dataset.k] = +el.value; $('v_' + el.dataset.k).textContent = el.value; schedule(); });
    $('radius').oninput = e => { radius = +e.target.value; $('v_radius').textContent = radius; schedule(); };
    $('econ').innerHTML = ECON_FIELDS.map(([k, l, mn, mx, st]) => `<div><label>${l}</label><input type="number" data-e="${k}" min="${mn}" max="${mx}" step="${st}" value="${econ[k]}"></div>`).join('');
    $('econ').querySelectorAll('input').forEach(el => el.onchange = () => { const v = parseFloat(el.value); if (!isNaN(v)) { econ[el.dataset.e] = v; schedule(); } });
    $('resetBtn').onclick = () => { buildStateFromDefaults(); buildControls(); rerank(); };
    $('pdfBtn').onclick = downloadPdf;
  }
  function buildStateFromDefaults() {
    weights = Object.fromEntries(Object.entries(S.defaults.weights).map(([k, v]) => [k, Math.round(v * 100)]));
    radius = S.defaults.radius; econ = { ...S.defaults.econ };
  }
  const body = () => ({ weights, radius, econ });
  function schedule() { clearTimeout(timer); timer = setTimeout(rerank, 250); }

  async function rerank() {
    const my = ++seq;
    const r = await fetch('/api/rank', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body()) });
    if (!r.ok) return;
    const data = await r.json();
    if (my !== seq) return;           // a newer request superseded this one
    R = data; sel = 0; render();
  }

  async function downloadPdf() {
    const b = $('pdfBtn'); b.textContent = 'Building PDF…'; b.disabled = true;
    try {
      const r = await fetch('/api/report.pdf', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body()) });
      if (!r.ok) throw new Error(r.status);
      const url = URL.createObjectURL(await r.blob());
      const a = document.createElement('a'); a.href = url; a.download = 'WideLens_Nagpur_Expansion_Report.pdf'; a.click(); URL.revokeObjectURL(url);
    } catch (e) { alert('Could not build the PDF.'); }
    b.textContent = '⬇ PDF report'; b.disabled = false;
  }

  function render() {
    const recs = R.recommendations;
    renderHero(); renderKpis(); renderTable();
    WLCharts.rank(recs, S.factor_labels);
    WLMap.showRecs(recs, R.radius, sel, pick);
    $('insights').innerHTML = R.insights.map(t => `<li>${esc(t).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')}</li>`).join('');
    $('road').innerHTML = R.roadmap.map(p => `<li><b>${esc(p.area)}</b> - score ${p.score.toFixed(0)}, ≈ ${inr(p.monthly_revenue)}/month, payback ${p.payback_months ? p.payback_months.toFixed(0) + ' months' : 'n/a'}</li>`).join('') || '<li>No site pays back within 5 years on these assumptions.</li>';
    $('roadNote').textContent = R.roadmap_note || '';
  }

  function pick(i) { sel = i; renderHero(); highlightRow(); WLMap.focus(R.recommendations[i], R.radius); }

  function renderHero() {
    const r = R.recommendations[sel], isTop = sel === 0;
    const rb = r.robust_top1;
    const why = r.why.map(w => `<div class="wrow"><span>${esc(w.label)}</span><div class="bar"><i style="width:${Math.min(100, w.points / Math.max(r.score, 1) * 100)}%"></i></div><b>${w.points.toFixed(0)}</b></div>`).join('');
    const pay = r.payback_months ? `${r.payback_months.toFixed(0)} months` : 'Not viable';
    $('hero').innerHTML = `
      <div>
        <span class="tag">${isTop ? 'RECOMMENDED NEXT STORE' : 'OPTION #' + r.rank}</span>
        <h2>${esc(r.area)}, Nagpur</h2>
        <p class="sub">Expansion score <b>${r.score.toFixed(0)}/100</b> · ${r.dist_to_store_km.toFixed(1)} km from your nearest store</p>
        <div class="stats">
          <div class="stat"><b>${r.catchment_customers.toLocaleString('en-IN')}</b><span>customers within ${R.radius} km</span></div>
          <div class="stat"><b>${r.unserved_customers.toLocaleString('en-IN')}</b><span>of them not near any store</span></div>
          <div class="stat"><b>${inr(r.monthly_revenue)}</b><span>est. monthly revenue</span></div>
          <div class="stat"><b>₹${Math.round(r.avg_rent)}/sq ft</b><span>rent (${inr(r.monthly_rent)}/month)</span></div>
          <div class="stat"><b>${r.competitor_count}</b><span>competitors in area</span></div>
          <div class="stat"><b>${pay}</b><span>estimated payback</span></div>
        </div>
        <div class="chips">${R.recommendations.slice(0, 5).map((x, i) => `<span class="chip" data-i="${i}">#${x.rank} ${esc(x.area)}</span>`).join('')}</div>
      </div>
      <div class="why">
        <h4 style="margin-top:0">Top reasons</h4>${why}
        <div class="robust"><b>Robustness:</b> ranks #1 in <b>${(rb * 100).toFixed(0)}%</b> and top-3 in <b>${(r.robust_top3 * 100).toFixed(0)}%</b> of 500 randomly re-weighted scenarios.
          ${rb >= 0.6 ? '<span class="pill g">Clear winner</span>' : rb >= 0.25 ? '<span class="pill a">Close call</span>' : '<span class="pill r">Not a stable #1</span>'}</div>
      </div>`;
    $('hero').querySelectorAll('.chip').forEach(c => c.onclick = () => pick(+c.dataset.i));
  }

  function renderKpis() {
    const k = S.kpis, cv = R.coverage, f = S.forecast;
    const items = [
      ['Customers', k.customers.toLocaleString('en-IN'), `${k.areas_covered} localities`],
      ['Revenue in file', inr(k.revenue), `avg ${inr(k.avg_spend)} per customer`],
      [`Beyond ${R.radius} km of a store`, (cv.unserved_share * 100).toFixed(0) + '%', `${cv.unserved_customers.toLocaleString('en-IN')} customers · ${(cv.unserved_revenue_share * 100).toFixed(0)}% of spend`],
      ['Revenue trend', f ? `${f.monthly_growth_pct >= 0 ? '+' : ''}${f.monthly_growth_pct.toFixed(1)}%/mo` : 'n/a', f ? `peak ${f.peak_month}` : 'add a Sales sheet'],
    ];
    $('kpis').innerHTML = items.map(([a, b, c]) => `<div class="kpi"><span>${a}</span><b>${b}</b><small>${c}</small></div>`).join('');
  }

  function renderTable() {
    const pill = v => v >= 0.6 ? 'g' : v >= 0.25 ? 'a' : 'r';
    const rows = R.recommendations.map((r, i) => `<tr data-i="${i}" class="${i === sel ? 'sel' : ''}">
      <td><b>${r.rank}</b></td><td><b>${esc(r.area)}</b></td>
      <td class="n"><div style="display:flex;gap:8px;align-items:center;justify-content:flex-end"><b>${r.score.toFixed(0)}</b><div class="bar" style="width:70px"><i style="width:${r.score}%"></i></div></div></td>
      <td class="n"><span class="pill ${pill(r.robust_top3)}">${(r.robust_top3 * 100).toFixed(0)}% top-3</span></td>
      <td class="n">${r.catchment_customers.toLocaleString('en-IN')}</td><td class="n">${r.unserved_customers.toLocaleString('en-IN')}</td>
      <td class="n">₹${Math.round(r.avg_rent)}</td><td class="n">${r.competitor_count}</td><td class="n">${r.dist_to_store_km.toFixed(1)} km</td>
      <td class="n">${inr(r.monthly_revenue)}</td><td class="n">${r.payback_months ? r.payback_months.toFixed(0) + ' mo' : 'n/a'}</td></tr>`).join('');
    $('rankTbl').innerHTML = `<thead><tr><th>#</th><th>Locality</th><th class="n">Score</th><th class="n">Stability</th><th class="n">Customers nearby</th><th class="n">Unserved</th><th class="n">Rent /sq ft</th><th class="n">Rivals</th><th class="n">To nearest store</th><th class="n">Est. revenue /mo</th><th class="n">Payback</th></tr></thead><tbody>${rows}</tbody>`;
    $('rankTbl').querySelectorAll('tbody tr').forEach(tr => tr.onclick = () => { pick(+tr.dataset.i); window.scrollTo({ top: 0, behavior: 'smooth' }); });
  }
  function highlightRow() { $('rankTbl').querySelectorAll('tbody tr').forEach((tr, i) => tr.classList.toggle('sel', i === sel)); }

  boot();
})();
