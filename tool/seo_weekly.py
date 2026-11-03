"""주간 SEO 리포트(2026-11-03 SEO 자동화). 실제 사이트를 둘러보고 마크다운 한 장을 찍는다.
- 사이트맵의 모든 주소: 응답 코드 · 응답 시간 · 크기 · 제목 · 설명 길이 · noindex 여부
- 로컬 점검(check_seo · check_links) 결과
- PageSpeed Insights(모바일) 점수와 LCP · CLS · TBT: 키(PSI_API_KEY)가 있으면 더 안정적으로
- 지난 리포트와 비교할 숫자는 CI가 이슈로 쌓아 둔다
실행: python3 tool/seo_weekly.py > report.md
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

R = Path(__file__).resolve().parent.parent
SITE = 'https://dansuki.com/'
UA = 'Mozilla/5.0 (compatible; dansuki-seo-weekly/1.0; +https://dansuki.com/)'
PSI_PAGES = ['', 'basic-words/', 'test/', 'middle-school-words/']


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return r.status, (time.time() - t) * 1000, body
    except urllib.error.HTTPError as e:
        return e.code, (time.time() - t) * 1000, b''
    except Exception:
        return 0, (time.time() - t) * 1000, b''


def meta(html):
    t = re.search(r'<title>(.*?)</title>', html, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', html)
    robots = re.search(r'<meta name="robots" content="([^"]*)"', html)
    return (t.group(1).strip() if t else ''), (d.group(1) if d else ''), (robots.group(1) if robots else '')


def local(cmd):
    p = subprocess.run([sys.executable, *cmd], cwd=R, capture_output=True, text=True)
    out = (p.stdout + p.stderr).strip()
    return p.returncode == 0, out


def psi(path):
    q = {'url': SITE + path, 'strategy': 'mobile', 'category': 'performance'}
    if os.environ.get('PSI_API_KEY'):
        q['key'] = os.environ['PSI_API_KEY']
    code, _, body = get('https://www.googleapis.com/pagespeedonline/v5/runPagespeed?' + urllib.parse.urlencode(q), timeout=90)
    if code != 200:
        return None, f'PSI {code}'
    j = json.loads(body)
    lh = j.get('lighthouseResult', {})
    a = lh.get('audits', {})
    score = round((lh.get('categories', {}).get('performance', {}).get('score') or 0) * 100)
    val = lambda k: a.get(k, {}).get('displayValue', '-')
    field = j.get('loadingExperience', {}).get('overall_category', '데이터 없음')
    return score, f"LCP {val('largest-contentful-paint')} · CLS {val('cumulative-layout-shift')} · TBT {val('total-blocking-time')} · 실사용 {field}"


def main():
    today = time.strftime('%Y-%m-%d', time.gmtime(time.time() + 9 * 3600))
    sm_code, _, sm = get(SITE + 'sitemap.xml')
    urls = re.findall(r'<loc>([^<]+)</loc>', sm.decode('utf-8', 'replace')) if sm_code == 200 else []
    lines = [f'# SEO 주간 리포트 · {today}', '']
    problems = []

    # 1) 로컬 점검
    ok1, out1 = local(['tool/check_seo.py'])
    ok2, out2 = local(['tool/check_links.py'])
    lines += ['## 점검', f'- SEO 점검: {"✅ 통과" if ok1 else "❌ 실패"}', f'- 사이트 안 링크: {"✅ 깨진 링크 없음" if ok2 else "❌ 깨진 링크 있음"}']
    if not ok1:
        problems.append('SEO 점검 실패'); lines += ['```', out1[-1500:], '```']
    if not ok2:
        problems.append('깨진 링크'); lines += ['```', out2[-1500:], '```']
    for f in ['robots.txt', 'llms.txt']:
        c, _, _ = get(SITE + f)
        lines.append(f'- /{f}: {c}')
        if c != 200:
            problems.append(f'/{f} {c}')
    lines.append('')

    # 2) 실제 페이지
    lines += ['## 페이지', f'사이트맵 주소 {len(urls)}개', '', '| 주소 | 응답 | 시간 | 크기 | 제목 길이 | 설명 길이 |', '|---|---|---|---|---|---|']
    for u in urls:
        code, ms, body = get(u)
        html = body.decode('utf-8', 'replace')
        title, desc, robots = meta(html)
        flag = ''
        if code != 200:
            problems.append(f'{u} 응답 {code}'); flag = ' ❌'
        if 'noindex' in robots:
            problems.append(f'{u} noindex'); flag = ' ⚠️ noindex'
        if not title or not desc:
            problems.append(f'{u} 제목 · 설명 없음')
        lines.append(f'| {u.replace(SITE, "/")}{flag} | {code} | {ms:.0f}ms | {len(body) / 1024:.0f}KB | {len(title)} | {len(desc)} |')
    # 단어별 페이지: 사이트맵 개수와 무작위 10개 응답
    wc, _, wsm = get(SITE + 'sitemap-words.xml')
    wurls = re.findall(r'<loc>([^<]+)</loc>', wsm.decode('utf-8', 'replace')) if wc == 200 else []
    import random
    sample = random.sample(wurls, min(10, len(wurls)))
    bad = [u for u in sample if get(u)[0] != 200]
    lines += ['', f'단어별 페이지: 사이트맵 {len(wurls):,}개, 무작위 {len(sample)}개 중 응답 실패 {len(bad)}개' + (' ✅' if not bad else ' ❌')]
    if wc != 200 or bad:
        problems.append(f'단어 페이지 문제({wc}, 실패 {len(bad)})')
    lines.append('')

    # 3) 속도
    lines += ['## 속도(PageSpeed 모바일)', '']
    for p in PSI_PAGES:
        score, detail = psi(p)
        if score is None:
            lines.append(f'- /{p}: 측정 못 함({detail}). PSI_API_KEY를 넣으면 안정적으로 잴 수 있어요.')
        else:
            lines.append(f'- /{p}: **{score}점** · {detail}')
            if score < 70:
                problems.append(f'/{p} 속도 {score}점')
    lines.append('')

    lines += ['## 요약', ('- 이번 주 문제 없음 ✅' if not problems else '\n'.join(f'- ❌ {x}' for x in problems)), '',
              '검색 노출(Search Console · 네이버 서치어드바이저) 숫자는 아직 연결 전이에요. 연결하면 여기에 검색어 · 클릭 · 노출이 붙어요.']
    print('\n'.join(lines))
    Path(os.environ.get('SEO_PROBLEMS_FILE', '/dev/null')).write_text(str(len(problems)))


if __name__ == '__main__':
    main()
