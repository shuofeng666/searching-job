"""Research-first search: official employer postings, 2027 feed, 2025/26 archive.

No paid request is made without SERPAPI_KEY. Search results are leads, not proof
that a role is open, has a verified deadline, or supports work authorization.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import requests
from radar import TARGETS, tidy_url

ROOT = Path(__file__).resolve().parent / 'public' / 'data'
FEED = ROOT / 'feed.json'
ARCHIVE = ROOT / 'archive.json'
COMPANIES = {
    'Microsoft': ('microsoft.com',),
    'Meta': ('metacareers.com', 'meta.com'),
    'Autodesk': ('autodesk.com',),
    'Adobe': ('adobe.com',),
    'Google': ('google.com', 'research.google', 'deepmind.google'),
    'Apple': ('apple.com',),
    'NVIDIA': ('nvidia.com',),
    'IBM': ('ibm.com',),
    'Amazon': ('amazon.jobs', 'amazon.com'),
    'Snap': ('snap.com',),
    'Samsung': ('samsung.com',),
    'Honda': ('honda-ri.com',),
    'Atlassian': ('atlassian.com',),
    'Salesforce': ('salesforce.com',),
    'Roblox': ('roblox.com',),
    'Sony': ('sony.com',),
    'Spotify': ('spotify.com',),
    'HP': ('hp.com',),
    'ByteDance': ('bytedance.com', 'tiktok.com'),
    'Tencent': ('tencent.com',),
    'Huawei': ('huawei.com',),
}
CORE = ('Microsoft', 'Meta', 'Autodesk', 'Adobe')
ROTATING = tuple(c for c in COMPANIES if c not in CORE)
TOPICS = ('HCI research intern', 'human AI interaction research internship',
          'UX researcher PhD intern', 'collaborative design fabrication research intern',
          'creativity support tools research intern', 'XR interaction research internship')
FOCUS = ('hci', 'human-computer', 'human computer', 'human-ai', 'human ai',
         'human-centered', 'human centred', 'interaction', 'ux research',
         'user experience research', 'user research', 'usability', 'human factors',
         'collaboration', 'cscw', 'creativity', 'creative tools', 'design tool',
         'computational design', 'fabrication', 'cad ', '3d design', 'accessibility',
         'assistive', 'xr ', 'mixed reality', 'augmented reality', 'reality labs',
         'visualization', 'visualisation')
EXCLUDE_TITLE = ('algorithm', 'recommendation', 'foundation model', 'deep learning',
                 'machine learning engineer', 'marketing', 'graphic design',
                 'product designer', 'visual designer', 'software engineer')
PLACES = {
    'US': ('united states', 'usa', 'california', 'new york', 'seattle', 'redmond',
           'mountain view', 'san francisco', 'boston', 'cambridge, ma', 'pittsburgh'),
    'CA': ('canada', 'toronto', 'montreal', 'montréal', 'vancouver', 'waterloo, on'),
    'SG': ('singapore',), 'HK': ('hong kong',),
}

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def read_json(path, fallback):
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            if isinstance(data, dict):
                return data
        except (ValueError, OSError):
            pass
    return fallback

def company_for(url):
    host = (urlparse(url).hostname or '').lower()
    for company, domains in COMPANIES.items():
        if any(host == domain or host.endswith('.' + domain) for domain in domains):
            return company
    return None

def location_for(text):
    lower = text.lower()
    matched = [code for code, tokens in PLACES.items()
               if any(token in lower for token in tokens)]
    return matched[0] if len(matched) == 1 else ''

def classify_result(result):
    url = tidy_url(result.get('link', ''))
    company = company_for(url) if url else None
    title = str(result.get('title') or '').strip()[:240]
    description = str(result.get('snippet') or '').strip()[:1800]
    text = (title + ' ' + description).lower()
    if not company or not re.search(r'\b(intern|internship|co-op|visiting researcher)\b', title, re.I):
        return None
    if any(term in title.lower() for term in EXCLUDE_TITLE):
        return None
    if not any(term in text for term in FOCUS):
        return None
    years = set(re.findall(r'(?<!\d)20(?:25|26|27)(?!\d)', text))
    if '2027' in years:
        year = 2027
    elif len(years) == 1:
        year = int(next(iter(years)))
    else:
        return None  # No inferred year from a search query or posting timestamp.
    if year not in (2025, 2026, 2027):
        return None
    region = location_for(title + ' ' + description)
    ref = hashlib.sha256(url.encode('utf-8')).hexdigest()[:20]
    reasons = ['Official employer domain', 'Relevant HCI/design research language']
    if re.search(r'\bph\.?d\.?\b|doctoral', text):
        reasons.append('Doctoral studies mentioned')
    score = 68 + (8 if 'research' in title.lower() else 0) + (8 if 'phd' in text or 'ph.d' in text else 0)
    record = dict(id=ref, title=title, company=company, region=region,
                  location=region or 'Location not verified', kind='job',
                  description=description, url=url, source='Employer-domain search result',
                  source_date=str(result.get('date') or '')[:80],
                  deadline=None, deadline_status='Unverified',
                  year=year, score=min(100, score), reasons=reasons,
                  flags=['Verify posting is open', 'Verify Summer start, PhD and work authorization',
                         'No official deadline verified'])
    return record

def search_google(key, query, region='US'):
    country = {'US':'us','CA':'ca','SG':'sg','HK':'hk'}.get(region, 'us')
    response = requests.get('https://serpapi.com/search.json', params={
        'engine':'google', 'q':query, 'gl':country, 'hl':'en', 'num':10,
        'api_key':key}, timeout=24)
    response.raise_for_status()
    data = response.json()
    if data.get('error'):
        raise RuntimeError('Search provider error')
    return data.get('organic_results') or []

def plan(day):
    """12 requests total: four fixed firms, four rotating firms, two topics, two history."""
    jobs = []
    for company in CORE:
        region = 'CA' if company == 'Autodesk' else 'US'
        jobs.append((company, region,
            f'"{company}" ("HCI" OR "human AI" OR "UX research" OR "interaction research" OR "design tools") (intern OR internship) 2027', False))
    for i in range(4):
        company = ROTATING[(day * 4 + i) % len(ROTATING)]
        region = ('US', 'CA', 'SG', 'HK')[(day + i) % 4]
        jobs.append((company, region,
            f'"{company}" ("HCI" OR "human AI" OR "UX research" OR "interaction" OR "design") research intern 2027', False))
    for i in range(2):
        topic = TOPICS[(day * 2 + i) % len(TOPICS)]
        region = ('US', 'CA', 'SG', 'HK')[(day + i) % 4]
        jobs.append(('Topic: ' + topic, region, f'"{topic}" 2027 (Microsoft OR Meta OR Autodesk OR Adobe OR Google OR Apple OR IBM OR NVIDIA)', False))
    for i, year in enumerate((2025, 2026)):
        company = tuple(COMPANIES)[(day * 2 + i) % len(COMPANIES)]
        jobs.append((company + f' archive {year}', 'US',
            f'"{company}" ("HCI" OR "UX research" OR "interaction" OR "design tools") internship {year}', True))
    return jobs

def scan(key, feed, archive, day=None, search=search_google):
    if not key:
        raise ValueError('SERPAPI_KEY missing')
    today = datetime.now(timezone.utc)
    index = day if day is not None else today.toordinal()
    stamp = now()
    # Discard the first-generation unverified third-party leads from the public job feed.
    old = {x['id']:x for x in feed.get('jobs', [])
           if isinstance(x, dict) and x.get('id') and
           x.get('source') == 'Employer-domain search result' and x.get('year') == 2027}
    history = {x['id']:x for x in archive.get('postings', [])
               if isinstance(x, dict) and x.get('id')}
    coverage = dict(feed.get('coverage') or {})
    calls = received = added = historic = 0
    errors = []
    for label, region, query, is_archive in plan(index):
        calls += 1
        try:
            found = search(key, query, region)
            received += len(found)
            accepted = 0
            for raw in found:
                item = classify_result(raw)
                if not item:
                    continue
                if is_archive and item['year'] not in (2025, 2026):
                    continue
                if not is_archive and item['year'] != 2027:
                    continue
                target = history if is_archive else old
                previous = target.get(item['id'], {})
                item['first_seen'] = previous.get('first_seen', stamp)
                item['last_seen'] = stamp
                if is_archive:
                    item['historical_only'] = True
                    item['flags'].append('Historical evidence only; 2027 opening not implied')
                if not previous:
                    if is_archive: historic += 1
                    else: added += 1
                target[item['id']] = item
                accepted += 1
            coverage[label] = dict(checked_at=stamp, region_searched=region,
                                   raw_results=len(found), matched=accepted, error=None)
        except Exception as exc:
            status = getattr(getattr(exc, 'response', None), 'status_code', None)
            msg = f'HTTP {status}' if status else type(exc).__name__
            errors.append(f'{label}: {msg}')
            coverage[label] = dict(checked_at=stamp, region_searched=region,
                                   matched=None, error=msg)
    targets = [dict(name=n, company=c, region=r, focus=f, url=u)
               for n,c,r,f,u in TARGETS]
    record = dict(at=stamp, requests=calls, received=received,
                  new_jobs=added, new_historical=historic, errors=errors,
                  status='partial' if errors else 'success')
    fresh = dict(jobs=sorted(old.values(), key=lambda x:x['last_seen'], reverse=True)[:500],
                 runs=[record, *(feed.get('runs') or [])][:30], last_scan=stamp,
                 targets=targets, coverage=coverage, scanner_version=2)
    past = dict(postings=sorted(history.values(), key=lambda x:(-x['year'], x['company'])),
                last_scan=stamp, years=[2025, 2026],
                note='Historical employer-domain search results; not current openings.')
    return fresh, past

def main():
    key = os.getenv('SERPAPI_KEY', '')
    if not key:
        raise SystemExit('SERPAPI_KEY missing. No requests made.')
    feed = read_json(FEED, {'jobs':[], 'runs':[]})
    archive = read_json(ARCHIVE, {'postings':[]})
    fresh, past = scan(key, feed, archive)
    ROOT.mkdir(parents=True, exist_ok=True)
    FEED.write_text(json.dumps(fresh, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    ARCHIVE.write_text(json.dumps(past, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    latest = fresh['runs'][0]
    print(f"Requests: {latest['requests']}; raw results: {latest['received']}; "
          f"new 2027: {latest['new_jobs']}; new history: {latest['new_historical']}; "
          f"errors: {len(latest['errors'])}")
    if len(latest['errors']) == latest['requests']:
        raise SystemExit('All searches failed. Results saved for diagnosis.')

if __name__ == '__main__':
    main()
