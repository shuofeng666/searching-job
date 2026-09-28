"""Research-internship discovery. Results are evidence, NEVER proof a job is open.

The four explicitly requested labs get a company query every run. All other
employers rotate. Historical search is weekly; no dates are extrapolated.
No paid searches occur on import or without SERPAPI_KEY.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from scanner_v2 import COMPANIES as BASE_COMPANIES, CORE, TOPICS as BASE_TOPICS, TARGETS, location_for, now, read_json, search_google, tidy_url

COMPANIES = {**BASE_COMPANIES, 'Figma': ('figma.com',), 'Notion': ('notion.com', 'notion.so'),
 'Shure': ('shure.com',), 'Intuit': ('intuit.com',), 'DoorDash': ('careersatdoordash.com',),
 'Lyft': ('lyft.com',), 'Delta': ('delta.com',), 'Canva': ('canva.com', 'lifeatcanva.com'),
 'Miro': ('miro.com',), 'Stryker': ('stryker.com',), 'Asana': ('asana.com',),
 'Airtable': ('airtable.com',), 'Dropbox': ('dropbox.com',), 'PTC': ('ptc.com',),
 'Unity': ('unity.com',), 'Epic Games': ('epicgames.com',)}
ROTATING = tuple(c for c in COMPANIES if c not in CORE)
TOPICS = (*BASE_TOPICS, 'design research', 'product design creative tools',
          'UX research', 'design technologist', 'human AI prototyping')

ROOT = Path(__file__).resolve().parent / 'public' / 'data'
FEED, ARCHIVE = ROOT / 'feed.json', ROOT / 'archive.json'
INTERN = re.compile(r'\b(?:intern|internship|co[ -]?op|visiting researcher)\b', re.I)
RESEARCH_TITLE = re.compile(r'\b(?:research|researcher|scientist|hci|human[ -]computer|human[ -]ai|user experience research|ux research|user researcher|human factors)\b', re.I)
TOPIC = re.compile(r'hci|human[ -]computer|human[ -]ai|human[ -]agent|human[ -]cent(?:er|re)ed|user (?:experience )?research|ux research|interaction|creativ|design tools?|fabricat|\bcad\b|collaborat|cscw|accessib|visualiz|visualis|mixed reality|augmented reality|\bxr\b', re.I)
REJECT_TITLE = re.compile(r'algorithm|foundation model|deep learning|machine learning engineer|recommendation|quantum|chemistry|\bproduct (?:management|manager)\b|graphic design|marketing|software engineer|visual designer|UI designer|business analyst|program manager|recruiter', re.I)
DESIGN_TITLE = re.compile(r'\b(?:product design(?:er)?|ux design(?:er)?|user experience design|interaction design(?:er)?|design technologist|creative technologist|industrial design)\b', re.I)
# Product design is eligible only with substantive HCI/prototyping evidence, not
# a generic "collaborative team" sentence. These are still unverified leads.
DESIGN_EVIDENCE = re.compile(r'user research|usability|user.cent(?:er|re)ed|interaction design|prototyp|design tools?|creative tools?|human.ai|\bhci\b|\bcad\b|fabricat', re.I)
EXPLICIT_YEAR = re.compile(r'(?<!\d)20(?:25|26|27)(?!\d)')
ARTICLE_PATH = re.compile(r'/(?:news|blog|blogs|people|person|publications|publication|articles|stories|press|fellowship)(?:/|$)', re.I)
# A Workday board can be a company-owned official job page without an *.company.com URL.
ATS_HOSTS = {'autodesk.wd1.myworkdayjobs.com': 'Autodesk',
 'nvidia.wd5.myworkdayjobs.com': 'NVIDIA', 'nvidia.eightfold.ai': 'NVIDIA',
 'careersus-shure.icims.com': 'Shure', 'delta.avature.net': 'Delta'}
ATS_PATHS = {('job-boards.greenhouse.io', '/figma/'): 'Figma',
 ('job-boards.greenhouse.io', '/lyft/'): 'Lyft',
 ('jobs.ashbyhq.com', '/notion/'): 'Notion'}
CORE_QUERIES = {
 'Microsoft': '"Microsoft Research" ("HCI" OR "human AI" OR "UX research" OR "interaction research") (intern OR internship) 2027',
 'Meta': '"Meta" ("Reality Labs" OR "HCI" OR "UX research" OR "interaction research") (intern OR internship) 2027',
 'Autodesk': '"Autodesk Research" ("HCI" OR "fabrication" OR "design tools" OR "agentic canvas") (intern OR internship) 2027',
 'Adobe': '"Adobe Research" ("HCI" OR "creative tools" OR "human AI" OR "UX research") (intern OR internship) 2027',
}
TARGET_REGIONS=('US','CA','SG','HK')

def employer(url):
 host=(urlparse(url).hostname or '').lower()
 if host in ATS_HOSTS: return ATS_HOSTS[host]
 for (board,prefix),name in ATS_PATHS.items():
  if host==board and urlparse(url).path.startswith(prefix): return name
 for name,domains in COMPANIES.items():
  if any(host==domain or host.endswith('.'+domain) for domain in domains): return name
 return None

def role_track(title, snippet=''):
 if not INTERN.search(title) or REJECT_TITLE.search(title): return None
 text=title+' '+snippet
 if RESEARCH_TITLE.search(title) and TOPIC.search(text): return 'research'
 if DESIGN_TITLE.search(title) and DESIGN_EVIDENCE.search(snippet): return 'hci_product_design'
 # Explicit HCI eligibility in a doctoral data-science role is a useful adjacent
 # research route, not permission to ingest generic data-science internships.
 if re.search(r'phd.*intern.*data science', title, re.I) and re.search(r'\bhci\b|human.computer interaction', snippet, re.I):
  return 'research_adjacent'
 return None

def classify(raw):
 url=tidy_url(raw.get('link',''))
 if not url: return None
 company=employer(url)
 title=str(raw.get('title') or '').strip()[:240]
 snippet=str(raw.get('snippet') or '').strip()[:1800]
 track=role_track(title,snippet)
 if not company or not track: return None
 if ARTICLE_PATH.search(urlparse(url).path): return None
 # Search snippets often mention *other* roles in sidebars. Never infer a year
 # from a snippet, search query, posted date or neighboring listing.
 years=set(EXPLICIT_YEAR.findall(title))
 year=int(next(iter(years))) if len(years)==1 else None
 region=location_for(title+' '+snippet)
 flags=['Employer-domain search result, not an independently verified open position',
        'Check 2027 summer dates, PhD eligibility, research mentor and work authorization',
        'No application deadline verified']
 if year is None: flags.append('Year not explicit in job title; placed in research leads')
 return {
  'id':hashlib.sha256(url.encode('utf-8')).hexdigest()[:20],
  'title':title,'company':company,'region':region,'location':region or 'Location not verified',
  'kind':'web','description':snippet,'url':url,
  'source':'Employer-domain search result; posting not verified',
  'source_date':str(raw.get('date') or '')[:80],
  'deadline':None,'deadline_status':'Unverified','year':year,'score':None,
  'verification_status':'search_lead','open_verified':False,'research_team_verified':False,
  'role_track':track,
  'reasons':['Employer URL','Relevant internship title','HCI/research or design-method evidence'], 'flags':flags,
 }

def plan(day):
 """12 searches/day. Every core company rotates through US/CA/SG/HK over four days."""
 tasks=[]
 day_of_week=day % 7
 for offset,company in enumerate(CORE):
  region=TARGET_REGIONS[(day+offset)%len(TARGET_REGIONS)]
  tasks.append((company,region,CORE_QUERIES[company],False))
 historic=day_of_week==0
 count=4 if historic else 6
 for i in range(count):
  name=ROTATING[(day*count+i)%len(ROTATING)]
  region=TARGET_REGIONS[(day+i)%len(TARGET_REGIONS)]
  tasks.append((name,region,f'"{name}" ("HCI" OR "UX research" OR "design research" OR "product design" OR "human AI" OR "design technologist") (intern OR internship) 2027',False))
 for i in range(2):
  topic=TOPICS[(day*2+i)%len(TOPICS)]
  region=TARGET_REGIONS[(day+2+i)%len(TARGET_REGIONS)]
  tasks.append(('Topic: '+topic,region,f'"{topic}" (intern OR internship) 2027',False))
 if historic:
  for i,year in enumerate((2025,2026)):
   name=list(COMPANIES)[(day*2+i)%len(COMPANIES)]
   tasks.append((name+f' archive {year}','US',f'"{name}" "research intern" (HCI OR interaction OR creativity OR UX) {year}',True))
 assert len(tasks)==12
 return tasks

def _research_record(item):
 title=str(item.get('title',''))
 return bool(role_track(title,str(item.get('description',''))))

def scan(key,feed,archive,day=None,search=search_google):
 if not key: raise ValueError('SERPAPI_KEY missing; no requests made')
 day=datetime.now(timezone.utc).toordinal() if day is None else day
 stamp=now()
 current={j['id']:j for j in feed.get('jobs',[]) if isinstance(j,dict) and j.get('id') and j.get('year')==2027 and _research_record(j) and j.get('source','').startswith('Employer-domain')}
 leads={j['id']:j for j in feed.get('watch_leads',[]) if isinstance(j,dict) and j.get('id') and _research_record(j)}
 history={j['id']:j for j in archive.get('postings',[]) if isinstance(j,dict) and j.get('id') and _research_record(j)}
 coverage=dict(feed.get('coverage') or {})
 errors=[];received=added=archived=unconfirmed=0;tasks=plan(day)
 for label,region,query,past in tasks:
  try:
   raw=search(key,query,region)
   received+=len(raw);hits=uncertain=0
   for candidate in raw:
    item=classify(candidate)
    if not item: continue
    if past:
     if item['year'] not in (2025,2026):continue
     target=history;item['historical_only']=True
     item['flags'].append('Historical posting only; 2027 opening not implied')
    elif item['year']==2027: target=current
    elif item['year'] is None: target=leads
    else: continue
    previous=target.get(item['id'],{})
    item['first_seen']=previous.get('first_seen',stamp)
    item['last_seen']=stamp
    if not previous:
     if target is current:added+=1
     elif target is history:archived+=1
     else:unconfirmed+=1
    target[item['id']]=item
    if target is leads: uncertain+=1
    else: hits+=1
    if target is current: leads.pop(item['id'],None)
   prior=coverage.get(label) if isinstance(coverage.get(label),dict) else {}
   recent=[r for r in prior.get('recent_regions',[]) if r in TARGET_REGIONS and r!=region]
   recent=[region,*recent][:4]
   coverage[label]={'checked_at':stamp,'region_searched':region,'recent_regions':recent,'raw_results':len(raw),
                    'matched':hits,'unresolved':uncertain,'error':None,
                    'meaning':'One search query this run; recent_regions records up to four latest target regions'}
  except Exception as exc:
   code=getattr(getattr(exc,'response',None),'status_code',None)
   reason='HTTP '+str(code) if code else type(exc).__name__
   errors.append(label+': '+reason)
   prior=coverage.get(label) if isinstance(coverage.get(label),dict) else {}
   recent=[r for r in prior.get('recent_regions',[]) if r in TARGET_REGIONS and r!=region]
   coverage[label]={'checked_at':stamp,'region_searched':region,'recent_regions':[region,*recent][:4],
                    'matched':None,'unresolved':None,'error':reason}
 targets=[dict(name=n,company=c,region=r,focus=f,url=u) for n,c,r,f,u in TARGETS]
 run={'at':stamp,'requests':len(tasks),'received':received,'new_jobs':added,
      'new_historical':archived,'new_unconfirmed':unconfirmed,'errors':errors,
      'status':'partial' if errors else 'success'}
 fresh={'jobs':sorted(current.values(),key=lambda j:j.get('last_seen',''),reverse=True)[:500],
        'watch_leads':sorted(leads.values(),key=lambda j:j.get('last_seen',''),reverse=True)[:200],
        'coverage':coverage,'targets':targets,'runs':[run,*(feed.get('runs') or [])][:60],
        'last_scan':stamp,'scanner_version':4,
        'data_note':'Research search leads are not verified open jobs; 2027 is title evidence only.'}
 past={'postings':sorted(history.values(),key=lambda j:(-j['year'],j['company'])),
       'last_scan':stamp,'years':[2025,2026],
       'note':'Historical employer-domain leads; not evidence of an open 2027 role.'}
 return fresh,past

def _atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix(path.suffix+'.tmp')
 tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 tmp.replace(path)

def main():
 key=os.environ.get('SERPAPI_KEY','')
 if not key:raise SystemExit('SERPAPI_KEY missing; no paid search started')
 fresh,history=scan(key,read_json(FEED,{'jobs':[],'runs':[]}),read_json(ARCHIVE,{'postings':[]}))
 _atomic(FEED,fresh);_atomic(ARCHIVE,history)
 r=fresh['runs'][0]
 print(f"Requests {r['requests']}; raw {r['received']}; research 2027 leads {r['new_jobs']}; uncertain year {r['new_unconfirmed']}; history {r['new_historical']}; errors {len(r['errors'])}")
 if len(r['errors'])==r['requests']:raise SystemExit('All searches failed; diagnostic data saved')

if __name__=='__main__':main()
