'use strict';

window.ObservatoryContributorData = fetch('contributor_populations.json').then(r => {
  if (!r.ok) throw Error('Contributor data unavailable');
  return r.json();
}).then(d => {
  if (d.schema_version !== 1 || d.annual.length !== 16 || d.monthly.length !== 192 || d.rolling12.length !== 181) throw Error('Incomplete contributor series');
  for (const r of [d.study, ...d.annual, ...d.monthly, ...d.rolling12]) {
    if (!Number.isSafeInteger(r.papers) || r.papers <= 0) throw Error('Invalid paper count');
    for (const m of ['names','ids']) {
      const v = r[m], all = d.study[m].authors;
      if (!Number.isSafeInteger(v.authors) || v.authors <= 0 || v.authors > all) throw Error('Invalid contributor count');
      if (Math.abs(v.papers_per_active_contributor - r.papers/v.authors) > 1e-10 || Math.abs(v.papers_per_study_contributor - r.papers/all) > 1e-10) throw Error('Invalid contributor denominator');
      for (const measure of ['fractional','coauthored']) {
        const t = v[measure], total = measure==='fractional' ? r.papers : v.coauthored_participations;
        if (!Number.isFinite(t.share) || t.share < .1-1e-10 || t.share > 1 || t.contributors !== v.authors || Math.abs(t.group_mass-v.authors/10)>1e-9) throw Error('Invalid decile membership');
        if (Math.abs(t.total_output-total)>1e-7 || Math.abs(t.top_output/total-t.share)>1e-10 || Math.abs(t.top_mean/t.other90_mean-t.mean_ratio)>1e-9) throw Error('Invalid decile output');
      }
    }
  }
  return d;
});

(() => {
  const charts = window.ObservatoryCharts;
  const el = id => document.getElementById(id);
  const fmt = new Intl.NumberFormat('en-US', {maximumFractionDigits:3});
  const num = n => n === null || n === undefined ? '—' : fmt.format(n);
  const pct = n => (100*n).toFixed(2)+'%';
  const pp = (a,b) => ((b-a)>=0?'+':'')+(100*(b-a)).toFixed(2)+' percentage points';
  let data, period='annual', measure='fractional';
  const identity = [
    {key:'ids',label:'OpenAlex author IDs · resolved',color:'#365bc9'},
    {key:'names',label:'Distinct names · no extra merging',color:'#a76519'}
  ];
  const rankingNote = 'Rank contributor keys with at least one retained paper in each window. The top group has exactly 10% of the population weight. At the cutoff, tied keys share the remaining membership weight equally. Rankings are recomputed for each window, identity definition and selected measure.';
  function figure(rows, config, i) {
    const titleId=`decile-chart-${i}-title`, captionId=`decile-chart-${i}-caption`;
    const windowText=period==='annual'?'Each point is a full calendar year.':period==='monthly'?'Each point is one calendar month.':'Each point covers its month and the preceding 11 months; adjacent windows overlap.';
    return `<figure class="explained-chart" aria-labelledby="${titleId}" aria-describedby="${captionId}"><div class="chart-heading"><h3 id="${titleId}">${i}. ${config.title}</h3><p>${charts.date(rows[0].period)}–${charts.date(rows.at(-1).period)} · ${measure==='fractional'?'fractional paper credit':'coauthored-paper counts'}</p></div>${charts.legend(config.series,rows,config.unit)}${charts.lineChart(rows,config.series,{...config,mode:period})}<figcaption class="chart-explanation" id="${captionId}"><p><strong>What it shows.</strong> ${config.shows}</p><p><strong>How it was obtained.</strong> ${config.method}</p><p><strong>Time window and ranking.</strong> ${windowText} ${rankingNote}</p><p class="chart-source">Source: the same paired arXiv-linked Mathematics papers as the P/A analysis; OpenAlex snapshot frozen 16 September 2026. Dates come from arXiv IDs. Fractional scores are rounded to 12 decimal places only to identify ties. <a href="contributor_populations.json" download>Exact aggregates and cutoff details</a>.</p></figcaption></figure>`;
  }
  function render() {
    if (!data) return;
    const rows=data[period], latest=rows.at(-1), study=data.study;
    const isFractional=measure==='fractional';
    const unit=isFractional?'fractional paper credit':'coauthored papers';
    const shares=identity.map(s=>({...s,value:r=>100*r[s.key][measure].share}));
    shares.push({label:'Equal-output benchmark',color:'#8792a6',value:()=>10});
    el('decile-share').innerHTML=figure(rows,{
      title:isFractional?'Share of paper credit held by the most prolific 10%':'Share of coauthored-paper participations held by the most prolific 10%',
      unit:'%',unitLabel:isFractional?'percent of total fractional paper credit':'percent of all key–paper participations',series:shares,
      shows:`The share of ${isFractional?'all fractional paper credit':'all coauthored-paper participations'} associated with the highest-output tenth of observed contributor keys. Higher shares mean greater concentration. If every key had equal output, the top tenth would hold 10%.`,
      method:isFractional?'Give each slot on a k-slot byline 1/k of a paper and add credit by contributor key. Rank keys by that credit. Divide credit assigned to the top-decile group by total credit, which equals the retained paper count P.':'Count one coauthored paper for each distinct key on its byline; repeated raw-name slots count once per paper. Rank keys by these counts. Divide the top group’s counts by J, the sum of all key–paper participations. This is not a share of distinct papers: one collaborative paper contributes to multiple keys.'
    },1);
    const ratios=identity.map(s=>({...s,value:r=>r[s.key][measure].mean_ratio}));
    ratios.push({label:'Equal-output benchmark',color:'#8792a6',value:()=>1});
    el('decile-ratio').innerHTML=figure(rows,{
      title:'Mean output of the top 10% relative to the other 90%',unit:'times the other 90% mean',series:ratios,
      shows:`How many times more ${unit} the average member of the top-decile group has than the average member of the other 90%. A value of 1 means equal mean output. This compares groups of observed keys, not verified people.`,
      method:'Divide top-decile output by 0.1 × A; divide the remaining output by 0.9 × A. Take the ratio of those two means. Equivalently, if the top-decile share is S, the ratio is 9S/(1−S). Boundary ties use the same proportional membership weights as graph 1.'
    },2);
    const a=data.annual[0], b=data.annual.at(-1);
    el('decile-findings').innerHTML=`<p class="eyebrow">ANNUAL COMPARISON · ${isFractional?'FRACTIONAL CREDIT':'COAUTHORED PAPERS'}</p><h2>What the selected measure shows</h2>${identity.map(s=>`<p class="body-copy">Using ${s.key==='ids'?'OpenAlex author IDs':'distinct names'}, the annual top-decile share changes from <strong>${pct(a[s.key][measure].share)} in ${a.period} to ${pct(b[s.key][measure].share)} in ${b.period}</strong> (${pp(a[s.key][measure].share,b[s.key][measure].share)}). In ${b.period}, the top tenth’s mean output is <strong>${num(b[s.key][measure].mean_ratio)} times</strong> the other 90% mean.</p>`).join('')}<p class="chart-note">These annual findings stay fixed when you change the graph’s time window. Switching the output measure recalculates both the ranking and its share. Annual changes describe concentration in this recorded population; they do not establish an effect of AI.</p>`;
    el('decile-study').innerHTML=`<p class="eyebrow">CUMULATIVE RANKING · JANUARY 2010–DECEMBER 2025</p><h2>The most prolific 10% over the whole study</h2><p class="body-copy">Rank all ${num(study.names.authors)} distinct names or ${num(study.ids.authors)} OpenAlex IDs by their accumulated ${unit} on ${num(study.papers)} retained papers. This is a separate ranking over all sixteen years, not the average of the annual shares.</p><div class="table-scroll"><table><thead><tr><th scope="col">Identity definition</th><th scope="col">Top 10% share</th><th scope="col">Top 10% mean</th><th scope="col">Other 90% mean</th><th scope="col">Ratio of means</th></tr></thead><tbody>${identity.map(s=>{const t=study[s.key][measure];return `<tr><th scope="row">${s.key==='ids'?'OpenAlex IDs':'Distinct names'}</th><td>${pct(t.share)}</td><td>${num(t.top_mean)}</td><td>${num(t.other90_mean)}</td><td>${num(t.mean_ratio)}×</td></tr>`;}).join('')}</tbody></table></div><p class="chart-note">Means are cumulative ${unit} per weighted contributor key, not annual rates. Longer observed participation increases the opportunity to accumulate output. The full-period decile is not a cohort tracked year by year.</p>`;
    el('decile-cutoffs').innerHTML=`<h3>Cutoff details for ${charts.escape(charts.windowLabel(latest.period,period))}</h3><p class="body-copy">A cutoff does not select every tied key in full. Each boundary key gets the same weight, so the top group always totals exactly 10%.</p><div class="table-scroll"><table><thead><tr><th scope="col">Identity</th><th scope="col">Active keys</th><th scope="col">Top-group weight</th><th scope="col">Output cutoff</th><th scope="col">Keys above cutoff</th><th scope="col">Tied keys</th><th scope="col">Weight per tied key</th></tr></thead><tbody>${identity.map(s=>{const t=latest[s.key][measure];return `<tr><th scope="row">${s.key==='ids'?'OpenAlex IDs':'Distinct names'}</th><td>${num(t.contributors)}</td><td>${num(t.group_mass)}</td><td>${num(t.threshold)}</td><td>${num(t.strictly_above)}</td><td>${num(t.boundary_ties)}</td><td>${pct(t.boundary_weight)}</td></tr>`;}).join('')}</tbody></table></div><p class="chart-note">Cutoff units: ${unit} in the selected window. Displayed values are rounded; downloads retain the calculation precision.</p>`;
    el('decile-values').innerHTML=rows.map(r=>`<tr><th scope="row">${charts.escape(charts.windowLabel(r.period,period))}</th><td>${num(r.papers)}</td>${['ids','names'].map(m=>{const t=r[m][measure];return `<td>${num(r[m].authors)}</td><td>${pct(t.share)}</td><td>${num(t.top_mean)}</td><td>${num(t.other90_mean)}</td>`;}).join('')}</tr>`).join('');
    document.querySelectorAll('[data-decile-period]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.decilePeriod===period)));
    document.querySelectorAll('[data-decile-measure]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.decileMeasure===measure)));
    el('decile-table-unit').textContent=`Selected output measure: ${unit}. Means are per weighted contributor key within each window.`;
  }
  document.querySelectorAll('[data-decile-period]').forEach(b=>b.addEventListener('click',()=>{period=b.dataset.decilePeriod;render();}));
  document.querySelectorAll('[data-decile-measure]').forEach(b=>b.addEventListener('click',()=>{measure=b.dataset.decileMeasure;render();}));
  window.ObservatoryContributorData.then(d=>{data=d;render();}).catch(()=>{el('decile-error').hidden=false;});
})();
