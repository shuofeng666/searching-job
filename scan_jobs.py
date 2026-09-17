"""Scheduled public vacancy discovery. SERPAPI_KEY stays in GitHub Actions secrets."""
from __future__ import annotations
import json
import os
from datetime import datetime,timezone
from pathlib import Path
from radar import REGIONS, SEARCH_TEMPLATES, TARGETS, classify, search_one, stable_id, tidy_url
DATA_PATH=Path(__file__).resolve().parent/'public'/'data'/'feed.json'
def utcnow():return datetime.now(timezone.utc).isoformat(timespec='seconds')
def empty_feed():return {'jobs':[],'runs':[],'last_scan':None,'targets':[dict(name=n,company=c,region=r,focus=f,url=u) for n,c,r,f,u in TARGETS]}
def load_feed(path=DATA_PATH):
 if path.exists():
  raw=json.loads(path.read_text(encoding='utf-8'))
  if isinstance(raw,dict) and isinstance(raw.get('jobs'),list):
   base=empty_feed();base.update({k:raw[k] for k in ('jobs','runs','last_scan') if k in raw});return base
 return empty_feed()
def run_once(api_key,previous,search=search_one,time=utcnow,budget=12):
 if not api_key:raise ValueError('SERPAPI_KEY missing: add it as GitHub Actions secret')
 timestamp=time();prior={j['id']:j for j in previous['jobs'] if isinstance(j,dict) and 'id' in j}
 errors=[];received=requests=new_jobs=0
 for region in REGIONS:
  for engine,query,_ in SEARCH_TEMPLATES:
   if requests>=budget:break
   requests+=1
   try:candidates=search(api_key,region,engine,query)
   except Exception as exc:
    status=getattr(getattr(exc,'response',None),'status_code',None)
    errors.append(f'{region}/{engine}: HTTP {status}' if status else f'{region}/{engine}: {type(exc).__name__}')
    continue
   received+=len(candidates)
   for job in candidates:
    url=tidy_url(job.get('url',''))
    if not url:continue
    title=str(job.get('title','')).strip()[:240];company=str(job.get('company','')).strip()[:240];location=str(job.get('location','')).strip()[:240]
    if not title or not company:continue
    kind=job.get('kind','job');description=str(job.get('description',''))[:10000]
    score,reasons,flags=classify(title,company,description,kind)
    if score<40:continue
    jid=stable_id(title,company,location,url);old=prior.get(jid,{})
    prior[jid]=dict(id=jid,title=title,company=company,location=location,region=region,kind=kind,description=description,url=url,source=str(job.get('source',''))[:150],source_date=str(job.get('source_date',''))[:100],first_seen=old.get('first_seen') or timestamp,last_seen=timestamp,score=score,reasons=reasons,flags=flags)
    if not old:new_jobs+=1
 result=empty_feed();result['jobs']=sorted(prior.values(),key=lambda j:j.get('last_seen') or '',reverse=True)[:500]
 record={'at':timestamp,'requests':requests,'received':received,'new_jobs':new_jobs,'errors':errors,'status':'partial' if errors else 'success'}
 result['runs']=[record,*(previous.get('runs') or [])][:15];result['last_scan']=timestamp
 return result
def main():
 key=os.environ.get('SERPAPI_KEY','')
 if not key:raise SystemExit('SERPAPI_KEY missing: no search performed')
 result=run_once(key,load_feed());DATA_PATH.parent.mkdir(parents=True,exist_ok=True)
 DATA_PATH.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 run=result['runs'][0]
 print(f"Requests: {run['requests']}; results: {run['received']}; new: {run['new_jobs']}; errors: {len(run['errors'])}")
 if run['errors'] and run['requests']==len(run['errors']):raise SystemExit('All searches failed; failure status saved')
if __name__=='__main__':main()
