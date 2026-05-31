let currentMineral = 'lithium';
let activeShocks   = new Set();

function redraw() {
  const d = mineralData[currentMineral];
  if (!d) return;
  const { p50, p10, p90 } = getAdjustedForecast(d, activeShocks);
  const rec      = computeRecommendation(currentMineral, d.spotRaw, p50, p10, p90, activeShocks, d.decision);
  const hasShock = activeShocks.size > 0;
  renderChart(d, p50, p10, p90, hasShock, d.decision.color);
  updateStats(d, p50, p90);
  updateDataBar(d, p50, p10, p90);
  updateRecommendation(rec, currentMineral);
  updateDrivers(d);
}

function selectMineral(key, btn) {
  currentMineral = key;
  document.querySelectorAll('.mineral-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  redraw();
}

function toggleShock(key, btn) {
  if (activeShocks.has(key)) { activeShocks.delete(key); btn.classList.remove('active'); }
  else                       { activeShocks.add(key);    btn.classList.add('active');    }
  redraw();
}

function resetShocks() {
  activeShocks.clear();
  document.querySelectorAll('.shock-pill').forEach(b => b.classList.remove('active'));
  redraw();
}

updateClock();
setInterval(updateClock, 1000);

loadMineralData()
  .then(() => { redraw(); document.getElementById('loadingOverlay').style.display = 'none'; })
  .catch(err => {
    console.error(err);
    document.getElementById('loadingOverlay').innerHTML = `
      <div style="color:#f04f5a;font-family:'DM Mono',monospace;font-size:12px;text-align:center;padding:24px">
        ⚠ Could not load ev_minerals_results.json<br><br>
        Run the pipeline first:<br>
        <span style="color:#5a6a7e">python3 sybilion_ev_minerals.py</span>
      </div>`;
  });