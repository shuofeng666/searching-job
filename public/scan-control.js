/* Authenticated manual scan controls, injected into the existing deadline interface. */
(()=>{
 const URL='https://github.com/shuofeng666/searching-job/actions/workflows/scan.yml';
 const root=document.getElementById('opportunities');
 if(!root||document.getElementById('radar-scan-panel'))return;
 const panel=document.createElement('section');
 panel.id='radar-scan-panel';panel.setAttribute('aria-label','手动扫描与公司监测');
 panel.innerHTML=`<style>
 #radar-scan-panel{background:#fff;border:1px solid #d9e5f0;border-radius:12px;padding:17px 19px;margin-bottom:19px;color:#233b56}
 #radar-scan-panel .radar-top{display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap}
 #radar-scan-panel h3{font-size:16px;margin:0 0 5px}
 #radar-scan-panel p{font-size:12px;line-height:1.6;color:#63748a;margin:0}
 #radar-scan-panel button{background:#2968a4;border:1px solid #2968a4;border-radius:8px;color:white;padding:11px 15px;font-size:13px;font-weight:700}
 #radar-scan-panel button:disabled{opacity:.55;cursor:not-allowed}
 #radar-scan-panel .radar-auth{display:none;gap:8px;align-items:center;flex-wrap:wrap;margin-top:13px}
 #radar-scan-panel .radar-auth.active{display:flex}
 #radar-scan-panel input{max-width:300px;min-width:190px;padding:10px;border:1px solid #bed0df;border-radius:7px;font:inherit;font-size:13px}
 #radar-scan-panel .radar-link{color:#245e98;text-decoration:underline;font-size:12px}
 #radar-scan-panel .radar-companies{display:flex;gap:8px;flex-wrap:wrap;margin-top:13px}
 #radar-scan-panel .radar-company{font-size:11px;border:1px solid #dfe7ee;background:#f7fafc;padding:6px 8px;border-radius:6px}
 #radar-scan-panel #radar-message{margin-top:11px;min-height:17px}
 </style><div class="radar-top"><div><h3>🔎 立即搜索研究实习</h3><p>每天自动搜索，也可手动启动。Adobe、Meta 等公司即使未命中，也显示扫描覆盖情况。</p></div><button type="button" id="radar-run">检查扫描设置…</button></div><form id="radar-auth" class="radar-auth"><input id="radar-pass" type="password" autocomplete="off" placeholder="输入扫描密码（不会保存）" aria-label="扫描密码" required maxlength="256"><button id="radar-submit" type="submit">确认开始扫描</button><button id="radar-cancel" type="button" style="background:white;color:#325c83;border-color:#d1dfeb">取消</button></form><p id="radar-message" role="status" aria-live="polite"></p><div class="radar-companies" id="radar-companies"></div><a class="radar-link" href="${URL}" target="_blank" rel="noopener noreferrer">查看 GitHub 扫描日志 ↗</a>`;
 const toolbar=root.querySelector('.toolbar');root.insertBefore(panel,toolbar||root.firstChild);
 const $=id=>panel.querySelector('#'+id),run=$('radar-run'),auth=$('radar-auth'),pass=$('radar-pass'),message=$('radar-message');
 let running=false,baseline=null,pending=false;
 const msg=text=>{message.textContent=text;};
 const date=t=>t?new Date(t).toLocaleString('zh-CN'):'未知';
 async function status(){
  try{
   const r=await fetch('/api/scan',{cache:'no-store'}),data=await r.json();
   if(!data.configured){run.disabled=true;run.textContent='待配置：手动扫描';msg('需先配置 Vercel 环境变量。可通过下面的 GitHub 链接手动运行。');return;}
   if(data.last?.status&&data.last.status!=='completed'){
    running=true;run.disabled=true;run.textContent='扫描运行中…';msg(`GitHub Actions 正在运行，开始于 ${date(data.last.created_at)}。`);
   }else{
    running=false;run.disabled=false;run.textContent='▶ 立即搜索新岗位';
    if(data.last&&!pending)msg(`最近扫描：${date(data.last.created_at)} · ${data.last.conclusion==='success'?'运行成功（岗位仍须核实）':data.last.conclusion||'已结束'}`);
    else if(!pending)msg('配置就绪，可以启动扫描。');
   }
  }catch{run.disabled=true;run.textContent='扫描服务暂不可用';msg('当前部署无法读取扫描接口，可从 GitHub Actions 手动启动。');}
 }
 run.onclick=()=>{if(!run.disabled){auth.classList.add('active');pass.focus();}};
 $('radar-cancel').onclick=()=>{auth.classList.remove('active');pass.value='';};
 auth.onsubmit=async event=>{
  event.preventDefault();const password=pass.value;pass.value='';auth.classList.remove('active');run.disabled=true;run.textContent='正在请求…';msg('正在向 GitHub Actions 提交任务…');
  try{
   const response=await fetch('/api/scan',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password})});
   const data=await response.json();msg(data.message||data.error||'响应异常');
   if(response.ok){pending=true;running=true;run.textContent='已提交扫描';}
  }catch{msg('无法启动，请前往 GitHub Actions 检查。');}
  setTimeout(status,5000);
 };
 async function coverage(){
  try{
   const r=await fetch('/data/feed.json?ts='+Date.now(),{cache:'no-store'}),data=await r.json(),area=$('radar-companies');area.replaceChildren();
   for(const name of ['Microsoft','Meta','Adobe','Autodesk']){
    const c=data.coverage?.[name],el=document.createElement('span');el.className='radar-company';
    el.textContent=name+' · '+(!c?'尚未搜索':c.error?'搜索失败':`匹配 ${c.matched??0} 条 · 待核实`);
    area.append(el);
   }
   if(baseline===null)baseline=data.last_scan||'';
   if(pending&&data.last_scan&&data.last_scan!==baseline){pending=false;baseline=data.last_scan;msg('新数据已提交。刷新页面可以看到最新岗位。');run.disabled=false;run.textContent='▶ 立即搜索新岗位';}
  }catch{msg('监测数据暂时读取失败，请稍后刷新。');}
 }
 status();coverage();setInterval(()=>{status();coverage();},20000);
})();
