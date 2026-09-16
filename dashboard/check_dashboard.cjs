const fs=require('fs'),vm=require('vm'),assert=require('assert');
const root=__dirname+'/';
function node(id){return {id,hidden:false,innerHTML:'',textContent:'',dataset:{},attributes:{},events:{},children:[],classList:{toggle(){}},setAttribute(k,v){this.attributes[k]=v},removeAttribute(k){delete this.attributes[k]},addEventListener(k,v){this.events[k]=v},append(...x){this.children.push(...x)}}}
async function run(corrupt=''){
 const elems=new Map(),get=id=>{if(!elems.has(id))elems.set(id,node(id));return elems.get(id)};
 get('historical-error').hidden=true; get('decile-error').hidden=true;
 const buttons=['annual','monthly','rolling12'].map(p=>{let n=node(p);n.dataset.historyPeriod=p;return n});
 const decileButtons=['annual','monthly','rolling12'].map(p=>{let n=node(p);n.dataset.decilePeriod=p;return n});
 const measureButtons=['fractional','coauthored'].map(p=>{let n=node(p);n.dataset.decileMeasure=p;return n});
 const views=[...fs.readFileSync(root+'index.html','utf8').matchAll(/id="(view-[^"]+)"/g)].map(m=>get(m[1]));
 const nav=views.map(v=>{let n=node('nav-'+v.id);n.dataset.view=v.id.slice(5);return n});
 const context={console,Intl,Date,Number,String,Object,Math,Set,Error,window:{location:{hash:''},addEventListener(){},scrollTo(){}},document:{getElementById:get,querySelector:s=>get(s.replace(/^#/,'')),querySelectorAll:s=>s==='[data-history-period]'?buttons:s==='[data-decile-period]'?decileButtons:s==='[data-decile-measure]'?measureButtons:s==='.view'?views:s==='[data-view]'?nav:[],createElement:t=>node(t)},fetch:async url=>{const data=JSON.parse(fs.readFileSync(root+url,'utf8'));if(corrupt==='historical'&&url==='historical_participation.json')data.annual[0].papers=-1;if(corrupt==='decile'&&url==='contributor_populations.json')data.annual[0].ids.fractional.share=2;return {ok:true,json:async()=>data}}};
 vm.createContext(context);
 for(const f of ['chart-utils.js','contributor-deciles.js','historical-trends.js','app.js'])vm.runInContext(fs.readFileSync(root+f,'utf8'),context,{filename:f});
 await new Promise(r=>setImmediate(r));
 if(corrupt){if(corrupt==='decile')assert.equal(get('decile-error').hidden,false);assert.equal(get('historical-error').hidden,false);assert(!get('historical-primary').innerHTML.includes('<svg'));return}
 assert.equal(get('historical-error').hidden,true);assert.equal(get('view-trends').hidden,false);assert.equal(get('view-papers').hidden,true);assert(context.document.title.startsWith('Papers per observed contributor'));
 for(const b of buttons){b.events.click();const p=b.dataset.historyPeriod,primary=get('historical-primary').innerHTML,support=get('historical-support').innerHTML,table=get('historical-values').innerHTML;
  assert(primary.includes('Papers per active contributor · Pₜ/Aₜ'));assert.equal((primary.match(/<svg/g)||[]).length,1);assert.equal((support.match(/<svg/g)||[]).length,3);assert(primary.includes('How it was obtained.'));assert(get('historical-fixed').innerHTML.includes('Pₜ/A_all'));assert(get('historical-fixed').innerHTML.includes('178,730'));assert.equal((get('historical-fixed').innerHTML.match(/<svg/g)||[]).length,1);assert(!/NaN|Infinity|undefined/.test(primary+support+table));assert.equal((table.match(/<tr>/g)||[]).length,{annual:16,monthly:192,rolling12:181}[p]);assert.equal(b.attributes['aria-pressed'],'true');
 }
 assert.equal((get('historical-partial').innerHTML.match(/<tr>/g)||[]).length,16);
 assert(get('historical-study').innerHTML.includes('231,929'));assert(get('historical-study').innerHTML.includes('1.679'));
 assert.equal(get('decile-error').hidden,true);
 for(const measure of measureButtons){measure.events.click();for(const b of decileButtons){b.events.click();
   const all=get('decile-share').innerHTML+get('decile-ratio').innerHTML+get('decile-study').innerHTML+get('decile-values').innerHTML;
   assert.equal((all.match(/<svg/g)||[]).length,2);assert(!/NaN|Infinity|undefined/.test(all));assert(all.includes('How it was obtained.'));
   assert.equal((get('decile-values').innerHTML.match(/<tr>/g)||[]).length,{annual:16,monthly:192,rolling12:181}[b.dataset.decilePeriod]);
   assert.equal(b.attributes['aria-pressed'],'true');assert.equal(measure.attributes['aria-pressed'],'true');
   assert(get('decile-study').innerHTML.includes(measure.dataset.decileMeasure==='fractional'?'52.02%':'49.16%'));
 }}
 context.window.location.hash='#decile';vm.runInContext('route()',context);assert.equal(get('view-decile').hidden,false);assert.equal(get('view-trends').hidden,true);assert(context.document.title.startsWith('Top 10% contributors'));
 console.log('Both denominator graphs, whole-study summary, all six decile controls, routes, captions and values passed.');
}
run().then(()=>run('historical')).then(()=>run('decile')).then(()=>console.log('Invalid-data guard passed.')).catch(e=>{console.error(e);process.exitCode=1});
