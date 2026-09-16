'use strict';

window.ObservatoryCharts = (() => {
  const formatter = new Intl.NumberFormat('en-US', {maximumFractionDigits: 3});
  const escape = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const date = value => value.length === 4 ? value : new Date(value + '-01T00:00:00Z').toLocaleDateString('en-GB', {month:'short', year:'numeric', timeZone:'UTC'});
  const windowLabel = (value, mode) => {
    if (mode !== 'rolling12') return date(value);
    const end = new Date(value + '-01T00:00:00Z');
    end.setUTCMonth(end.getUTCMonth() - 11);
    return `${date(end.toISOString().slice(0, 7))}–${date(value)}`;
  };
  const windowNote = mode => ({
    monthly:'Each point represents one calendar month, assigned from the date in the arXiv ID.',
    annual:'Each point represents one full calendar year.',
    rolling12:'Each point includes its labelled month and the preceding 11 months. Adjacent windows overlap, and percentages use the summed counts within each window.'
  })[mode];
  function niceMax(value) {
    if (!(value > 0)) return 1;
    const power = 10 ** Math.floor(Math.log10(value));
    return [1, 2, 2.5, 5, 10].find(n => n * power >= value) * power;
  }
  function lineChart(rows, series, {title, unit, mode, maxY, unitLabel}) {
    const values = series.flatMap(s => rows.map(s.value)).filter(Number.isFinite);
    if (!values.length) return '<div class="spark-unavailable">No measured values available for this series.</div>';
    const top = maxY || niceMax(Math.max(...values));
    const w = 680, h = 160, pad = 8;
    const point = (v, i) => [pad + i * (w - 2 * pad) / Math.max(1, rows.length - 1), h - pad - v / top * (h - 2 * pad)];
    const format = v => formatter.format(v) + (unit === '%' ? '%' : '');
    const grid = [0, .25, .5, .75, 1].map(f => {
      const y = point(top * f, 0)[1];
      return `<line x1="${pad}" y1="${y}" x2="${w-pad}" y2="${y}" stroke="#dce3ed" stroke-width="1" vector-effect="non-scaling-stroke"/>`;
    }).join('');
    const paths = series.map((s, index) => {
      let open = false;
      const path = rows.map((r, i) => {
        const value = s.value(r);
        if (!Number.isFinite(value)) { open = false; return ''; }
        const [x, y] = point(value, i), command = open ? 'L' : 'M';
        open = true;
        return `${command}${x},${y}`;
      }).join(' ');
      const markers = rows.map((r, i) => {
        const value = s.value(r);
        if (!Number.isFinite(value)) return '';
        const [x, y] = point(value, i);
        return `<circle cx="${x}" cy="${y}" r="3" fill="${s.color}" class="chart-point"><title>${escape(windowLabel(r.period, mode))} · ${escape(s.label)}: ${format(value)}${unit === '%' ? '' : ' ' + escape(unit)}</title></circle>`;
      }).join('');
      return `<path d="${path}" fill="none" stroke="${s.color}" stroke-width="2.5" ${index ? 'stroke-dasharray="7 5"' : ''} vector-effect="non-scaling-stroke"/>${markers}`;
    }).join('');
    const tickIndexes = [...new Set([0, Math.floor((rows.length - 1) / 2), rows.length - 1])];
    const ticks = tickIndexes.map((i, k) => `<span style="left:${i / Math.max(1, rows.length - 1) * 100}%;transform:translateX(${k === 0 ? '0' : k === tickIndexes.length - 1 ? '-100%' : '-50%'})">${date(rows[i].period)}</span>`).join('');
    const axisTitle = mode === 'rolling12' ? 'End of the 12-month window' : mode === 'annual' ? 'arXiv ID year' : 'arXiv ID month';
    return `<div class="chart-unit">Vertical axis: ${unitLabel ? escape(unitLabel) : unit === '%' ? 'percent of linked papers' : escape(unit)} · scale starts at zero</div><div class="chart-plot"><div class="chart-y-axis" aria-hidden="true">${[1, .75, .5, .25, 0].map(f => `<span>${format(top*f)}</span>`).join('')}</div><div class="chart-canvas"><svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none" role="img" aria-label="${escape(title)}. ${date(rows[0].period)} to ${date(rows.at(-1).period)}. Vertical scale 0 to ${format(top)}. Exact values are in the table below."><title>${escape(title)}</title>${grid}${paths}</svg><div class="chart-x-ticks" aria-hidden="true">${ticks}</div><div class="chart-x-label">${axisTitle}</div></div></div>`;
  }
  const legend = (series, rows, unit) => `<div class="chart-legend">${series.map((s, i) => `<span><i style="border-color:${s.color};border-top-style:${i ? 'dashed' : 'solid'}" aria-hidden="true"></i>${escape(s.label)} <strong>${formatter.format(s.value(rows.at(-1)))}${unit === '%' ? '%' : ''}</strong><small>latest window</small></span>`).join('')}</div>`;
  return {lineChart, legend, date, windowLabel, windowNote, escape};
})();
