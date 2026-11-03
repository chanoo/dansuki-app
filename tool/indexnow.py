"""바뀐 페이지를 IndexNow로 검색엔진에 알린다(2026-11-03 SEO 자동화).
- api.indexnow.org: Bing · Yandex · Seznam 등 IndexNow 참여 엔진이 서로 나눠 받는다.
- searchadvisor.naver.com/indexnow: 네이버.
키 파일은 docs/<KEY>.txt(사이트 맨 위에 그 키 한 줄). 사이트맵에 있는 주소만 보낸다.
실행: python3 tool/indexnow.py <바뀐 파일 경로 ...>   (CI는 git diff로 바뀐 docs/ 파일을 넘긴다)
      python3 tool/indexnow.py --all                  (사이트맵 전체)
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

R = Path(__file__).resolve().parent.parent
D = R / 'docs'
HOST = 'dansuki.com'
KEY = next(p.stem for p in D.glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}', p.stem))
ENDPOINTS = ['https://api.indexnow.org/indexnow', 'https://searchadvisor.naver.com/indexnow']


def sitemap_urls():
    out = []
    for name in ('sitemap.xml', 'sitemap-words.xml'):
        f = D / name
        if f.exists():
            out += re.findall(r'<loc>([^<]+)</loc>', f.read_text(encoding='utf-8'))
    return out


def url_of(path):
    """docs/basic-words/index.html → https://dansuki.com/basic-words/"""
    p = Path(path)
    try:
        rel = p.resolve().relative_to(D.resolve()).as_posix()
    except ValueError:
        rel = p.as_posix().removeprefix('docs/')
    if rel.endswith('index.html'):
        rel = rel[:-len('index.html')]
    return f'https://{HOST}/{rel}'


def main(args):
    allowed = set(sitemap_urls())
    if args == ['--all']:
        urls = sorted(allowed)
    else:
        urls = sorted({u for u in map(url_of, args) if u in allowed})
        # 사이트맵 자체나 공통 CSS · 글꼴만 바뀌었으면 보낼 페이지가 없다.
    if not urls:
        print('보낼 주소 없음')
        return 0
    body = json.dumps({'host': HOST, 'key': KEY, 'keyLocation': f'https://{HOST}/{KEY}.txt', 'urlList': urls}).encode()
    ok = 0
    for ep in ENDPOINTS:
        req = urllib.request.Request(ep, data=body, headers={'Content-Type': 'application/json; charset=utf-8'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                print(ep, r.status, f'{len(urls)}개')
                ok += 1
        except urllib.error.HTTPError as e:
            # 202(받음 · 확인 중)도 성공. 403 키 확인 실패 · 422 주소 문제 · 429 너무 잦음.
            print(ep, e.code, e.read()[:200].decode('utf-8', 'replace'))
            ok += e.code in (200, 202)
        except Exception as e:  # 네트워크 문제는 배포를 막지 않는다
            print(ep, 'error', e)
    for u in urls:
        print('  ', u)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
