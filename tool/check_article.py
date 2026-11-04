"""공부 글 자동 검수(2026-11-03 콘텐츠 자동화). 사람이 검토하지 않고 올리는 글의 마지막 관문.
하나라도 걸리면 1로 끝나고, 매일 글 루틴은 그 글을 올리지 않는다.
실행: python3 tool/check_article.py docs/<slug>/index.html
"""
import html
import json
import re
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
D = R / 'docs'

# 단숙이 원칙(tool/seo_topics.md '대상과 원칙')을 글자로 막는다
FORBIDDEN = [
    (r'영어책', "'영어책' 대신 '이야기'나 작품 이름"),
    (r'성적(이|을|도)?\s*(오르|올라|올려|향상|보장)', '성적 향상 약속'),
    (r'(등급|점수)(이|을|도)?\s*(오르|올라|올려|보장|확실)', '등급 · 점수 약속'),
    (r'보장(해요|합니다|돼요)|무조건|100\s*% (오르|외워|암기)', '보장 · 과장 표현'),
    (r'지금 안 하면|늦었(어요|다|습니다)|뒤처', '불안 조장'),
    (r'D\s*-\s*day|디데이|D-\d+', '시험일 압박'),
    (r'한정|선착순|마감 임박|곧 유료', '가짜 희소성'),
    (r'[\U0001F300-\U0001FAFF☀-➿]', '이모지'),
]


def text_of(s):
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def body_of(s):
    s = re.sub(r'<!-- blog:related -->.*?<!-- /blog:related -->', ' ', s, flags=re.S)
    a, b = s.find('<article'), s.find('</article>')
    return s[a:b] if a >= 0 and b > a else s


def grams(t, n=5):
    t = re.sub(r'\s+', '', t)
    return {t[i:i + n] for i in range(0, max(0, len(t) - n))}


def main(path):
    f = Path(path)
    s = f.read_text(encoding='utf-8')
    rel = f.resolve().parent.relative_to(D.resolve()).as_posix()  # 'blog/<slug>' 또는 예전 글 '<slug>'
    slug = rel
    art = body_of(s)
    # 글 본문만(앱 소개 상자 · 출처는 빼고) 센다
    main_txt = text_of(re.sub(r'<div class="article-app">.*?</div>|<section class="article-refs".*?</section>', ' ', art, flags=re.S))
    bad = []
    need = lambda ok, msg: ok or bad.append(msg)

    title = html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1)).strip() if '<title>' in s else ''
    desc = (re.search(r'<meta name="description" content="([^"]*)"', s) or [None, ''])[1]
    need(10 <= len(title) <= 60, f'제목 길이 {len(title)}자(10~60)')
    need(70 <= len(html.unescape(desc)) <= 130, f'설명 길이 {len(html.unescape(desc))}자(70~130)')
    need(f'<link rel="canonical" href="https://dansuki.com/{rel}/">' in s, 'canonical 주소가 폴더와 다름')
    need(len(re.findall(r'<h1[\s>]', s)) == 1, 'H1은 하나')
    need(len(re.findall(r'<h2[\s>]', art)) >= 4, 'H2 4개 이상')
    need('class="article-toc"' in art, '목차(nav.article-toc) 없음')
    need('class="article-app"' in art, '앱 소개 상자(div.article-app) 없음')
    need('class="byline"' in art, '바이라인 없음')
    words = len(main_txt.split())
    need(900 <= words <= 2200, f'본문 {words}어절(900~2,200)')

    # 구조화 데이터
    lds = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)]
    types = {n.get('@type') for d in lds for n in d.get('@graph', [d])}
    need(bool(types & {'Article', 'BlogPosting'}) and 'BreadcrumbList' in types, f'구조화 데이터에 BlogPosting(또는 Article) · BreadcrumbList 필요(지금 {sorted(t for t in types if t)})')

    # 링크: 사이트 안 3개 이상, 바깥 출처 1개 이상
    hrefs = re.findall(r'<a [^>]*href="([^"]+)"', art)
    inner = {h for h in hrefs if h.startswith('/') and not h.startswith('//')}
    outer = {h for h in hrefs if h.startswith('http') and 'dansuki.com' not in h and 'apps.apple.com' not in h and 'play.google.com' not in h}
    need(len(inner) >= 3, f'사이트 안 링크 {len(inner)}개(3개 이상)')
    refs = re.search(r'<section class="article-refs".*?</section>', art, re.S)
    need(refs and re.search(r'href="https?://', refs.group(0)), '출처(section.article-refs)에 바깥 링크 없음')
    need(len(outer) >= 1, '바깥 출처 링크 0개')

    # 메뉴 · 푸터는 사이트 공통(공부 글 모음 페이지와 똑같아야 함). 새 글이 메뉴에 칸을 늘리지 않게.
    ref = (D / 'blog/index.html').read_text(encoding='utf-8')
    nav_of = lambda x: re.sub(r'\s+|aria-current="page"', '', (re.search(r'<nav class="top">.*?</nav>', x, re.S) or [''])[0])
    foot_of = lambda x: re.sub(r'\s+', '', (re.search(r'<footer class="site">.*?</footer>', x, re.S) or [''])[0])
    need(nav_of(s) == nav_of(ref), '상단 메뉴가 사이트 공통 메뉴와 다름(메뉴는 고치지 말 것)')
    need(foot_of(s) == foot_of(ref), '푸터가 사이트 공통 푸터와 다름(푸터는 고치지 말 것)')

    # 금지 표현
    whole = text_of(art)
    for pat, why in FORBIDDEN:
        m = re.search(pat, whole)
        if m:
            bad.append(f'금지 표현({why}): "…{whole[max(0, m.start() - 15):m.end() + 15]}…"')

    # 다른 글과 너무 비슷하면 안 됨(글자 5개 묶음 겹침)
    mine = grams(main_txt)
    for g in [*D.glob('*/index.html'), *D.glob('blog/*/index.html')]:
        grel = g.resolve().parent.relative_to(D.resolve()).as_posix()
        if grel == rel or g.parent.name in ('words', 'articles', 'test', 'try', 'blog', 'category', 'page'):
            continue
        other = grams(text_of(body_of(g.read_text(encoding='utf-8'))))
        if mine and other:
            j = len(mine & other) / len(mine | other)
            need(j < 0.30, f'{g.parent.name}/와 너무 비슷함(겹침 {j:.0%})')

    print(f'{slug}: 제목 {len(title)}자 · 설명 {len(html.unescape(desc))}자 · 본문 {words}어절 · 안 링크 {len(inner)} · 바깥 출처 {len(outer)}')
    for b in bad:
        print('  ✗', b)
    if bad:
        sys.exit(1)
    print('  검수 통과')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('사용: python3 tool/check_article.py docs/<slug>/index.html')
    main(sys.argv[1])
