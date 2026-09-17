"""Idempotently add a safe scan button and archive link without rewriting UI."""
from pathlib import Path

HTML=Path(__file__).resolve().parent/'public'/'index.html'
MARKER='<script src="/scan-control.js" defer></script>'
ARCHIVE='<a class="tab" href="/archive.html">往年岗位</a>'

def patch(text):
    if MARKER not in text:
        if '</body>' not in text:raise ValueError('Main HTML has no closing body')
        text=text.replace('</body>',MARKER+'</body>',1)
    if ARCHIVE not in text:
        start='<nav class="tabs" aria-label="页面">'
        if start not in text:raise ValueError('Main navigation not found')
        before,tail=text.split(start,1)
        if '</nav>' not in tail:raise ValueError('Main navigation closing tag not found')
        text=before+start+tail.replace('</nav>',ARCHIVE+'</nav>',1)
    return text

if __name__=='__main__':
    original=HTML.read_text(encoding='utf-8');updated=patch(original)
    if updated!=original:
        HTML.write_text(updated,encoding='utf-8')
        print('Installed scan button and archive link into original homepage.')
    else:print('Scan UI already installed.')
