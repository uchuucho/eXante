let mineralData = null;

async function loadMineralData() {
  const res  = await fetch('data/ev_minerals_results.json');
  const json = await res.json();
  mineralData = mapSybilionOutput(json);
  return mineralData;
}

const CODE_TO_KEY = {
  PLITH:'lithium', PCOBA:'cobalt', PNICK:'nickel', PMANGELE:'manganese'
};

function buildDateLabels(dateStrings) {
  return dateStrings.map(d => {
    const dt = new Date(d + 'T00:00:00');
    return dt.toLocaleString('default', { month: 'short', year: '2-digit' });
  });
}

function buildFullDateLabels(dateStrings) {
  return dateStrings.map(d => {
    const dt = new Date(d + 'T00:00:00');
    return dt.toLocaleString('default', { month: 'long', year: 'numeric' });
  });
}

function mapSybilionOutput(json) {
  const result = {};
  for (const [code, key] of Object.entries(CODE_TO_KEY)) {
    const entry = json[code];
    if (!entry) continue;

    const dates      = entry.forecast_dates ?? [];
    const p50        = entry.p50_base ?? [];
    const p10        = (entry.p10_base ?? []).map(v => Math.max(0, v));
    const p90        = entry.p90_base ?? [];
    const histValues = entry.history_values ?? [];
    const histDates  = entry.history_dates  ?? [];
    const spot       = entry.spot ?? p50[0] ?? 0;

    const signals = entry.external_signals?.data ?? {};
    const drivers = Object.values(signals)
      .filter(s => (s.importance?.overall?.max ?? 0) > 50)
      .sort((a, b) => (b.importance?.overall?.max ?? 0) - (a.importance?.overall?.max ?? 0))
      .slice(0, 4)
      .map(s => s.driver_name);

    const decision = entry.decision_baseline ?? {
      action:'—', sub:'—', pct:0,
      color:'var(--accent)', desc:'—',
      mu:0, sigma:0, snr:0, utility:0
    };

    const colorMap = {
      'var(--accent)': '#00c896',
      'var(--amber)':  '#e8a842',
      'var(--red)':    '#f04f5a',
    };
    decision.color = colorMap[decision.color] ?? decision.color;

    result[key] = {
      label:          entry.name?.toUpperCase() ?? key.toUpperCase(),
      unit:           entry.unit ?? '',
      spot:           Math.round(spot).toLocaleString('en-US'),
      spotRaw:        spot,
      histDates,
      histValues,
      histLabels:     buildDateLabels(histDates),
      histFullLabels: buildFullDateLabels(histDates),
      fcDates:        dates,
      fcLabels:       buildDateLabels(dates),
      fcFullLabels:   buildFullDateLabels(dates),
      p50, p10, p90,
      decision,
      scenario_grid:  entry.scenario_grid ?? {},
      drivers,
    };
  }
  return result;
}