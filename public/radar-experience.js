/* Research-first experience: discovery evidence is deliberately separate from open jobs. */
(()=>{
 'use strict';
 const root=document.getElementById('opportunities');
 if(!root||document.getElementById('research-workspace'))return;
 const KEY='research-radar-reviewed-at-v1';
 const CORE=['Autodesk','Adobe','Microsoft','Meta'];
 const safe=url=>{try{let u=new URL(url);return u.protocol==='https:'?u.href:null}catch{return null}};
 const make=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n};
 function link(url,label){const a=make('a','research-evidence-link',label);const href=safe(url);if(href){a.href=href;a.target='_blank';a.rel='noopener noreferrer'}else{a.removeAttribute('href');a.setAttribute('aria-disabled','true')}return a}
 const section=make('section','research-workspace');section.id='research-workspace';
 section.innerHTML=`<style>
 .research-workspace{border:1px solid #dce6ef;background:#fff;border-radius:12px;padding:16px 19px;margin-bottom:19px;color:#1d3754}
 .research-workspace .research-head{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}
 .research-workspace h3{font-size:15px;letter-spacing:-.2px;margin:0 0 4px}
 .research-workspace .research-muted{font-size:12px;color:#63758a;line-height:1.6;margin:0}
 .research-workspace .research-stats{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0;padding:11px 0;border-top:1px solid #e7edf4;border-bottom:1px solid #e7edf4;font-size:12px}
 .research-workspace .research-stats span{flex:1;min-width:105px}.research-workspace strong{color:#163a60}
 .research-workspace button{font:inherit;font-size:12px;border:1px solid #bdd0e2;background:#f7fafc;color:#28547d;border-radius:7px;padding:8px 12px;cursor:pointer}
 .research-workspace details{border-top:1px solid #e7edf4;padding:12px 0}
 .research-workspace details:first-of-type{border-top:0}
 .research-workspace summary{font-size:13px;font-weight:750;color:#244b72;cursor:pointer;list-style:revert}
 .research-workspace .research-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:12px}
 .research-workspace .research-item{border:1px solid #e2e9f1;border-radius:9px;padding:12px;background:#fbfcfe;min-width:0}
 .research-workspace .research-item b{display:block;font-size:12px;line-height:1.45;margin-bottom:5px}
 .research-workspace .research-item p{font-size:12px;color:#586d81;line-height:1.5;margin:6px 0}
 .research-workspace .research-item small{font-size:11px;color:#63758a;display:block;margin-bottom:7px}
 .research-workspace .research-evidence-link{display:inline-block;margin:5px 10px 0 0;font-size:12px;color:#205e98;text-decoration:underline}
 .research-workspace .research-flag{font-size:10px;background:#fff3dc;color:#81591e;padding:3px 6px;border-radius:4px}
 @media(max-width:650px){.research-workspace{padding:14px 12px}.research-workspace .research-grid{grid-template-columns:1fr}}
 </style><div class="research-head"><div><h3>我的研究实习雷达</h3><p class="research-muted">只把 2027 证据放进岗位列表；研究团队、年份不明线索和往年记录独立显示。</p></div><button id="research-reviewed" type="button">✓ 我已查看本轮线索</button></div><div id="research-stats" class="research-stats" role="status" aria-live="polite">正在读取…</div><details id="research-leads"><summary id="research-leads-summary">待核实的研究岗位线索</summary><p class="research-muted">这些链接不是已核实的 Summer 2027 招聘；先检查职位页面和年份，再决定是否加入申请清单。</p><div class="research-grid" id="research-lead-list"></div></details><details id="research-teams"><summary>研究组跟踪：Autodesk、Adobe、Microsoft、Meta</summary><p class="research-muted">有研究方向证据不等于正在招聘。找不到岗位时仍保留研究组、官方招聘入口和历史证据。</p><div class="research-grid" id="research-team-list"></div></details><p class="research-muted" id="research-health">本页只显示搜索证据，申请前请核实官方页面。</p>`;
 const toolbar=root.querySelector('.toolbar');root.insertBefore(section,toolbar||root.firstChild);
 const get=id=>section.querySelector('#'+id);
 const date=s=>{try{return s?new Date(s).toLocaleDateString('zh-CN'):'未扫描'}catch{return '未知'}};
 const rejected=/algorithm|foundation model|deep learning|machine learning engineer|\bproduct (?:design|designer|management|manager)\b|marketing|graphic design/i;
 function clean(items){return (Array.isArray(items)?items:[]).filter(x=>x&&typeof x==='object'&&!rejected.test(String(x.title||'')))}
 function item(title,body,urls,meta){const box=make('div','research-item');box.append(make('b','',title));if(meta)box.append(make('small','',meta));box.append(make('p','',body));for(const [url,label] of urls)box.append(link(url,label));return box}
 function render(feed,evidence){
  const leads=clean(feed.watch_leads),jobs=clean(feed.jobs),groups=Array.isArray(evidence.groups)?evidence.groups:[];
  let reviewed='';try{reviewed=localStorage.getItem(KEY)||''}catch{}
  const fresh=leads.filter(x=>!reviewed||String(x.first_seen||'')>reviewed);
  const newJobs=jobs.filter(x=>!reviewed||String(x.first_seen||'')>reviewed);
  const stats=get('research-stats');stats.replaceChildren();
  for(const [label,num] of [['2027 搜索线索',jobs.length],['年份待核实',leads.length],['本次未查看',newJobs.length+fresh.length],['监测研究组',groups.length]]){
   const span=make('span');const n=make('strong','',String(num));span.append(n,document.createTextNode(' '+label));stats.append(span);
  }
  get('research-leads-summary').textContent=`待核实的研究岗位线索 · ${leads.length} 条`;
  const list=get('research-lead-list');list.replaceChildren();
  for(const x of leads.slice(0,30))list.append(item(`${x.company||'未知公司'} · ${x.title||'未命名研究线索'}`,
   String(x.description||'请打开原始链接核实。').slice(0,260),[[x.url,'查看来源 ↗']],
   `年份未证实 · ${x.region||'地区未证实'} · 首次发现 ${date(x.first_seen)}`));
  if(!leads.length)list.append(make('p','research-muted','目前没有年份待核实的研究职位。没有发现不代表该团队不招聘。'));
  const teamlist=get('research-team-list');teamlist.replaceChildren();
  for(const company of CORE){const group=groups.find(g=>g.company===company);if(!group)continue;
   const c=feed.coverage?.[company];const status=!c?'尚未执行公司定向搜索':c.error?`搜索失败：${c.error}`:`最近搜索 ${date(c.checked_at)} · 2027 标题线索 ${c.matched??0} · 年份待确认 ${c.unresolved??0}`;
   const urls=[[group.research_url,'研究方向 ↗'],[group.internship_url,'官方招聘入口 ↗']];
   if(group.historical_url)urls.push([group.historical_url,'往年研究证据 ↗']);
   teamlist.append(item(group.team,group.research_evidence,urls,status));
  }
  const last=feed.runs?.[0],lastScan=feed.last_scan;
  const stale=!lastScan||Date.now()-Date.parse(lastScan)>72*3600000;
  let health='最近数据检查：'+date(lastScan)+'。';
  if(!lastScan)health='尚未成功写入扫描数据。已列出已核实存在的研究团队，但没有声称它们在招人。';
  else if(stale)health+=' 数据已超过72小时，请检查 GitHub Actions。';
  else if(last?.status==='partial')health+=' 最近一轮有搜索失败；查看 GitHub 日志与覆盖卡片。';
  else health+=' 扫描完成不代表逐条核实招聘开放状态。';
  get('research-health').textContent=health;
 }
 let data={jobs:[],watch_leads:[],coverage:{}},evidence={groups:[]};
 async function refresh(){try{
  const [a,b]=await Promise.all([fetch('/data/feed.json?x='+Date.now(),{cache:'no-store'}),fetch('/data/research-evidence.json',{cache:'no-store'})]);
  if(!a.ok||!b.ok)throw Error('fetch failed');data=await a.json();evidence=await b.json();render(data,evidence);
 }catch{get('research-health').textContent='研究证据暂时加载失败。请刷新页面，或通过 GitHub 检查数据文件。';}}
 get('research-reviewed').onclick=()=>{try{localStorage.setItem(KEY,new Date().toISOString())}catch{}render(data,evidence)};
 refresh();setInterval(refresh,60000);
})();
