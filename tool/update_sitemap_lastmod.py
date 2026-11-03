"""sitemap.xml의 lastmod를 페이지 파일이 마지막으로 바뀐 날(git 커밋 날짜, 한국 시간)로 맞춘다(2026-11-03 SEO 자동화).
실행: python3 tool/update_sitemap_lastmod.py   → 바뀐 줄이 있으면 고쳐 쓰고 'changed N'을 찍는다.
CI(.github/workflows/seo.yml)가 푸시마다 돌린다. git 기록이 있어야 해서 checkout은 fetch-depth: 0.
"""
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

R = Path(__file__).resolve().parent.parent
SM = R / 'docs/sitemap.xml'


def page_file(url):
    path = urlsplit(url).path.lstrip('/')
    p = R / 'docs' / path
    return p / 'index.html' if (not path or path.endswith('/')) else p


def last_day(f):
    out = subprocess.run(['git', 'log', '-1', '--format=%cd', '--date=format-local:%Y-%m-%d', '--', str(f)],
                         cwd=R, capture_output=True, text=True, env={'TZ': 'Asia/Seoul', 'PATH': '/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin'})
    return out.stdout.strip()


def main():
    s = SM.read_text(encoding='utf-8')
    n = 0

    def fix(m):
        nonlocal n
        url, old = m.group(2), m.group(4)
        day = last_day(page_file(url))
        if day and day != old:
            n += 1
            return f'{m.group(1)}{url}{m.group(3)}{day}{m.group(5)}'
        return m.group(0)

    s2 = re.sub(r'(<loc>)([^<]+)(</loc>\s*<lastmod>)([^<]+)(</lastmod>)', fix, s)
    if n:
        SM.write_text(s2, encoding='utf-8')
    print('changed', n)


if __name__ == '__main__':
    main()
