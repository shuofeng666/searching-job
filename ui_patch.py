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
GOOGLE_UXR_MARKER="id:'official-google-uxr-us-2027'"
GOOGLE_UXR=("SEED.push({id:'official-google-uxr-us-2027',"
 "title:'User Experience Research Intern, PhD, Summer 2027',"
 "company:'Google',location:'United States · multiple locations',region:'US',"
 "url:'https://www.google.com/about/careers/applications/jobs/results/137409539979780806-user-experience-research-intern-phd-summer-2027',"
 "description:'博士 UX Research 实习，包含独立研究、用户访谈、可用性实验和数据分析。具体 HCI Research 团队及论文机会未在岗位中保证。官网要求符合在读博士及毕业时间条件。',"
 "deadline:'2027-02-26',deadline_kind:'rolling',"
 "date_note:'Google 官方页面写明请在 2027-02-26 前申请，滚动审核，可提前结束。请在申请前再次核实。',"
 "topics:['HCI','UX Research'],kind:'official',first_seen:'2026-09-17',"
 "source:'Google Careers 官方招聘 · 2026-09-17 来源核查',"
 "flags:['滚动审核可能提前关闭','需要核实博士预计毕业日期与岗位申请资格','不保证分配至学术研究组或发表论文']});\n")

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
    # Only insert into the known homepage with an existing SEED array. Do not
    # touch test fixtures or any unfamiliar page layout.
    anchor='const $=id=>'
    if GOOGLE_UXR_MARKER not in text and 'const SEED=[' in text and anchor in text:
        text=text.replace(anchor,GOOGLE_UXR+anchor,1)
    return text

if __name__=='__main__':
    original=HTML.read_text(encoding='utf-8');updated=patch(original)
    if updated!=original:
        HTML.write_text(updated,encoding='utf-8')
        print('Installed research radar and evidence-backed Google UX research internship.')
    else:print('Research UI is already installed.')
