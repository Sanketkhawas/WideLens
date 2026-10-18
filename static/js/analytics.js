/* Chart.js charts */
window.WLCharts = (function () {
  const C = { blue: '#2563EB', green: '#10B981', amber: '#F59E0B', dark: '#111827', grey: '#CBD5E1', red: '#EF4444', purple: '#8B5CF6', teal: '#14B8A6' };
  const FACTOR_COLORS = { demand: '#2563EB', gap: '#10B981', spend: '#8B5CF6', competition: '#F59E0B', rent: '#14B8A6', population: '#94A3B8' };
  Chart.defaults.font.family = '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif';
  Chart.defaults.font.size = 11;
  Chart.defaults.color = '#6B7280';
  const inrShort = v => v >= 1e7 ? (v / 1e7).toFixed(1) + ' Cr' : v >= 1e5 ? (v / 1e5).toFixed(1) + ' L' : v >= 1e3 ? (v / 1e3).toFixed(0) + 'k' : v;
  const charts = {};
  function make(id, cfg) { if (charts[id]) charts[id].destroy(); charts[id] = new Chart(document.getElementById(id), cfg); return charts[id]; }
  const noGrid = { grid: { display: false } };

  function rank(recs, labels) {
    const top = recs.slice(0, 8);
    make('rankChart', {
      type: 'bar',
      data: { labels: top.map(r => `#${r.rank} ${r.area}`),
        datasets: Object.keys(labels).map(k => ({ label: labels[k], data: top.map(r => +r['c_' + k].toFixed(1)), backgroundColor: FACTOR_COLORS[k], borderWidth: 0 })) },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false,
        scales: { x: { stacked: true, max: 100, title: { display: true, text: 'Expansion score' } }, y: { stacked: true, ...noGrid } },
        plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, boxHeight: 10 } } } }
    });
  }

  function forecast(S) {
    const f = S.forecast, el = document.getElementById('fcNote');
    if (!f) { el.textContent = 'Add a Sales sheet to see the revenue trend and forecast.'; return; }
    const H = f.hist_labels, F = f.f_labels, pad = n => Array(n).fill(null);
    const labels = H.concat(F);
    const joined = pad(H.length - 1).concat([f.hist[f.hist.length - 1]], f.forecast);
    make('fcChart', {
      type: 'line',
      data: { labels, datasets: [
        { label: 'Actual', data: f.hist.concat(pad(F.length)), borderColor: C.blue, backgroundColor: C.blue, tension: .3, pointRadius: 2 },
        { label: 'Forecast', data: joined, borderColor: C.amber, borderDash: [6, 4], backgroundColor: C.amber, tension: .3, pointRadius: 2 },
        { label: 'Upper (80%)', data: pad(H.length).concat(f.upper), borderWidth: 0, pointRadius: 0, backgroundColor: 'rgba(245,158,11,.18)', fill: '+1' },
        { label: 'Lower (80%)', data: pad(H.length).concat(f.lower), borderWidth: 0, pointRadius: 0, fill: false }] },
      options: { responsive: true, maintainAspectRatio: false, interaction: { mode: 'index', intersect: false },
        scales: { y: { ticks: { callback: v => '₹' + inrShort(v) } }, x: { ...noGrid, ticks: { maxTicksLimit: 10 } } },
        plugins: { legend: { labels: { boxWidth: 10, filter: i => !i.text.includes('Upper') && !i.text.includes('Lower') } },
          tooltip: { callbacks: { label: c => c.raw == null ? null : `${c.dataset.label}: ₹${Math.round(c.raw).toLocaleString('en-IN')}` } } } }
    });
    el.textContent = `Trend ${f.monthly_growth_pct >= 0 ? '+' : ''}${f.monthly_growth_pct.toFixed(1)}%/month with seasonality; in-sample error ≈ ${f.mape.toFixed(0)}% MAPE. Shaded band = 80% range. Expected peak: ${f.peak_month}.`;
  }

  function areas(S) {
    const storeAreas = new Set(S.stores.map(s => s.area));
    make('areaChart', {
      type: 'bar',
      data: { labels: S.areas.labels, datasets: [{ data: S.areas.revenue, backgroundColor: S.areas.labels.map(a => storeAreas.has(a) ? C.dark : C.blue), borderRadius: 4 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false },
        tooltip: { callbacks: { label: c => `₹${c.raw.toLocaleString('en-IN')} · ${S.areas.customers[c.dataIndex]} customers` } } },
        scales: { y: { ticks: { callback: v => '₹' + inrShort(v) } }, x: { ...noGrid, ticks: { maxRotation: 55, minRotation: 55 } } } }
    });
  }

  function segments(S) {
    const col = [C.green, C.blue, C.amber, C.grey];
    make('segChart', { type: 'doughnut',
      data: { labels: S.segments.labels, datasets: [{ data: S.segments.revenue, backgroundColor: col, borderWidth: 2, borderColor: '#fff' }] },
      options: { responsive: true, maintainAspectRatio: false, cutout: '62%', plugins: { legend: { position: 'right', labels: { boxWidth: 10 } },
        tooltip: { callbacks: { label: c => `${c.label}: ₹${inrShort(c.raw)} revenue` } } } } });
    const rows = S.segments.labels.map((l, i) => `<tr><td>${l}</td><td class="n">${S.segments.customers[i].toLocaleString('en-IN')}</td><td class="n">₹${S.segments.avg_spend[i].toLocaleString('en-IN')}</td><td class="n">${S.segments.avg_freq[i]}</td></tr>`).join('');
    document.getElementById('segTbl').innerHTML = `<table class="tbl"><tr><th>Segment</th><th class="n">Customers</th><th class="n">Avg spend</th><th class="n">Orders</th></tr>${rows}</table>`;
  }

  function categories(S) {
    if (!S.categories) return;
    make('catChart', { type: 'bar',
      data: { labels: S.categories.labels, datasets: [{ data: S.categories.revenue, backgroundColor: C.blue, borderRadius: 4 }] },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } },
        scales: { x: { ticks: { maxTicksLimit: 5, maxRotation: 0, callback: v => '₹' + inrShort(v) } }, y: noGrid } } });
  }

  function age(S) {
    make('ageChart', { type: 'bar',
      data: { labels: S.demo.age_labels, datasets: [{ data: S.demo.age_values, backgroundColor: C.blue, borderRadius: 4 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: noGrid } } });
    const g = S.demo, tot = g.gender_values.reduce((a, b) => a + b, 0);
    document.getElementById('genderNote').textContent = g.gender_labels.map((l, i) => `${l} ${(100 * g.gender_values[i] / tot).toFixed(0)}%`).join(' · ');
  }
  return { rank, forecast, areas, segments, categories, age };
})();
