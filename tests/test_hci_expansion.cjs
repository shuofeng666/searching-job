const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const data=JSON.parse(fs.readFileSync('public/data/hci-expansion.json','utf8'));
const html=fs.readFileSync('public/index.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
function runtime(){
 const nodes=new Map();
 const node=()=>({value:'',checked:false,innerHTML:'',textContent:'',classList:{add(){},remove(){},toggle(){}},addEventListener(){},after(el){nodes.set(el.id,el)}});
 const context=vm.createContext({URL,URLSearchParams,location:{search:''},localStorage:{getItem(){return null},setItem(){}},document:{getElementById(id){if(id==='hciExpansion')return nodes.get(id);if(!nodes.has(id))nodes.set(id,node());return nodes.get(id)},createElement:node,addEventListener(){},querySelectorAll(){return []}},payload:data});
 vm.runInContext(script.replace(/load\(\);\s*$/,''),context);
 vm.runInContext('curatedData=payload',context);
 return {context,nodes,run:s=>vm.runInContext(s,context)};
}
test('curated entries preserve evidence, region, URL and unknown dates',()=>{
 const entries=[...data.items,...data.caution_items,...data.watch_items];
 assert.equal(entries.length,12);
 assert.equal(new Set(entries.map(x=>x.id)).size,entries.length);
 for(const x of entries){for(const key of ['region','url','status','evidence','match_reason','fit_caveat','deadline','deadline_status'])assert.ok(Object.hasOwn(x,key),x.id+':'+key);assert.equal(new URL(x.url).protocol,'https:');}
 assert.equal(data.items.find(x=>x.company==='Roblox').deadline,null);
 assert.ok(data.items.find(x=>x.company==='Roblox').deadline_inference);
 assert.equal(data.caution_items[0].eligibility_status,'explicit_f1_j1_exclusion');
 assert.equal(data.watch_items.find(x=>x.company==='Notion').year,null);
});
test('actual frontend includes design jobs, excludes unverified curated leads and supports filters',()=>{
 const {run}=runtime();
 assert.equal(run('allJobs().filter(x=>x.id.startsWith("hci-")).length'),6);
 assert.equal(run('allJobs().some(x=>x.company==="Notion")'),false);
 run('selectedTopics.add("Design Tools")');
 assert.equal(run('visible().filter(x=>x.id.startsWith("hci-")).length'),3);
 run('selectedRegions.add("CA")');
 assert.equal(run('visible().filter(x=>x.id.startsWith("hci-")).length'),0);
});
test('rendered cards escape content, preserve caveats and do not invent countdowns',()=>{
 const {run,nodes}=runtime();run('render()');
 assert.match(nodes.get('hciExpansion').innerHTML,/F1\/J1/);
 assert.match(nodes.get('hciExpansion').innerHTML,/推断/);
 assert.match(nodes.get('undated').innerHTML,/Figma/);
 assert.equal(run('remaining(curatedJobs()[3])'),'');
 assert.match(run('expansionCard({...payload.items[0],title:"<img onerror=evil()>"})'),/&lt;img/);
 assert.equal(run('allJobs().filter(x=>x.id==="hci-figma-design-2027").length'),1);
});
