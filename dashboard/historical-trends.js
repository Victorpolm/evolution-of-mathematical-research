'use strict';
(() => {
  const charts = window.ObservatoryCharts;
  const el = id => document.getElementById(id);
  const fmt = new Intl.NumberFormat('en-US', {maximumFractionDigits: 3});
  const num = n => n === null || n === undefined ? '—' : fmt.format(n);
  const pct = n => n === null ? '—' : (100*n).toFixed(2)+'%';
  const change = (a,b) => ((b/a-1)*100 >= 0 ? '+' : '')+((b/a-1)*100).toFixed(1)+'%';
  let data, populations, period = 'annual';
  const definition = [
    {label: 'OpenAlex author IDs · resolved', color:'#365bc9', value:r=>r.ids.papers_per_author},
    {label: 'Distinct names · no extra merging', color:'#a76519', value:r=>r.names.papers_per_author}
  ];
  function figure(rows, config, i) {
    const titleId = `historical-chart-${i}-title`, captionId = `historical-chart-${i}-caption`;
    const windowText = period === 'annual' ? 'One point per full calendar year.' : period === 'monthly' ? 'One point per calendar month.' : 'Each point covers its month and the preceding 11 months. Adjacent windows overlap.';
    return `<figure class="explained-chart" aria-labelledby="${titleId}" aria-describedby="${captionId}"><div class="chart-heading"><h3 id="${titleId}">${i}. ${config.title}</h3><p>${charts.date(rows[0].period)}–${charts.date(rows.at(-1).period)} · ${period==='annual'?'calendar years':period==='monthly'?'calendar months':'12-month windows'}</p></div>${charts.legend(config.series,rows,config.unit)}${charts.lineChart(rows,config.series,{...config,mode:period})}<figcaption class="chart-explanation" id="${captionId}"><p><strong>What it shows.</strong> ${config.shows}</p><p><strong>How it was obtained.</strong> ${config.method}</p><p><strong>Time window.</strong> ${windowText} ${config.denominator || 'Contributor counts use the union of keys within each window, never the sum of monthly counts.'}</p><p class="chart-source">Source: OpenAlex metadata frozen 16 September 2026; arXiv-linked works with Mathematics as their primary OpenAlex field, queried publication years 2010–2026. Analysis year/month comes from the arXiv ID. This is a selected population. <a href="${config.download || 'historical_participation.json'}" download>Exact values and provenance</a>.</p></figcaption></figure>`;
  }
  function renderCharts() {
    if (!data) return;
    const rows = data[period];
    const primary = {
      title:'Papers per active contributor · Pₜ/Aₜ', unit:'papers per active contributor key', series:definition,
      shows:'How many retained papers correspond to one distinct contributor key in the same time window. Both lines use exactly the same papers. Blue uses OpenAlex’s existing resolved author IDs; dashed brown uses distinct raw-name strings. Neither is a validated count of people.',
      method:'Divide retained paper count P by distinct keys A on those papers. Retain complete returned bylines with names and usable IDs, no repeated ID or group-name flag, and fewer than 100 slots without truncation. Names receive only Unicode and whitespace normalization; case, initials, accents and punctuation remain. No new identity-merging algorithm is applied.'
    };
    el('historical-primary').innerHTML = figure(rows,primary,1);
    const study = populations.study;
    el('historical-fixed').innerHTML = figure(rows, {
      title:'Papers per contributor in the full study · Pₜ/A_all', unit:'papers per full-study contributor key',
      series:[
        {label:'OpenAlex author IDs · fixed pool',color:'#365bc9',value:r=>r.papers/study.ids.authors},
        {label:'Distinct names · fixed pool',color:'#a76519',value:r=>r.papers/study.names.authors}],
      shows:'Papers in each time window divided by everyone observed at any point in the full study. Contributors with no retained paper in that window contribute zero. Because the denominator is fixed, this curve follows changes in paper counts; it does not measure the output of the active workforce.',
      method:`Keep exactly the same paper count P as graph 1. Divide by the 2010–2025 union of ${num(study.ids.authors)} OpenAlex IDs or ${num(study.names.authors)} distinct names, including keys observed before or after the selected window. Never add annual contributor counts.`,
      denominator:'The numerator follows the selected window; the denominator always covers January 2010–December 2025. Changing the study endpoints would change this fixed population.',
      download:'contributor_populations.json'
    }, 2);
    const configs = [
      {title:'Papers linked and retained each period',unit:'papers',series:[
        {label:'All uniquely linked papers',color:'#365bc9',value:r=>r.coverage.linked_papers},
        {label:'Retained paired papers · P',color:'#a76519',value:r=>r.papers}],
       shows:'The paper population before and after byline checks. The gap is excluded papers, not a fall in research output.',
       method:'Link each OpenAlex work to one unambiguous arXiv paper ID, remove ambiguous multiple-work groups, select 2010–2025 ID months, and count once. Apply the same byline checks used in graph 1 to obtain retained P.'},
      {title:'Observed contributors on the retained papers',unit:'distinct contributor keys',series:[
        {label:'OpenAlex author IDs',color:'#365bc9',value:r=>r.ids.authors},
        {label:'Distinct raw names',color:'#a76519',value:r=>r.names.authors}],
       shows:'The two denominators used in graph 1. One key counts once per period even when it appears on several papers. Uploading accounts and total author–paper links are not counted here.',
       method:'Take the set of usable OpenAlex IDs and, separately, the set of normalized raw names on the identical retained papers. Different names may represent one person, and one name or ID may represent several people.'},
      {title:'Retention through linkage and author-data checks',unit:'%',unitLabel:'percent of each stated paper population',maxY:100,series:[
        {label:'Paired / unambiguously linked papers',color:'#a76519',value:r=>100*r.coverage.retention},
        {label:'Paired / mapped arXiv paper IDs',color:'#365bc9',value:r=>100*r.coverage.overall_retention}],
       shows:'The solid brown line measures retention after byline checks among unambiguously linked papers. The dashed blue line also includes the earlier exclusion of arXiv IDs linked to multiple OpenAlex works. Changing selection can affect both P and A; their ratio does not automatically remove it.',
       method:'For brown, divide paired P by unambiguously linked papers. For blue, divide the same P by all distinct in-window arXiv IDs mapped from single-ID works, including ambiguous multiple-work groups. Multiply by 100. Neither denominator is all arXiv mathematics.'}
    ];
    el('historical-support').innerHTML = configs.map((c,i)=>figure(rows,c,i+3)).join('');
    el('historical-values').innerHTML = rows.map(r=>`<tr><th scope="row">${charts.escape(charts.windowLabel(r.period,period))}</th><td>${num(r.coverage.linked_papers)}</td><td>${num(r.papers)}</td><td>${pct(r.coverage.retention)}</td><td>${num(r.names.authors)}</td><td>${num(r.ids.authors)}</td><td>${num(r.names.papers_per_author)}</td><td>${num(r.ids.papers_per_author)}</td><td>${num(r.papers/study.names.authors)}</td><td>${num(r.papers/study.ids.authors)}</td></tr>`).join('');
    document.querySelectorAll('[data-history-period]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.historyPeriod===period)));
  }
  function renderFindings() {
    const a=data.annual[0], b=data.annual.at(-1);
    const lo=Math.min(...data.annual.map(r=>r.coverage.retention)), hi=Math.max(...data.annual.map(r=>r.coverage.retention));
    el('historical-findings').innerHTML = `<p class="eyebrow">WHAT THE RECORDED DATA SHOW</p><h2>The long-run comparison, with its coverage limits</h2><p class="body-copy">Between ${a.period} and ${b.period}, papers per active OpenAlex ID change from <strong>${num(a.ids.papers_per_author)} to ${num(b.ids.papers_per_author)} (${change(a.ids.papers_per_author,b.ids.papers_per_author)})</strong>. Using distinct names, the ratio changes from <strong>${num(a.names.papers_per_author)} to ${num(b.names.papers_per_author)} (${change(a.names.papers_per_author,b.names.papers_per_author)})</strong>.</p><p class="body-copy">Retained paper counts change by <strong>${change(a.papers,b.papers)}</strong>, compared with <strong>${change(a.ids.authors,b.ids.authors)}</strong> for observed IDs and <strong>${change(a.names.authors,b.names.authors)}</strong> for names. A higher P/A means paper counts grew faster than the corresponding contributor-key count.</p><p class="body-copy">Across those years, byline retention ranges from <strong>${pct(lo)} to ${pct(hi)}</strong>. ${num(data.diagnostics.duplicate_arxiv_id_groups)} additional arXiv paper-ID groups have ambiguous multiple-work links and are excluded; graph 5 includes this earlier selection step. These are changes among recorded contributor keys on selected papers. They do not establish a change in individual researchers’ productivity or an effect of AI.</p><p class="body-copy">Mean returned team size rises from <strong>${num(a.mean_team_size)} to ${num(b.mean_team_size)}</strong>. Authorship slots per key change from ${num(a.names.incidences_per_author)} to ${num(b.names.incidences_per_author)} for names, and ${num(a.ids.incidences_per_author)} to ${num(b.ids.incidences_per_author)} for IDs. The identity P/A = (I/A) ÷ (I/P), where I counts byline slots, explains why collaboration matters to the ratio.</p><p class="chart-note">A raw-name string can occur in several slots of one paper. The new <a href="#decile">top-decile analysis</a> counts that key once per paper for coauthored-paper totals, while fractional credit retains all slots.</p>`;
    const study=populations.study;
    el('historical-study').innerHTML=`<p class="eyebrow">ALL SIXTEEN YEARS COMBINED</p><h2>Whole-study papers per contributor · P_all/A_all</h2><p class="body-copy">${num(study.papers)} retained papers from January 2010 to December 2025, divided by each distinct key observed anywhere on those papers. Each key appears once in the full-study denominator, however many years it participated.</p><div class="table-scroll"><table><thead><tr><th scope="col">Identity definition</th><th scope="col">Full-study contributors · A_all</th><th scope="col">P_all/A_all</th><th scope="col">Mean coauthored papers</th></tr></thead><tbody>${['ids','names'].map(m=>`<tr><th scope="row">${m==='ids'?'OpenAlex author IDs':'Distinct raw names'}</th><td>${num(study[m].authors)}</td><td>${num(study[m].papers_per_active_contributor)}</td><td>${num(study[m].coauthored_papers_per_active_contributor)}</td></tr>`).join('')}</tbody></table></div><p class="chart-note">These are cumulative totals per observed key over 16 years, not annual rates. Mean coauthored papers counts each key once per paper; P_all/A_all shares each paper’s credit across its byline. <a href="CONTRIBUTOR_POPULATIONS.md" download>Definitions, calculations and results</a> · <a href="#decile">Explore the most prolific 10% →</a></p>`;
    el('historical-partial').innerHTML=data.annual_audit.map(r=>{
      const p=r.partial_credit;
      return `<tr><th scope="row">${r.period}</th><td>${num(p.usable_byline_papers)}</td><td>${num(p.raw_name_keys_usable)}</td><td>${num(p.identified_id_keys)}</td><td>${num(p.usable_papers_per_raw_name)}</td><td>${num(p.usable_papers_per_identified_id)}</td><td>${num(p.allocated_credit_to_ids)}</td><td>${num(p.unallocated_missing_id_credit)}</td><td>${num(p.unallocated_unusable_byline_credit)}</td><td>${num(p.mean_allocated_credit_per_id)}</td></tr>`;
    }).join('');
    const stages=data.flow.stages;
    el('historical-flow').innerHTML=[['Acquired works',data.diagnostics.candidate_works],['Outside 2010–2025 arXiv ID dates',stages.outside_target_id_window||0],['No unique modern arXiv ID',stages.no_unique_modern_arxiv_id||0],['Multiple arXiv IDs on one work',stages.multiple_arxiv_ids||0],['Works in ambiguous linkage groups',data.diagnostics.works_in_duplicate_arxiv_groups],['Uniquely linked target-window papers',data.diagnostics.unique_arxiv_papers_in_window],['Retained paired papers',data.annual.reduce((n,r)=>n+r.papers,0)]].map(([label,n])=>`<tr><th scope="row">${label}</th><td>${num(n)}</td></tr>`).join('');
    el('historical-source-count').textContent=`${num(data.diagnostics.candidate_works)} acquired works → ${num(data.diagnostics.unique_arxiv_papers_in_window)} uniquely linked papers dated 2010–2025 → ${num(data.annual.reduce((n,r)=>n+r.papers,0))} paired papers.`;
  }
  document.querySelectorAll('[data-history-period]').forEach(b=>b.addEventListener('click',()=>{period=b.dataset.historyPeriod;renderCharts();}));
  Promise.all([fetch('historical_participation.json').then(r=>{if(!r.ok)throw Error('Historical data unavailable');return r.json();}),window.ObservatoryContributorData]).then(([d,p])=>{
    if(d.snapshot_manifest_sha256!==p.snapshot_manifest_sha256)throw Error('Inconsistent source snapshots');
    if(d.annual.length!==16||d.monthly.length!==192||d.rolling12.length!==181)throw Error('Incomplete historical series');
    for(const k of ['annual','monthly','rolling12'])for(const [i,r] of d[k].entries()){
      if(!Number.isSafeInteger(r.papers)||r.papers<0||r.papers>r.coverage.linked_papers)throw Error('Invalid paper counts');
      if(r.period!==p[k][i].period||r.papers!==p[k][i].papers)throw Error('Inconsistent paper populations');
      for(const m of ['names','ids'])if(r.papers && (!r[m].authors||r[m].authors!==p[k][i][m].authors||Math.abs(r.papers/r[m].authors-r[m].papers_per_author)>1e-10))throw Error('Invalid denominator');
    }
    data=d;populations=p;renderCharts();renderFindings();
  }).catch(()=>{el('historical-error').hidden=false;});
})();
