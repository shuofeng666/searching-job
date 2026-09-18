"""Idempotent, narrowly scoped changes to existing HCI Deadlines-style homepage."""
from pathlib import Path

HTML=Path(__file__).resolve().parent/'public'/'index.html'
MARKER='<script src="/scan-control.js" defer></script>'
EXPERIENCE='<script src="/radar-experience.js" defer></script>'
ARCHIVE='<a class="tab" href="/archive.html">往年岗位</a>'
BAD_SOURCE="return [...store.manual,...SEED,...(feed.jobs||[])].map(normalize).filter(j=>{const key="
GOOD_SOURCE="return [...store.manual,...SEED,...(feed.jobs||[])].map(normalize).filter(j=>!/(?:product (?:design|management)|algorithm|foundation model|machine learning engineer)/i.test(j.title||'')).filter(j=>{const key="
OLD_BADGE="let flag=j.kind==='official'?'官方岗位页面':'搜索线索，未核实';"
NEW_BADGE="let flag=j.kind==='official'?'官方招聘链接 · 开放状态待核实':'搜索线索，未核实';"

def patch(text):
    if '</body>' not in text:raise ValueError('Main HTML has no closing body')
    for marker in (MARKER, EXPERIENCE):
        if marker not in text:text=text.replace('</body>',marker+'</body>',1)
    if ARCHIVE not in text:
        start='<nav class="tabs" aria-label="页面">'
        if start not in text:raise ValueError('Main navigation not found')
        before,tail=text.split(start,1)
        if '</nav>' not in tail:raise ValueError('Main navigation closing tag not found')
        text=before+start+tail.replace('</nav>',ARCHIVE+'</nav>',1)
    if BAD_SOURCE in text:text=text.replace(BAD_SOURCE,GOOD_SOURCE,1)
    if OLD_BADGE in text:text=text.replace(OLD_BADGE,NEW_BADGE,1)
    return text

if __name__=='__main__':
    original=HTML.read_text(encoding='utf-8');updated=patch(original)
    if updated!=original:
        HTML.write_text(updated,encoding='utf-8')
        print('Installed personal research queue and accurate job labels.')
    else:print('Research UI is already installed.')
