"""Public research internship discovery helpers. No user data stored here."""
import hashlib
import re
from urllib.parse import parse_qsl,urlencode,urlparse,urlunparse,quote
import requests
REGIONS={'US':('United States','us'),'CA':('Canada','ca'),'SG':('Singapore','sg'),'HK':('Hong Kong','hk')}
SEARCH_TEMPLATES=[('jobs','"research intern" HCI PhD 2027','HCI research'),('jobs','"UX research intern" PhD 2027','UX research'),('web','("HCI research intern" OR "human AI interaction" OR "research internship") 2027 (Autodesk OR Adobe OR Microsoft OR Google OR Meta OR Apple OR IBM OR Samsung OR NVIDIA)','Research labs')]
TARGETS=[
('Autodesk Research · HCI & Visualization','Autodesk','US / CA','CAD collaboration, fabrication, design tools','https://www.autodesk.com/research'),
('Adobe Research · HCI','Adobe','US','Creativity support and creative tools','https://research.adobe.com/'),
('Microsoft Research · HCI / Tools for Thought','Microsoft','US / CA','Human-AI collaboration and cognition','https://www.microsoft.com/en-us/research/'),
('Google Research · HCI / UX Research','Google','US / CA','Human-centered research and user studies','https://research.google/'),
('Google DeepMind · Human-AI Interaction','Google DeepMind','US / CA','Human-AI interaction, not algorithm training','https://deepmind.google/'),
('Meta · Reality Labs Research','Meta','US / CA','Interaction techniques and spatial computing','https://about.meta.com/realitylabs/'),
('Apple · Human Interface / Research','Apple','US / CA','Interaction and design research','https://jobs.apple.com/'),
('IBM Research · Human-Centered AI','IBM','US / CA','Human-AI decision support','https://research.ibm.com/'),
('NVIDIA Research · HCI','NVIDIA','US / CA','Design and simulation interaction','https://research.nvidia.com/'),
('Amazon Science · UX Research','Amazon','US / CA','Human-centered systems','https://www.amazon.science/'),
('Autodesk Research · Toronto','Autodesk','CA','HCI and visualization','https://www.autodesk.com/research'),
('Adobe Research · Creative Intelligence','Adobe','US','Creativity tools','https://research.adobe.com/'),
('Samsung Research','Samsung','US / CA / SG','XR and interaction research','https://research.samsung.com/'),
('Sony Research','Sony','US / CA','Creative interaction','https://www.sony.com/en/SonyInfo/research/'),
('Snap Research','Snap','US / CA','AR interaction','https://research.snap.com/'),
('Spotify Research','Spotify','US / CA','User research, not recommendation algorithms','https://research.atspotify.com/'),
('Roblox Research','Roblox','US / CA','Co-creation and collaboration','https://corp.roblox.com/'),
('Atlassian Research / UX','Atlassian','US / CA','Teamwork and CSCW','https://www.atlassian.com/company/careers'),
('Salesforce Research / UX','Salesforce','US / CA','Human-AI work','https://www.salesforce.com/company/careers/'),
('Honda Research Institute USA','Honda','US','Human-AI group interaction','https://usa.honda-ri.com/'),
('Microsoft Research Asia · Singapore','Microsoft','SG','HCI teams only, not ML-only positions','https://www.microsoft.com/en-us/research/'),
('Samsung Research Singapore','Samsung','SG','Human-centered interaction','https://research.samsung.com/'),
('ByteDance / TikTok · UX Research','ByteDance','SG / US','Human-AI UX research','https://jobs.bytedance.com/'),
('Tencent · UX / Interactive Research','Tencent','HK / SG','Research-focused interaction','https://careers.tencent.com/'),
('Huawei · HCI Research','Huawei','HK / CA / SG','HCI research, not algorithm work','https://career.huawei.com/'),
('A*STAR · Human-Centered Research','A*STAR','SG','Research institute; secondary target','https://www.a-star.edu.sg/'),
('ASTRI · Human-Centered R&D','ASTRI','HK','Applied research; secondary target','https://www.astri.org/'),
('NUS · HCI / Design Research','NUS','SG','Academic research; secondary target','https://www.nus.edu.sg/'),
('SUTD · Computational Design','SUTD','SG','Academic design research; secondary target','https://www.sutd.edu.sg/'),
('SMU · HCI Research','SMU','SG','Academic HCI; secondary target','https://www.smu.edu.sg/')]
COMPANIES={'autodesk':'Autodesk','adobe':'Adobe','microsoft':'Microsoft','google':'Google','deepmind':'Google DeepMind','meta':'Meta','apple':'Apple','ibm':'IBM','nvidia':'NVIDIA','amazon':'Amazon','spotify':'Spotify','samsung':'Samsung','sony':'Sony','snap':'Snap','huawei':'Huawei','tencent':'Tencent','bytedance':'ByteDance','tiktok':'TikTok','shopify':'Shopify','atlassian':'Atlassian','intel':'Intel','hp':'HP','qualcomm':'Qualcomm','salesforce':'Salesforce','roblox':'Roblox','honda':'Honda','astri':'ASTRI','a*star':'A*STAR'}
INTERN=('intern','internship','co-op','visiting research','student researcher')
EXCLUDED=('algorithm engineer','recommendation algorithm','ranking algorithm','machine learning engineer','foundation model training','model training','deep learning algorithm','marketing intern','product design intern','graphic design intern','visual design intern','ui design intern','ux designer intern','frontend engineer intern')
MATCH={'HCI / Human-AI':('hci','human-computer','human computer','human-ai','human ai','human agent','human-centered ai'),'Design tools / Creativity':('design tool','creativity','creative tool','authoring','computational design','cad','fabrication','visualization'),'Collaboration / CSCW':('collaboration','collaborative','cscw','sensemaking','teamwork','decision making'),'UX Research':('ux research','user researcher','user experience research','usability research','user research')}
def tidy_url(raw):
 try:
  u=urlparse(raw)
  if u.scheme not in ('https','http') or not u.hostname:return ''
  q=[(k,v) for k,v in parse_qsl(u.query) if not k.lower().startswith('utm_') and k.lower() not in ('gclid','fbclid')]
  return urlunparse((u.scheme,u.netloc.lower(),u.path.rstrip('/'),'',urlencode(q),''))
 except (ValueError,TypeError):return ''
def stable_id(title,company,location,url):
 norm=lambda x:re.sub('[^a-z0-9]','',(x or '').lower())
 return hashlib.sha256(f'{norm(title)}|{norm(company)}|{norm(location)}'.encode()).hexdigest()[:20]
def classify(title,company,description,kind):
 t=title.lower();text=(title+' '+description).lower();c=company.lower();reasons=[];flags=[];score=0
 if not any(x in t for x in INTERN):
  if kind!='web' or not any(x in text for x in INTERN):return 0,[],['Not an internship']
 if any(x in t for x in EXCLUDED):return 0,[],['Excluded non-research role']
 if any(k in c for k in COMPANIES) or any(x in c for x in ('research','nus','ntu','smu','sutd','a*star','astri')):score+=20;reasons.append('Large organization or research institute')
 else:return 0,[],['Organization outside research-first scope']
 if any(x in t for x in ('research','researcher','scientist','visiting research')):score+=27;reasons.append('Research position')
 elif any(x in t for x in ('ux','user experience','interaction')):score+=14;reasons.append('Interaction / UX')
 for label,terms in MATCH.items():
  if any(x in text for x in terms):score+=13 if label=='HCI / Human-AI' else 9;reasons.append(label)
 if any(x in text for x in ('phd','ph.d','doctoral')):score+=8;reasons.append('PhD mentioned')
 else:flags.append('Confirm PhD eligibility')
 if '2027' in text:score+=5
 else:flags.append('Confirm Summer 2027 dates')
 if any(x in text for x in ('publish','publication','chi ','uist','research paper')):score+=8;reasons.append('Publication mentioned, not guaranteed')
 else:flags.append('Mentorship and publication scope unverified')
 if kind=='web':flags.append('Unverified web lead; confirm actual posting and location')
 if '2026' in text and '2027' not in text:score-=20;flags.append('Possibly old 2026 posting')
 return max(0,min(100,score)),reasons,flags
def search_one(key,region,engine,query,timeout=30):
 if region not in REGIONS:raise ValueError('Unknown region')
 response=requests.get('https://serpapi.com/search.json',params={'engine':'google_jobs' if engine=='jobs' else 'google','q':query,'location':REGIONS[region][0],'gl':REGIONS[region][1],'hl':'en','api_key':key},timeout=timeout)
 response.raise_for_status();data=response.json()
 if data.get('error'):raise RuntimeError('Search provider returned an error')
 out=[]
 if engine=='jobs':
  for x in data.get('jobs_results') or []:
   title=x.get('title','');company=x.get('company_name','');loc=x.get('location',REGIONS[region][0]);options=x.get('apply_options') or []
   url=next((p.get('link') for p in options if p.get('link')),None) or x.get('share_link') or ('https://www.google.com/search?q='+quote(f'{title} {company} {loc} jobs'))
   if title and company and tidy_url(url):out.append(dict(title=title,company=company,location=loc,region=region,kind='job',description=x.get('description',''),url=url,source='Google Jobs / SerpApi',source_date=(x.get('detected_extensions') or {}).get('posted_at','')))
 else:
  for x in data.get('organic_results') or []:
   title=x.get('title','');snippet=x.get('snippet','');url=x.get('link','')
   if not title or not tidy_url(url) or not any(w in (title+' '+snippet).lower() for w in INTERN):continue
   name=next((value for k,value in COMPANIES.items() if k in (title+' '+snippet+' '+url).lower()),urlparse(url).hostname or 'Unknown')
   out.append(dict(title=title,company=name,location=REGIONS[region][0]+' (search context only)',region=region,kind='web',description=snippet,url=url,source='Web search / SerpApi; unverified',source_date=x.get('date','')))
 return out
