"""Remove legacy false positives without spending SerpApi credits or altering scan history."""
from __future__ import annotations
import json
from scanner_v4 import FEED, ARCHIVE, _research_record, read_json


def cleaned(feed, archive):
    def valid_current(x):
        return isinstance(x,dict) and x.get('year')==2027 and _research_record(x) and str(x.get('source','')).startswith('Employer-domain')
    def valid_watch(x):
        return isinstance(x,dict) and x.get('year') is None and _research_record(x) and str(x.get('source','')).startswith('Employer-domain')
    def valid_history(x):
        return isinstance(x,dict) and x.get('year') in (2025,2026) and _research_record(x) and str(x.get('source','')).startswith('Employer-domain')
    feed=dict(feed);archive=dict(archive)
    feed['jobs']=[x for x in feed.get('jobs',[]) if valid_current(x)]
    feed['watch_leads']=[x for x in feed.get('watch_leads',[]) if valid_watch(x)]
    archive['postings']=[x for x in archive.get('postings',[]) if valid_history(x)]
    return feed,archive


def main():
    feed=read_json(FEED,{'jobs':[]});archive=read_json(ARCHIVE,{'postings':[]})
    new_feed,new_archive=cleaned(feed,archive)
    removed=(len(feed.get('jobs',[]))-len(new_feed['jobs'])+
             len(feed.get('watch_leads',[]))-len(new_feed['watch_leads'])+
             len(archive.get('postings',[]))-len(new_archive['postings']))
    if removed:
        FEED.write_text(json.dumps(new_feed,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        ARCHIVE.write_text(json.dumps(new_archive,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Offline cleanup removed {removed} invalid leads; no paid searches run.')

if __name__=='__main__':main()
