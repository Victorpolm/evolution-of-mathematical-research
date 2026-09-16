'use strict';

(() => {
  let data;
  let aggregation = 'monthly';
  const charts = window.ObservatoryCharts;
  const number = new Intl.NumberFormat('en-US');
  const label = value => value.length === 4 ? value : new Date(value + '-01T00:00:00Z').toLocaleDateString('en-GB', {month:'short',year:'numeric',timeZone:'UTC'});
  const series = [
    {key:'papers', name:'Paper uploads recorded in the repository', color:'#365bc9', unit:'papers',
      explanation:'The number of distinct arXiv paper IDs listed in the project’s mathematics manifest for each time window. This is a different population from the OpenAlex coverage audit.',
      method:'Extract the year and month from each arXiv ID, remove duplicate IDs, and count IDs in each window. All 169,394 source IDs passed format and uniqueness checks; the 1,367 August 2026 IDs are excluded because that month is incomplete in this snapshot. The remaining 168,027 cover August 2023–July 2026. The ID list alone cannot verify completeness against all arXiv mathematics.'},
    {key:'contributors', name:'Distinct contributors on the repository’s papers', color:'#087f83', unit:'contributors',
      explanation:'This would count distinct coauthors with at least one paper in each window. The repository ID list contains no authors, so this quantity is unavailable; an empty graph does not mean zero contributors.',
      method:'An author table must first be linked to the same retained papers. For each window, count the union of author identities once, using both distinct-name and OpenAlex-ID approaches. For 12-month windows, recompute that union across the whole window rather than adding monthly author counts.'},
    {key:'papersPerContributor', name:'Papers per contributor on the same paper population', color:'#7555a7', unit:'papers per contributor',
      explanation:'This would compare paper production with the number of active contributors. It is unavailable because the denominator has not been measured for this repository population.',
      method:'Divide papers P by distinct contributors A in the same window and on exactly the same eligible paper set. P/A equals mean fractional credit only when all paper credit is allocated. With missing IDs, retain unallocated credit separately; do not substitute author counts from the smaller OpenAlex sample.'}
  ];

  function render() {
    if (!data) return;
    const rows = data[aggregation];
    document.querySelector('#period-note').textContent = charts.windowNote(aggregation);
    document.querySelectorAll('[data-period]').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.period === aggregation)));
    document.querySelector('#paper-spark-rows').innerHTML = series.map((s, index) => {
      const last = rows.at(-1)[s.key];
      const available = last !== null && Number.isFinite(last);
      const chartSeries=[{label:s.key==='papers'?'Recorded paper IDs':s.name,color:s.color,value:r=>r[s.key]}];
      const titleId=`manifest-chart-${index+1}-title`,captionId=`manifest-chart-${index+1}-caption`;
      return `<figure class="explained-chart" aria-labelledby="${titleId}" aria-describedby="${captionId}"><div class="chart-heading"><h3 id="${titleId}">${index+1}. ${s.name}</h3><p>${label(rows[0].period)}–${label(rows.at(-1).period)} · ${available?'observed counts':'data unavailable'}</p></div>${available?charts.legend(chartSeries,rows,s.unit)+charts.lineChart(rows,chartSeries,{title:s.name,unit:s.unit,mode:aggregation}):'<div class="spark-unavailable">Not measured: the repository manifest contains paper IDs only.</div>'}<figcaption id="${captionId}" class="chart-explanation"><p><strong>What it shows.</strong> ${s.explanation}</p><p><strong>${available?'How it was obtained.':'How it would be calculated.'}</strong> ${s.method}</p>${available?`<p><strong>Time window.</strong> ${charts.windowNote(aggregation)} Latest window: ${charts.windowLabel(rows.at(-1).period,aggregation)}.</p>`:''}<p class="chart-source">Source: repository mathematics ID manifest, pinned to 4 September 2026; counts computed 6 September 2026. <a href="papers_contributors.json" download>Download values and provenance</a>.</p></figcaption></figure>`;
    }).join('');
    const tbody = document.querySelector('#paper-values tbody');
    tbody.replaceChildren();
    for (const r of rows) {
      const tr = document.createElement('tr');
      for (const [i,value] of [label(r.period),r.papers,r.contributors,r.papersPerContributor].entries()) {
        const cell = document.createElement(i === 0 ? 'th' : 'td');
        if (i === 0) cell.scope = 'row';
        cell.textContent = value === null ? 'Unavailable' : typeof value === 'number' ? number.format(value) : value;
        tr.append(cell);
      }
      tbody.append(tr);
    }
  }

  document.querySelectorAll('[data-period]').forEach(b => b.addEventListener('click', () => { aggregation = b.dataset.period; render(); }));
  fetch('papers_contributors.json').then(r => { if (!r.ok) throw Error('Missing series'); return r.json(); }).then(result => {
    for (const key of ['monthly','rolling12','annual']) {
      if (!Array.isArray(result[key]) || !result[key].length) throw Error('Empty series');
      for (const r of result[key]) {
        if (!/^\d{4}(-\d{2})?$/.test(r.period) || !Number.isSafeInteger(r.papers) || r.papers < 0) throw Error('Invalid observation');
        for (const key of ['contributors','papersPerContributor']) if (r[key] !== null && (!Number.isFinite(r[key]) || r[key] < 0)) throw Error('Invalid contributor observation');
      }
    }
    data = result; render();
  }).catch(() => {
    document.querySelector('#paper-spark-rows').replaceChildren();
    document.querySelector('#paper-data-error').hidden = false;
  });
})();
