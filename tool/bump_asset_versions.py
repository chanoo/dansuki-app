"""공통 파일(CSS · 글꼴 · 스크립트)의 ?v= 를 파일 내용 해시로 맞춘다(2026-11-03 콘텐츠 자동화).
GitHub Pages는 10분 캐시라 파일을 바꾸면 ?v= 를 올려야 바로 보인다. 사람이 날짜를 손으로 올리던 것을 자동으로.
순서: 글꼴 → (글꼴 주소가 든) site.css → 나머지 CSS · JS → 모든 HTML과 생성기(tool/build_word_pages.py).
실행: python3 tool/bump_asset_versions.py   → 'changed N files'
"""
import hashlib
import re
from pathlib import Path

R = Path(__file__).resolve().parent.parent
D = R / 'docs'
# (사이트 안 경로, 주소에 쓰는 이름 패턴)
ASSETS = ['fonts/MaruBuri-sub.woff2', 'site.css', 'article.css', 'words/w.css', 'navigation.js']


def ver(rel):
    return hashlib.sha1((D / rel).read_bytes()).hexdigest()[:8]


def swap(text, rel, v):
    name = re.escape(rel.split('/')[-1])
    # /fonts/MaruBuri-sub.woff2?v=… · fonts/MaruBuri-sub.woff2?v=… · /site.css?v=…
    return re.sub(rf'({name}\?v=)[0-9A-Za-z]+', rf'\g<1>{v}', text)


def main():
    changed = 0
    targets = [p for p in D.rglob('*.html')] + [D / 'site.css', R / 'tool/build_word_pages.py']
    cache = {p: p.read_text(encoding='utf-8') for p in targets if p.exists()}
    for rel in ASSETS:
        if not (D / rel).exists():
            continue
        v = ver(rel)
        for p, t in cache.items():
            n = swap(t, rel, v)
            if n != t:
                cache[p] = n
                if p == D / 'site.css':  # site.css 안의 글꼴 주소가 바뀌면 site.css 해시도 달라진다 → 바로 저장
                    p.write_text(n, encoding='utf-8')
    for p, t in cache.items():
        if p.read_text(encoding='utf-8') != t:
            p.write_text(t, encoding='utf-8')
            changed += 1
    print('changed', changed, 'files')


if __name__ == '__main__':
    main()
