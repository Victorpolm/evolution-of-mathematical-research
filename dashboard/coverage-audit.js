'use strict';
(() => {
  let audit, period='monthly';
  const charts=window.ObservatoryCharts;
  const el=id=>document.getElementById(id);
  const fmt=new Intl.NumberFormat('en-US',{maximumFractionDigits:3});
  const num=x=>x===null||x===undefined?'—':fmt.format(x);
  const share=x=>x===null?'—':(100*x).toFixed(2)+'%';
  const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const read=(r,key)=>key==='retention'?100*r.retention:key.startsWith('share:')?100*r.state_shares[key.slice(6)]:r[key];
  function renderSparks(){
    if(!audit)return;
    const rows=audit[period];
    const configs=[
      {title:'Papers before and after author-data checks',unit:'papers',series:[{key:'linked_papers',label:'All linked papers',color:'#365bc9'},{key:'paired_papers',label:'Retained for comparison',color:'#a76519'}],
        shows:'The blue line counts the papers we could link to one arXiv ID. The dashed brown line counts those retained for the distinct-name versus OpenAlex-ID comparison. The gap is the number excluded by the author-data checks.',
        method:'Count each linked paper once in its arXiv ID month. Retain it only if every returned author slot has a name and a usable ID, IDs are not repeated within the paper, and no group-name or truncated-byline flag applies; lists of 100 or more slots are excluded. These checks assess the returned metadata, not verified real people.'},
      {title:'Share of linked papers retained for comparison',unit:'%',maxY:100,series:[{key:'retention',label:'Retained share',color:'#a76519'}],
        shows:'The percentage of linked papers that pass those author-data checks. A lower value means more papers are excluded before the two identity approaches can be compared. It does not measure coverage of all arXiv mathematics.',
        method:'Divide retained papers by all linked papers in the same time window, then multiply by 100. In a rolling window, divide the 12-month totals rather than averaging monthly percentages.'},
      {title:'Linked papers with missing author IDs',unit:'%',series:[{key:'share:all_ids_missing',label:'All author IDs missing',color:'#9d3150'},{key:'share:some_ids_missing',label:'Some author IDs missing',color:'#7555a7'}],
        shows:'The red line is the share of papers whose entire nonempty author list lacks usable IDs. The dashed purple line is the share with both identified and unidentified author slots. These are percentages of papers, not percentages of authors.',
        method:'Put each linked paper into one of the two non-overlapping missing-ID categories, then divide each count by all linked papers in the same window and multiply by 100. Missing-ID categories take precedence if other exclusion flags also apply. Empty bylines enter the other-exclusion category.'}
    ];
    el('audit-sparks').innerHTML=configs.map((config,index)=>{
      const series=config.series.map(s=>({...s,value:r=>read(r,s.key)}));
      const titleId=`audit-chart-${index+1}-title`,captionId=`audit-chart-${index+1}-caption`;
      return `<figure class="explained-chart" aria-labelledby="${titleId}" aria-describedby="${captionId}"><div class="chart-heading"><h3 id="${titleId}">${index+1}. ${config.title}</h3><p>${charts.date(rows[0].period)}–${charts.date(rows.at(-1).period)} · ${period==='rolling12'?'12-month windows':period==='annual'?'calendar years':'monthly observations'}</p></div>${charts.legend(series,rows,config.unit)}${charts.lineChart(rows,series,{...config,mode:period})}<figcaption id="${captionId}" class="chart-explanation"><p><strong>What it shows.</strong> ${config.shows}</p><p><strong>How it was obtained.</strong> ${config.method}</p><p><strong>Time window.</strong> ${charts.windowNote(period)} Latest window: ${charts.windowLabel(rows.at(-1).period,period)}.</p><p class="chart-source">Source: OpenAlex metadata retrieved 15 September 2026; Mathematics primary field, arXiv-indexed works, queried publication years 2024–2026 and analysed arXiv ID dates in 2024–2025. <a href="retention_audit.json" download>Download the plotted values</a>.</p></figcaption></figure>`;
    }).join('');
    el('audit-window-note').textContent=charts.windowNote(period);
    el('audit-values').innerHTML=rows.map(r=>`<tr><th scope="row">${r.period}</th><td>${num(r.linked_papers)}</td><td>${num(r.paired_papers)}</td><td>${share(r.retention)}</td><td>${share(r.state_shares.all_ids_missing)}</td><td>${share(r.state_shares.some_ids_missing)}</td></tr>`).join('');
    document.querySelectorAll('[data-audit-period]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.auditPeriod===period)));
  }
  function render(){
    const [a,b]=audit.annual;
    el('audit-gap').textContent=audit.retention_gap_pp.paired.toFixed(2)+' pp';
    el('audit-finding').textContent=`Papers with no author IDs increase from ${num(a.states.all_ids_missing)} to ${num(b.states.all_ids_missing)}. This category accounts for ${audit.retention_gap_pp.all_ids_missing.toFixed(2)} percentage points of the gap. The underlying cause remains unresolved.`;
    const states=[['All linked target-window papers',r=>r.linked_papers],['Retained paired papers',r=>r.paired_papers],['Retained share',r=>share(r.retention)],['Entire byline has no IDs',r=>r.states.all_ids_missing],['Some IDs missing',r=>r.states.some_ids_missing],['Other byline exclusions',r=>r.states.other_byline_exclusion]];
    el('audit-coverage').innerHTML=states.map(([label,get])=>`<tr><th scope="row">${label}</th><td>${typeof get(a)==='number'?num(get(a)):get(a)}</td><td>${typeof get(b)==='number'?num(get(b)):get(b)}</td></tr>`).join('');
    const partial=[['Papers with usable bylines','usable_byline_papers'],['Observed valid IDs','identified_id_keys'],['Raw name keys, same usable bylines','raw_name_keys_usable'],['Credit allocated to IDs','allocated_credit_to_ids'],['Unallocated: missing IDs','unallocated_missing_id_credit'],['Unallocated: unusable bylines','unallocated_unusable_byline_credit'],['Mean allocated credit / ID','mean_allocated_credit_per_id']];
    el('audit-credit').innerHTML=partial.map(([label,key])=>`<tr><th scope="row">${label}</th><td>${num(a.partial_id_accounting[key])}</td><td>${num(b.partial_id_accounting[key])}</td></tr>`).join('');
    const [x,y]=audit.standardized_retention.annual;
    el('audit-standardized').textContent=`With the same pooled weights for team-size × subfield cells, retention is ${share(x.standardized_retention)} in 2024 and ${share(y.standardized_retention)} in 2025. Common cells cover ${share(x.common_support_share)} and ${share(y.common_support_share)} of usable bylines. The gap remains within those strata.`;
    el('audit-teams').innerHTML=[1,2,3,4,5,6].map(k=>{
      const v=audit.by_team_size.filter(r=>r.returned_slots===k);return `<tr><th scope="row">${k}</th>${v.map(r=>`<td>${num(r.linked_papers)}</td><td>${share(r.retention)}</td>`).join('')}</tr>`;
    }).join('');
    const fields=[...new Set(audit.by_subfield.map(r=>r.subfield))].sort();
    el('audit-fields').innerHTML=fields.map(field=>`<tr><th scope="row">${esc(field)}</th>${audit.by_subfield.filter(r=>r.subfield===field).map(r=>`<td>${num(r.linked_papers)}</td><td>${share(r.retention)}</td>`).join('')}</tr>`).join('');
    const flow=audit.work_flow.stages;
    el('audit-flow').innerHTML=[['Acquired OpenAlex works',audit.work_flow.acquired_works],['Outside the target arXiv-ID window',flow.outside_target_id_window],['Multiple arXiv IDs',flow.multiple_arxiv_ids],['No unique modern arXiv ID',flow.no_unique_modern_arxiv_id],['Uniquely linked target-window papers',flow.target_id_window],['Retained paired papers',a.paired_papers+b.paired_papers]].map(([label,value])=>`<tr><th scope="row">${label}</th><td>${num(value)}</td></tr>`).join('');
    el('audit-orcid').innerHTML=[['Recorded source ORCIDs','distinct_source_orcids'],['Observed on at least two papers','orcids_on_multiple_papers'],['Repeated ORCIDs with multiple IDs','multiple_ids_and_multiple_papers']].map(([label,key])=>`<tr><th scope="row">${label}</th><td>${num(a.orcid_on_paired_papers[key])}</td><td>${num(b.orcid_on_paired_papers[key])}</td></tr>`).join('')+`<tr><th scope="row">Multiple-ID share among repeated ORCIDs</th><td>${share(a.orcid_on_paired_papers.multiple_id_share_repeated_orcids)}</td><td>${share(b.orcid_on_paired_papers.multiple_id_share_repeated_orcids)}</td></tr>`;
    renderSparks();
  }
  document.querySelectorAll('[data-audit-period]').forEach(b=>b.addEventListener('click',()=>{period=b.dataset.auditPeriod;renderSparks();}));
  fetch('retention_audit.json').then(r=>{if(!r.ok)throw Error('Missing audit');return r.json();}).then(d=>{
    for(const k of ['monthly','annual','rolling12'])if(!Array.isArray(d[k])||!d[k].length)throw Error('Empty audit');
    for(const r of d.monthly)if(!Number.isSafeInteger(r.linked_papers)||r.paired_papers>r.linked_papers)throw Error('Invalid counts');
    audit=d;render();
  }).catch(()=>{el('audit-error').hidden=false;});
})();
