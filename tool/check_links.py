"""사이트 안 링크 점검(2026-11-03 SEO 자동화). docs/의 HTML에서 같은 사이트로 가는 href · src를 모아
실제 파일이 있는지, #앵커가 그 페이지에 있는지 본다. 바깥 링크는 보지 않는다(CI가 느려지고 남의 서버를 두드림).
실행: python3 tool/check_links.py   → 문제가 있으면 목록을 찍고 1로 끝난다.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

D = Path(__file__).resolve().parent.parent / 'docs'
HOSTS = {'dansuki.com', 'www.dansuki.com'}
SKIP_DIRS = {'threads', 'fonts', 'vocab', 'stories'}


class Collect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids = [], set()
        self._script = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'script':
            self._script = True
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'a' and a.get('name'):
            self.ids.add(a['name'])
        for k in ('href', 'src'):
            v = a.get(k)
            if v and not (tag == 'link' and a.get('rel') in ('preconnect', 'dns-prefetch')):
                self.links.append((tag, v))
        if tag == 'source' and a.get('srcset'):
            for part in a['srcset'].split(','):
                self.links.append((tag, part.strip().split(' ')[0]))

    def handle_endtag(self, tag):
        if tag == 'script':
            self._script = False


def target(url):
    """사이트 안 주소면 docs 안 파일 경로와 앵커, 아니면 None."""
    u = urlsplit(url)
    if u.scheme in ('mailto', 'tel', 'sms', 'javascript', 'data'):
        return None
    if u.scheme in ('http', 'https') and u.netloc not in HOSTS:
        return None
    return unquote(u.path), u.fragment


def resolve(page, path):
    if not path:
        return page
    base = D if path.startswith('/') else page.parent
    p = (base / path.lstrip('/')).resolve()
    if p.is_dir() or path.endswith('/'):
        p = p / 'index.html'
    return p


def main():
    pages = [p for p in D.rglob('*.html') if not (set(p.relative_to(D).parts[:-1]) & SKIP_DIRS)]
    parsed = {}
    for p in pages:
        c = Collect()
        c.feed(p.read_text(encoding='utf-8'))
        parsed[p.resolve()] = c
    bad = []
    for p, c in parsed.items():
        for tag, url in c.links:
            if '${' in url:  # 스크립트 템플릿 문자열
                continue
            t = target(url)
            if not t:
                continue
            path, frag = t
            f = resolve(p, path)
            rel = p.relative_to(D.resolve())
            if not f.exists():
                bad.append(f'{rel}: 없는 파일 {url}')
                continue
            if frag and f.suffix == '.html' and tag == 'a':
                ids = parsed[f].ids if f in parsed else set()
                if f not in parsed:
                    c2 = Collect(); c2.feed(f.read_text(encoding='utf-8')); ids = c2.ids
                if frag not in ids:
                    bad.append(f'{rel}: {url} — #{frag} 앵커가 없음')
    print(f'페이지 {len(parsed)}개, 사이트 안 링크 확인')
    for b in sorted(set(bad)):
        print('  ✗', b)
    if bad:
        sys.exit(1)
    print('  깨진 링크 없음')


if __name__ == '__main__':
    main()
