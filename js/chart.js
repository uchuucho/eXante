let chartInstance = null;

const todayPlugin = {
  id: 'todayLine',
  afterDraw(chart) {
    const { ctx, scales:{x,y} } = chart;
    const d = mineralData?.[currentMineral];
    if (!d || !d.histLabels.length) return;
    const xPos = x.getPixelForValue(d.histLabels.length - 1);
    ctx.save();
    ctx.strokeStyle = 'rgba(255,255,255,0.18)';
    ctx.lineWidth = 1; ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.moveTo(xPos, y.top); ctx.lineTo(xPos, y.bottom); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = 'rgba(255,255,255,0.35)';
    ctx.font = "9px 'DM Mono',monospace";
    ctx.fillText('today', xPos+5, y.top+13);
    ctx.restore();
  }
};

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1,3), 16);
  const g = parseInt(hex.slice(3,5), 16);
  const b = parseInt(hex.slice(5,7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function buildDatasets(d, adjP50, adjP10, adjP90, hasShock, color) {
  const hLen   = d.histValues.length;
  const bridge = { x:hLen-1, y:d.histValues[hLen-1] };

  return [
    { label:'History',
      data: d.histValues.map((y,i) => ({ x:i, y })),
      borderColor:'#7d8fa0', borderWidth:2,
      pointRadius:0, tension:0.4, fill:false },
    { label:'Band high',
      data: [bridge, ...adjP90.map((y,i) => ({ x:hLen+i, y }))],
      borderColor:'transparent',
      backgroundColor: hexToRgba(color, 0.12), fill:'+1',
      pointRadius:0, tension:0.4 },
    { label:'Band low',
      data: [bridge, ...adjP10.map((y,i) => ({ x:hLen+i, y }))],
      borderColor:'transparent',
      backgroundColor: hexToRgba(color, 0.12), fill:false,
      pointRadius:0, tension:0.4 },
    { label:'Original forecast',
      data: [bridge, ...d.p50.map((y,i) => ({ x:hLen+i, y }))],
      borderColor: hasShock ? hexToRgba(color, 0.35) : 'transparent',
      borderWidth:1.5, borderDash:[5,4], pointRadius:0, tension:0.4, fill:false },
    { label:'Forecast (p50)',
      data: [bridge, ...adjP50.map((y,i) => ({ x:hLen+i, y }))],
      borderColor: color, borderWidth:2.5,
      pointRadius: ctx => ctx.dataIndex===0 ? 0 : 4,
      pointBackgroundColor: color,
      pointBorderColor:'#0a0e14', pointBorderWidth:1.5,
      tension:0.4, fill:false },
  ];
}

function renderChart(d, adjP50, adjP10, adjP90, hasShock, color) {
  const allLabels = [...d.histLabels, ...d.fcLabels];
  const allFull   = [...d.histFullLabels, ...d.fcFullLabels];
  const hLen      = d.histValues.length;
  const datasets  = buildDatasets(d, adjP50, adjP10, adjP90, hasShock, color);

  const allVals = [...d.histValues, ...adjP50, ...adjP10, ...adjP90].filter(v => v > 0 && isFinite(v));
  const yMin = Math.min(...allVals);
  const yMax = Math.max(...allVals);
  const pad  = (yMax - yMin) * 0.22;

  if (chartInstance) chartInstance.destroy();

  const canvas = document.getElementById('mainChart');

  chartInstance = new Chart(canvas, {
    type: 'line',
    data: { labels: allLabels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration:300, easing:'easeInOutQuart' },
      interaction: { mode:'index', intersect:false },
      onHover(_, els) {
        if (!els.length) return;
        const xVal = Math.round(els[0].parsed.x);
        if (xVal < hLen) {
          setDataBar(allFull[xVal], d.histValues[xVal], null, null, d.unit);
        } else {
          const fi = xVal - hLen;
          setDataBar(
            allFull[xVal],
            adjP50[fi] ?? null,
            adjP10[fi] ?? null,
            adjP90[fi] ?? null,
            d.unit
          );
        }
      },
      plugins: {
        legend: { display:false },
        tooltip: {
          enabled: true,
          backgroundColor:'#0d1724',
          borderColor: hexToRgba(color, 0.35),
          borderWidth:1,
          titleColor: color,
          bodyColor:'#dde6f0',
          padding:12,
          caretSize:5,
          callbacks: {
            title: items => allFull[items[0].parsed.x] ?? allLabels[items[0].parsed.x],
            label: item => {
              if (['Band high','Band low'].includes(item.dataset.label)) return null;
              return `  ${item.dataset.label}: ${Math.round(item.parsed.y).toLocaleString('en-US')} ${d.unit}`;
            },
          },
          filter: item => !['Band high','Band low'].includes(item.dataset.label),
        }
      },
      scales: {
        x: {
          type:'linear',
          grid: { color:'rgba(255,255,255,0.035)', drawBorder:false },
          ticks: {
            color:'#4a5a72',
            font:{ family:"'DM Mono',monospace", size:10 },
            maxRotation:0, autoSkip:true, maxTicksLimit:14,
            callback: v => allLabels[Math.round(v)] ?? '',
          },
          border: { display:false },
          min:0, max:allLabels.length-1,
        },
        y: {
          grid: { color:'rgba(255,255,255,0.04)', drawBorder:false },
          ticks: {
            color:'#4a5a72',
            font:{ family:"'DM Mono',monospace", size:10 },
            callback: v => {
              if (v >= 1_000_000) return (v/1_000_000).toFixed(1)+'M';
              if (v >= 1_000)     return (v/1_000).toFixed(0)+'k';
              return v;
            },
            maxTicksLimit: 7,
          },
          border: { display:false },
          min: Math.max(0, yMin - pad),
          max: yMax + pad,
        }
      }
    },
    plugins: [todayPlugin],
  });

  canvas.onmouseleave = () => {
    setDataBar(
      allFull[allFull.length-1],
      adjP50[adjP50.length-1],
      adjP10[adjP10.length-1],
      adjP90[adjP90.length-1],
      d.unit
    );
  };
}