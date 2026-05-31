function setDataBar(fullLabel, p50, p10, p90, unit) {
  document.getElementById('barMonth').textContent = fullLabel ?? '—';
  document.getElementById('barP50').textContent   = p50 !== null ? Math.round(p50).toLocaleString('en-US') : '—';
  document.getElementById('barP10').textContent   = p10 !== null ? Math.round(p10).toLocaleString('en-US') : '—';
  document.getElementById('barP90').textContent   = p90 !== null ? Math.round(p90).toLocaleString('en-US') : '—';
  ['barUnit','barUnit2','barUnit3'].forEach(id => document.getElementById(id).textContent = unit);
}

function updateDataBar(d, adjP50, adjP10, adjP90) {
  setDataBar(
    d.fcFullLabels[d.fcFullLabels.length-1] ?? '—',
    adjP50[adjP50.length-1],
    adjP10[adjP10.length-1],
    adjP90[adjP90.length-1],
    d.unit
  );
}

function updateStats(d, adjP50, adjP90) {
  const exp   = Math.round(adjP50[adjP50.length-1]);
  const worst = Math.round(adjP90[adjP90.length-1]);
  const pct   = (((exp - d.spotRaw) / d.spotRaw)*100).toFixed(1);
  const color = pct>=0 ? 'var(--accent)' : 'var(--red)';
  document.getElementById('statSpot').textContent     = d.spot;
  document.getElementById('statUnit').textContent     = d.unit;
  document.getElementById('statExpected').textContent = exp.toLocaleString();
  document.getElementById('statExpected').style.color = color;
  document.getElementById('statDelta').textContent    = (pct>=0?'+':'')+pct+'%';
  document.getElementById('statDelta').style.color    = color;
  document.getElementById('statWorst').textContent    = worst.toLocaleString();
}

function updateRecommendation(rec, mineralKey) {
  const offset = 138.2 - (rec.pct/100)*138.2;
  document.getElementById('rightMineralLabel').textContent      = mineralKey.toUpperCase();
  document.getElementById('recAction').textContent              = rec.action;
  document.getElementById('recAction').style.color              = rec.color;
  document.getElementById('recSub').textContent                 = rec.sub;
  document.getElementById('recDesc').textContent                = rec.desc;
  document.getElementById('recPct').textContent                 = rec.pct+'%';
  document.getElementById('recPct').style.color                 = rec.color;
  document.getElementById('recRingFill').style.stroke           = rec.color;
  document.getElementById('recRingFill').style.strokeDashoffset = offset;
}

function updateDrivers(d) {
  const el = document.getElementById('driverChips');
  if (!el) return;
  if (!d.drivers || !d.drivers.length) {
    el.innerHTML = '<span style="font-size:10px;color:var(--muted)">No significant drivers</span>';
    return;
  }
  el.innerHTML = d.drivers.map(dr => `<span class="driver-chip">${dr}</span>`).join('');
}

function updateClock() {
  document.getElementById('liveClock').textContent =
    new Date().toUTCString().slice(0,25)+' UTC';
}