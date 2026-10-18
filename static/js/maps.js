/* Leaflet map: customer heat-map, existing stores, ranked candidate sites, catchment circle */
window.WLMap = (function () {
  let map, heat, group, circle, markers = [];
  const NAGPUR = [21.1300, 79.0800];

  function init(S) {
    map = L.map('map', { zoomControl: true }).setView(NAGPUR, 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18, attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    heat = L.heatLayer(S.heat, { radius: 12, blur: 16, maxZoom: 13, max: 3.0, minOpacity: 0.15,
      gradient: { 0.2: '#93C5FD', 0.5: '#2563EB', 0.8: '#F59E0B', 1: '#EF4444' } }).addTo(map);
    group = L.layerGroup().addTo(map);
    S.stores.forEach(s => {
      L.marker([s.latitude, s.longitude], { icon: pin('#111827', '■', 26) }).addTo(map)
        .bindTooltip(`<b>${s.store_name}</b><br>Existing store · ${s.area}`);
    });
    document.getElementById('tHeat').onchange = e => e.target.checked ? heat.addTo(map) : map.removeLayer(heat);
    document.getElementById('tCircle').onchange = e => { if (circle) e.target.checked ? circle.addTo(map) : map.removeLayer(circle); };
  }

  function pin(color, glyph, size) {
    return L.divIcon({ className: '', iconSize: [size, size], iconAnchor: [size / 2, size / 2],
      html: `<div style="width:${size}px;height:${size}px;border-radius:50%;background:${color};color:#fff;display:flex;align-items:center;justify-content:center;font:700 ${size * 0.5}px sans-serif;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.4)">${glyph}</div>` });
  }

  function showRecs(recs, radius, selected, onPick) {
    group.clearLayers(); markers = [];
    recs.slice(0, 6).forEach((r, i) => {
      const m = L.marker([r.latitude, r.longitude], { icon: pin(i === 0 ? '#10B981' : '#2563EB', r.rank, i === 0 ? 34 : 28), zIndexOffset: 500 - i })
        .addTo(group).bindTooltip(`<b>#${r.rank} ${r.area}</b><br>Score ${r.score.toFixed(0)}/100`);
      m.on('click', () => onPick(i));
      markers.push(m);
    });
    focus(recs[selected], radius);
  }

  function focus(r, radius) {
    if (!r) return;
    if (circle) map.removeLayer(circle);
    circle = L.circle([r.latitude, r.longitude], { radius: radius * 1000, color: '#10B981', weight: 2, fillColor: '#10B981', fillOpacity: 0.08 });
    if (document.getElementById('tCircle').checked) circle.addTo(map);
    map.flyTo([r.latitude, r.longitude], 12.5, { duration: 0.6 });
  }
  return { init, showRecs, focus };
})();
