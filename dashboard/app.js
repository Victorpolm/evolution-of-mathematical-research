'use strict';

const modules = {
  growth: {
    title: 'Growth decomposition', label: 'PRODUCTION & PARTICIPATION',
    description: 'Separate growth in the active-author population from change in fractional publication output per active author.',
    formula: 'P<sub>t</sub> = A<sub>t</sub> × ȳ<sub>t</sub>',
    formulaNote: 'Δ log P = Δ log A + Δ log ȳ',
    definition: 'P is the number of retained papers; A is the number of active author IDs; ȳ = P/A. With complete authorships and 1/k credit per author, total fractional credit equals the paper count. This identity is descriptive.',
    measures: [['Annual papers and active author IDs', 'Implemented'], ['Fractional output per active author', 'Implemented'], ['Fixed-composition field standardization', 'Planned'], ['Rolling 3- and 5-year activity populations', 'Planned']],
    limitation: 'An increase in active IDs can reflect indexing or identity changes as well as more researchers. Mean fractional output also depends on collaboration patterns.',
    pending: 'The 2010–2025 papers/contributors comparison is available on the first dashboard view. Its annual decomposition and coverage series describe observed keys; population and causal conclusions require validation.'
  },
  concentration: {
    title: 'Output concentration', label: 'DISTRIBUTION OF PRODUCTION',
    description: 'Measure how publication credit is distributed across active authors, including the upper tail.',
    formula: 'C<sub>q,t</sub> = Σ<sub>i ∈ T(q,t)</sub> y<sub>it</sub> / Σ<sub>i</sub> y<sub>it</sub>',
    formulaNote: 'q ∈ {0.01, 0.05, 0.10}',
    definition: 'The historical top-decile comparison uses exactly 0.1 × A population weight, sharing boundary membership equally across tied keys. Contributors are ranked anew in each window and separately over the whole study. Coauthored counts deduplicate keys within each paper; fractional credit preserves every byline slot.',
    measures: [['Fractional top 1%, 5%, and 10% shares', 'Implemented'], ['Fractional Gini coefficient', 'Implemented'], ['Full-count top 10% share and Gini', 'Implemented'], ['Lorenz curves and richer productivity quantiles', 'Planned']],
    limitation: 'The current partial-ID calculation keeps credit for missing slots unallocated. Concentration among observed IDs still depends on missing papers and identity errors. An independent identity audit is required before population interpretation.',
    pending: 'The Top 10% contributors view now reports 2010–2025 annual, monthly, rolling and cumulative top-decile shares under both identity definitions and output measures. Older pilot top-1%, top-5% and Gini estimates remain archived; identity and high-output-tail validation remain pending.'
  },
  entry: {
    title: 'Entry & observed age', label: 'COHORTS & PERSISTENCE',
    description: 'Describe entry into the observed arXiv-mathematics population and the duration of observed participation.',
    formula: 'a<sub>it</sub> = t − first observed arXiv-math year<sub>i</sub>',
    formulaNote: 'Observed participation age ≠ true academic age',
    definition: 'The implemented age uses the earliest appearance of an OpenAlex author ID in the supplied dataset. The default minimum lookback is five years. Authors first seen at the acquisition boundary are flagged as potentially left-censored.',
    measures: [['New observed-author share', 'Implemented'], ['Share with observed age 0–3 years', 'Implemented'], ['Median observed age and boundary-censored share', 'Implemented'], ['Entrant persistence and cohort productivity', 'Planned']],
    limitation: 'Earlier work may be absent or outside arXiv mathematics. Intermittent publishing can make established researchers look like entrants. Persistence comparisons also need equal follow-up across cohorts.',
    pending: 'The 2023–2025 pilot is too short for headline career-age and entry conclusions. A longer lookback and follow-up window are required.'
  },
  collaboration: {
    title: 'Collaboration', label: 'TEAM SIZE & COAUTHORSHIP',
    description: 'Track collaboration patterns to interpret changes in full-count and fractional productivity.',
    formula: 'I<sub>t</sub> = Σ<sub>p ∈ P(t)</sub> k<sub>p</sub>',
    formulaNote: 'Mean full-count output per author = I / A',
    definition: 'I counts author–paper incidences and k is paper team size. Papers and incidences are different units. Full counting awards one credit to each author; fractional counting awards 1/k.',
    measures: [['Mean and median identified team size', 'Implemented'], ['Single-author and 3+ author paper shares', 'Implemented'], ['Separate 2, 3–5, and 6+ team-size bins', 'Planned'], ['New coauthor ties and cross-field networks', 'Later study']],
    limitation: 'The current implementation counts identified authors per paper. Incomplete IDs can understate team size and inflate the apparent solo-paper share; use complete authorships for headline comparisons.',
    pending: 'The historical aggregate dataset reports annual paired team sizes and within-subfield counts for 2010–2025. A causal or person-level collaboration interpretation remains unvalidated.'
  }
};

const fmt = new Intl.NumberFormat('en-US');
const pct = value => (100 * value).toFixed(1) + '%';
let projectData;
let pilotView = 'works';

function renderPilot() {
  if (!projectData) return;
  const p = projectData.pilot;
  const works = pilotView === 'works';
  const numerator = works ? p.retainedWorks : p.identifiedLinks;
  const denominator = works ? p.candidateWorks : p.identifiedLinks + p.missingSlots;
  const rest = denominator - numerator;
  const percentage = pct(numerator / denominator);
  const mainLabel = works ? 'Retained usable works' : 'Identified paper–author links';
  const restLabel = works ? 'Candidates not retained' : 'Slots missing an author ID';
  const caption = works ? 'Retained from the queried candidate works' : 'Identified among the reported pilot authorship slots';
  const note = works
    ? 'This is pilot retention, not coverage of all arXiv mathematics. The 8,783 non-retained candidates are a calculated remainder; a reason-by-reason breakdown is not available here.'
    : 'The denominator is reconstructed as 155,781 identified links + 8,042 missing slots = 163,823. This is ID availability, not the accuracy of author disambiguation or the fraction of complete papers.';
  const title = works ? 'Share of candidate works retained in the earlier pilot' : 'Share of author slots with an ID in the earlier pilot';
  const explanation = works
    ? 'The blue part is the share of queried works retained as usable; the light part is the remaining candidates. This bar combines 2023–2025 and shows no year-by-year trend.'
    : 'The teal part is the share of reported paper–author slots with an OpenAlex ID; the amber part lacks one. An author appearing on several papers contributes several slots. This bar does not count unique people.';
  const calculation = works
    ? 'Use the earlier pilot totals reported in the statistical research plan: 69,166 retained works / 77,949 candidates × 100 = 88.7%. The remainder is 8,783 candidates.'
    : 'Use the earlier pilot totals reported in the statistical research plan: 155,781 identified slots / (155,781 identified + 8,042 missing slots) × 100 = 95.1%.';
  document.querySelector('#pilot-detail').innerHTML = `
    <figure class="explained-chart pilot-figure" aria-labelledby="pilot-chart-title" aria-describedby="pilot-chart-caption"><div class="chart-heading"><h3 id="pilot-chart-title">${title}</h3><p>2023–2025 combined · separate, previously reported pilot</p></div>
    <div class="pilot-stat"><strong>${percentage}</strong><span>${works ? 'pilot retention' : 'reported ID availability'}</span></div>
    <p class="pilot-caption">${caption}</p>
    <div class="bar-chart ${works ? '' : 'authors'}" role="img" aria-label="${mainLabel}: ${fmt.format(numerator)}, ${percentage}. ${restLabel}: ${fmt.format(rest)}, ${pct(rest / denominator)}."><span class="bar-main" style="width:${100 * numerator / denominator}%"></span><span class="bar-secondary" style="width:${100 * rest / denominator}%"></span></div>
    <div class="bar-axis" aria-hidden="true"><span>0%</span><span>50%</span><span>100%</span></div>
    <div class="legend-row"><span><i class="swatch ${works ? '' : 'teal'}" aria-hidden="true"></i>${mainLabel}</span><strong>${fmt.format(numerator)}</strong></div>
    <div class="legend-row"><span><i class="swatch ${works ? 'secondary' : 'missing'}" aria-hidden="true"></i>${restLabel}</span><strong>${fmt.format(rest)}</strong></div>
    <figcaption id="pilot-chart-caption" class="chart-explanation"><p><strong>What it shows.</strong> ${explanation}</p><p><strong>How it was obtained.</strong> ${calculation} Percentages are calculated here; the source records for that older pilot were not available for independent reproduction.</p><p>${note}</p><p class="chart-source">Source: statistical research plan, project snapshot of 4 September 2026. These totals are separate from the September 15 OpenAlex audit.</p></figcaption></figure>`;
  document.querySelectorAll('[data-pilot]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.pilot === pilotView)));
}

function renderModule(key) {
  const m = modules[key] || modules.growth;
  document.querySelector('#analysis-detail').innerHTML = `
    <article class="panel"><p class="eyebrow">${m.label}</p><h2>${m.title}</h2><p class="analysis-description">${m.description}</p>
    <div class="formula-box">${m.formula}<small>${m.formulaNote}</small></div>
    <p class="analysis-description">${m.definition}</p>
    <div class="analysis-status"><h3>Implementation</h3><ul class="measure-list">${m.measures.map(([measure,status]) => `<li><span>${measure}</span><span class="badge ${status === 'Implemented' ? 'blue' : 'gray'}">${status}</span></li>`).join('')}</ul></div>
    <p class="chart-note">${m.limitation}</p></article>
    <div class="result-state"><span class="result-symbol" aria-hidden="true">∅</span><div><h3>Evidence and interpretation</h3><p>${m.pending}</p></div></div>`;
  document.querySelectorAll('[data-module]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.module === key)));
}

function route() {
  const hash = window.location.hash.slice(1);
  const view = hash.startsWith('analysis') ? 'analysis' : hash === 'decile' ? 'decile' : hash === 'methods' ? 'methods' : hash === 'overview' ? 'overview' : hash === 'manifest' ? 'manifest' : hash === 'papers' ? 'papers' : 'trends';
  const key = hash.startsWith('analysis-') ? hash.slice(9) : 'growth';
  document.querySelectorAll('.view').forEach(section => { section.hidden = section.id !== 'view-' + view; });
  document.querySelectorAll('[data-view]').forEach(link => {
    const selected = link.dataset.view === view;
    link.classList.toggle('active', selected);
    if (selected) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current');
  });
  if (view === 'analysis') renderModule(Object.hasOwn(modules, key) ? key : 'growth');
  document.title = `${view === 'decile' ? 'Top 10% contributors' : view === 'trends' ? 'Papers per observed contributor' : view === 'papers' ? 'Earlier coverage audit' : view === 'manifest' ? 'Repository upload counts' : view === 'overview' ? 'Growth & participation' : view === 'analysis' ? 'Measures & results' : 'Methods & sources'} · Mathematics Observatory`;
}

document.querySelectorAll('[data-pilot]').forEach(button => button.addEventListener('click', () => { pilotView = button.dataset.pilot; renderPilot(); }));
document.querySelectorAll('[data-module]').forEach(button => button.addEventListener('click', () => { window.location.hash = 'analysis-' + button.dataset.module; }));
window.addEventListener('hashchange', route);
document.querySelectorAll('.nav-link,.readiness-card,.status-strip a,.text-action').forEach(link => link.addEventListener('click', () => { window.scrollTo({top: 0, behavior: 'instant'}); }));
route();

fetch('data.json').then(response => {
  if (!response.ok) throw new Error('Pilot data unavailable');
  return response.json();
}).then(data => {
  for (const key of ['candidateWorks','retainedWorks','identifiedLinks','missingSlots']) {
    if (!Number.isSafeInteger(data.pilot[key]) || data.pilot[key] < 0) throw new Error('Invalid pilot count');
  }
  if (data.pilot.retainedWorks > data.pilot.candidateWorks || !data.pilot.candidateWorks || !(data.pilot.identifiedLinks + data.pilot.missingSlots)) throw new Error('Invalid pilot denominator');
  projectData = data;
  document.querySelectorAll('[data-count]').forEach(el => { el.textContent = fmt.format(data.pilot[el.dataset.count]); });
  renderPilot();
  const sourceList = document.querySelector('#source-list');
  for (const source of data.sources) {
    const url = source.url || `https://github.com/${data.repository}/blob/${data.revision}/${source.path}`;
    const link = document.createElement('a');
    link.className = 'source-item'; link.href = url; link.target = '_blank'; link.rel = 'noopener noreferrer';
    const content = document.createElement('div');
    const title = document.createElement('strong'); title.textContent = source.title;
    const description = document.createElement('p'); description.textContent = source.description;
    content.append(title,description);
    const arrow = document.createElement('span'); arrow.textContent = '↗'; arrow.setAttribute('aria-hidden','true');
    link.append(content,arrow); sourceList.append(link);
    document.querySelectorAll(`[data-source="${source.id}"]`).forEach(el => { el.href = url; });
  }
}).catch(() => { document.querySelector('#data-error').hidden = false; });
