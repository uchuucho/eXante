const SCENARIO_SHOCKS = {
  geo: { G:0.25, P:0.0,  M:0.0  },
  pol: { G:0.0,  P:0.25, M:0.0  },
  min: { G:0.0,  P:0.0,  M:0.25 },
};

const SCENARIO_LABELS = {
  geo:'Geopolitical', pol:'Policy change', min:'Mining issue'
};

function buildGridKey(G, P, M) {
  const fmt = v => (Math.round(v*4)/4 % 1 === 0)
    ? (Math.round(v*4)/4).toFixed(1)
    : String(Math.round(v*4)/4);
  return `G=${fmt(G)},P=${fmt(P)},M=${fmt(M)}`;
}

function getAdjustedForecast(d, activeShocks) {
  if (!activeShocks.size) return { p50:d.p50, p10:d.p10, p90:d.p90 };

  let G=0, P=0, M=0;
  for (const key of activeShocks) {
    const s = SCENARIO_SHOCKS[key];
    G = Math.min(1, G+s.G);
    P = Math.min(1, P+s.P);
    M = Math.min(1, M+s.M);
  }

  const gridKey = buildGridKey(G, P, M);
  const adjP50  = d.scenario_grid[gridKey];
  if (!adjP50) {
    console.warn('Grid key not found:', gridKey);
    return { p50:d.p50, p10:d.p10, p90:d.p90 };
  }

  const factor = adjP50.map((v,i) => d.p50[i] > 0 ? v / d.p50[i] : 1);
  return {
    p50: adjP50,
    p10: d.p10.map((v,i) => Math.max(0, Math.round(v * factor[i]))),
    p90: d.p90.map((v,i) => Math.round(v * factor[i])),
  };
}

function computeRecommendation(mineralKey, spotRaw, p50, p10, p90, activeShocks, decision) {
  if (!activeShocks.size && decision) return decision;

  const logReturns = p50.map(v => Math.log(Math.max(v,1)) - Math.log(Math.max(spotRaw,1)));
  const mu = logReturns.reduce((a,b) => a+b, 0);
  const spreads = p50.map((_,i) => (Math.log(Math.max(p90[i],1)) - Math.log(Math.max(p10[i],1))) / (2*1.96));
  const sigma = Math.sqrt(spreads.reduce((a,b) => a+b*b, 0));
  const snr = mu / Math.max(sigma, 1e-8);
  const highUncert = sigma > 0.4;
  const nShocks = activeShocks.size;

  let action, sub, basePct;
  if      (snr>=0.3 && !highUncert) { action='Buy now';     sub='Full allocation';       basePct=88; }
  else if (snr>=0.3 &&  highUncert) { action='Buy partial'; sub='Split across time';     basePct=65; }
  else if (snr>=0.0)                { action='Hold';        sub='Wait for better entry'; basePct=40; }
  else                              { action='Wait';        sub='Downtrend in progress'; basePct=20; }

  const conviction = Math.max(5, Math.round(basePct*(1-nShocks*0.12)));
  const colorMap = { 'Buy now':'#00c896','Buy partial':'#00c896','Hold':'#e8a842','Wait':'#f04f5a' };
  const retPct = (mu*100).toFixed(1), sigmaPct = (sigma*100).toFixed(1);
  const activeList = [...activeShocks].map(k => SCENARIO_LABELS[k]).join(', ');
  const shockStr = activeList ? ` Active: ${activeList}.` : '';

  let desc;
  if      (action==='Buy now')     desc=`Expected log return ${retPct}% with risk ${sigmaPct}%. Strong signal.${shockStr}`;
  else if (action==='Buy partial') desc=`Expected return ${retPct}% but uncertainty is wide (${sigmaPct}%). Stagger purchases.${shockStr}`;
  else if (action==='Hold')        desc=`Return signal is weak (${retPct}%). Hold and revisit in 4–6 weeks.${shockStr}`;
  else                             desc=`Negative expected return (${retPct}%). Wait for a clearer floor.${shockStr}`;

  return { action, sub, pct:conviction, color:colorMap[action], desc,
           mu:parseFloat(mu.toFixed(4)), sigma:parseFloat(sigma.toFixed(4)),
           snr:parseFloat(snr.toFixed(4)), utility:parseFloat((mu-0.5*sigma*sigma).toFixed(4)) };
}