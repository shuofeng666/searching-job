"""Research-first 2027 scan. Search snippets are leads, never verified vacancies."""
from __future__ import annotations
import hashlib,json,os,re
from datetime import datetime,timezone
from pathlib import Path
from scanner_v2 import COMPANIES,CORE,ROTATING,TOPICS,TARGETS,company_for,location_for,now,read_json,search_google,tidy_url
ROOT=Path(__file__).resolve().parent/'public'/'data'
FEED,ARCHIVE=ROOT/'feed.json',ROOT/'archive.json'
INTERN=re.compile(r'\b(intern|internship|co-op|visiting researcher)\b',re.I)
RESEARCH=re.compile(r'\b(research|researcher|scientist|human[ -]computer|hci|ux research|user experience research|human factors)\b',re.I)
REJECT=re.compile(r'algorithm|foundation models?|deep learning|machine learning engineer|recommendation|\bproduct (?:design|management|designer|manager)\b|graphic design|marketing|software engineer|visual designer',re.I)
FOCUS=re.compile(r'hci|human.computer|human.ai|human.agent|ux research|user (?:experience )?research|human.centered|interaction|creativity|creative tools|design tools|\bcad\b|fabrication|cscw|collaboration|accessibility|visualization|visualisation|mixed reality|augmented reality',re.I)
YEAR=re.compile(r'(?<!\d)20(?:25|26|27)(?!\d)')

def classify(raw):
 url=tidy_url(raw.get('link',''));company=company_for(url) if url else None
 title=str(raw.get('title') or '').strip()[:240];snippet=str(raw.get('snippet') or '').strip()[:1800]
 if not company or not INTERN.search(title) or REJECT.search(title) or not RESEARCH.search(title):return None
 if not FOCUS.search(title+' '+snippet):return None
 years=set(YEAR.findall(title)) or set(YEAR.findall(snippet))
 year=int(next(iter(years))) if len(years)==1 else None
 region=location_for(title+' '+snippet)
 return dict(id=hashlib.sha256(url.encode()).hexdigest()[:20],title=title,company=company,
  region=region,location=region or 'Location not verified',kind='web',description=snippet,
  url=url,source='Employer-domain search result; posting not verified',
  source_date=str(raw.get('date') or '')[:80],deadline=None,deadline_status='Unverified',
  year=year,score=None,reasons=['Employer domain matched','Research role and HCI topic mentioned'],
  flags=['Verify posting is still open','Confirm research mentor, PhD, summer timing and visa','Deadline unverified'])

def plan(day):
 """12 searches: Microsoft, Meta, Autodesk, Adobe, four rotating, two topics, two archive."""
 tasks=[]
 for company in CORE:
  domain=COMPANIES[company][0]
  tasks.append((company,'US',f'site:{domain} ("research intern" OR "research scientist intern" OR "UX research intern" OR "HCI internship") (2027 OR summer)',False))
 for i in range(4):
  company=ROTATING[(day*4+i)%len(ROTATING)];domain=COMPANIES[company][0]
  region=('US','CA','SG','HK')[(day+i)%4]
  tasks.append((company,region,f'site:{domain} ("research intern" OR "UX research intern" OR "interaction research intern") 2027',False))
 for i in range(2):
  topic=TOPICS[(day*2+i)%len(TOPICS)];region=('US','CA','SG','HK')[(day+i)%4]
  tasks.append(('Topic: '+topic,region,f'"{topic}" (Microsoft OR Meta OR Adobe OR Autodesk OR Google) 2027',False))
 for i,year in enumerate((2025,2026)):
  company=list(COMPANIES)[(day*2+i)%len(COMPANIES)]
  tasks.append((f'{company} archive {year}','US',f'"{company}" "research intern" (HCI OR UX OR interaction OR creativity) {year}',True))
 return tasks

def research_record(item):
 title=str(item.get('title',''));text=title+' '+str(item.get('description',''))
 return bool(INTERN.search(title) and RESEARCH.search(title) and not REJECT.search(title) and FOCUS.search(text))

def scan(key,feed,archive,day=None,search=search_google):
 if not key:raise ValueError('Missing SERPAPI_KEY')
 day=datetime.now(timezone.utc).toordinal() if day is None else day;stamp=now()
 current={j['id']:j for j in feed.get('jobs',[]) if isinstance(j,dict) and j.get('id') and j.get('year')==2027 and research_record(j) and j.get('source','').startswith('Employer-domain')}
 leads={j['id']:j for j in feed.get('watch_leads',[]) if isinstance(j,dict) and j.get('id') and research_record(j)}
 history={j['id']:j for j in archive.get('postings',[]) if isinstance(j,dict) and j.get('id') and research_record(j)}
 coverage=dict(feed.get('coverage') or {});received=added=archived=unconfirmed=0;errors=[];tasks=plan(day)
 for label,region,query,past in tasks:
  try:
   raw=search(key,query,region);received+=len(raw);hits=leads_found=0
   for candidate in raw:
    item=classify(candidate)
    if not item:continue
    if past:
     if item['year'] not in (2025,2026):continue
     target=history;item['historical_only']=True
     item['flags'].append('Historical evidence only; no current opening implied')
    elif item['year']==2027:target=current
    elif item['year'] is None:
     target=leads;item['flags'].append('Year not verified; excluded from current opportunities')
    else:continue
    prev=target.get(item['id'],{});item['first_seen']=prev.get('first_seen',stamp);item['last_seen']=stamp
    if not prev:
     if target is current:added+=1
     elif target is history:archived+=1
     else:unconfirmed+=1
    target[item['id']]=item
    if target is leads:leads_found+=1
    else:hits+=1
   coverage[label]=dict(checked_at=stamp,region_searched=region,raw_results=len(raw),matched=hits,unresolved=leads_found,error=None)
  except Exception as error:
   code=getattr(getattr(error,'response',None),'status_code',None);reason='HTTP '+str(code) if code else type(error).__name__
   errors.append(label+': '+reason);coverage[label]=dict(checked_at=stamp,region_searched=region,matched=None,error=reason)
 targets=[dict(name=n,company=c,region=r,focus=f,url=u) for n,c,r,f,u in TARGETS]
 record=dict(at=stamp,requests=len(tasks),received=received,new_jobs=added,new_historical=archived,
             new_unconfirmed=unconfirmed,errors=errors,status='partial' if errors else 'success')
 fresh=dict(jobs=sorted(current.values(),key=lambda j:j['last_seen'],reverse=True)[:500],
            watch_leads=sorted(leads.values(),key=lambda j:j['last_seen'],reverse=True)[:120],
            coverage=coverage,targets=targets,runs=[record,*(feed.get('runs') or [])][:30],
            last_scan=stamp,scanner_version=3)
 old=dict(postings=sorted(history.values(),key=lambda j:(-j['year'],j['company'])),last_scan=stamp,
          years=[2025,2026],note='Historical employer-domain search leads; not current openings.')
 return fresh,old

def main():
 key=os.environ.get('SERPAPI_KEY','')
 if not key:raise SystemExit('SERPAPI_KEY missing; no paid search started')
 fresh,past=scan(key,read_json(FEED,{'jobs':[],'runs':[]}),read_json(ARCHIVE,{'postings':[]}))
 ROOT.mkdir(parents=True,exist_ok=True)
 FEED.write_text(json.dumps(fresh,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 ARCHIVE.write_text(json.dumps(past,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 last=fresh['runs'][0]
 print(f"Requests {last['requests']}; raw {last['received']}; 2027 research {last['new_jobs']}; uncertain-year {last['new_unconfirmed']}; archive {last['new_historical']}; errors {len(last['errors'])}")
 if len(last['errors'])==last['requests']:raise SystemExit('All searches failed; data saved for diagnosis')
if __name__=='__main__':main()
