"""새 블로그 글 뼈대 만들기(2026-11-03). 머리말 · 구조화 데이터 · 메뉴 · 푸터 · 앱 상자까지 사이트 공통으로 채우고,
본문 · 목차 · 출처 자리만 비워 둔다. 쓰는 사람(사람이든 루틴이든)은 그 세 곳만 채우면 된다.
실행:
  python3 tool/new_post.py <slug> --category memorize|daily|basics|parents \\
      --title '영단어 외우는 법 · 오래 남는 네 가지 | 단숙이' \\
      --h1 '영단어, <span class="mark">오래 남게</span> 외우는 법' \\
      --desc '설명 70~130자' --deck '한두 줄 소개' [--headline '검색 결과용 제목(h1에서 태그 뺀 것)']
→ docs/blog/<slug>/index.html (이미 있으면 멈춘다)
채울 곳: <!-- TOC --> · <!-- BODY --> · <!-- REFS --> (주석째로 바꿔 넣기)
"""
import argparse
import datetime as dt
import re
import sys

from blog_common import CATEGORIES, D, SITE, e, page_head, template

STORE = 'https://apps.apple.com/kr/app/id6819707350'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--category', required=True, choices=sorted(CATEGORIES))
    ap.add_argument('--title', required=True)
    ap.add_argument('--h1', required=True)
    ap.add_argument('--desc', required=True)
    ap.add_argument('--deck', required=True)
    ap.add_argument('--headline')
    a = ap.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', a.slug):
        sys.exit('slug는 영어 소문자 · 숫자 · 하이픈만')
    out = D / 'blog' / a.slug / 'index.html'
    if out.exists() or (D / a.slug).exists():
        sys.exit(f'이미 있는 주소: {a.slug}')
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).replace(microsecond=0)
    iso, day = now.isoformat(), now.date().isoformat()
    cat_name, _ = CATEGORIES[a.category]
    url = f'{SITE}blog/{a.slug}/'
    headline = a.headline or re.sub(r'<[^>]+>', '', a.h1).strip()
    org = {'@id': 'https://dansuki.com/#org', '@type': 'Organization', 'name': '단숙이', 'url': SITE}
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': a.title, 'description': a.desc, 'inLanguage': 'ko-KR',
         'isPartOf': {'@id': 'https://dansuki.com/#website'}, 'mainEntity': {'@id': url + '#post'}, 'breadcrumb': {'@id': url + '#crumb'}},
        {'@type': 'BlogPosting', '@id': url + '#post', 'url': url, 'mainEntityOfPage': {'@id': url + '#webpage'},
         'headline': headline, 'description': a.desc, 'inLanguage': 'ko-KR', 'datePublished': iso, 'dateModified': iso,
         'articleSection': cat_name, 'image': {'@type': 'ImageObject', 'url': 'https://dansuki.com/og.jpg'},
         'author': org, 'publisher': {**org, 'logo': {'@type': 'ImageObject', 'url': 'https://dansuki.com/icon.png'}},
         'isPartOf': {'@type': 'Blog', '@id': f'{SITE}blog/#blog', 'name': '단숙이 블로그', 'url': f'{SITE}blog/'}},
        {'@type': 'BreadcrumbList', '@id': url + '#crumb', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': '단숙이', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': '블로그', 'item': f'{SITE}blog/'},
            {'@type': 'ListItem', 'position': 3, 'name': cat_name, 'item': f'{SITE}blog/category/{a.category}/'},
            {'@type': 'ListItem', 'position': 4, 'name': headline, 'item': url}]}]}
    _, _, nav, tail = template()
    head = page_head(url=url, title=a.title, desc=a.desc, ld=ld, published=iso,
                     extra=f'<meta name="dansuki:category" content="{a.category}">')
    store = (f'<a class="store" href="{STORE}" aria-label="App Store에서 단숙이 받기"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.37 12.6c-.02-2.2 1.8-3.26 1.88-3.31-1.03-1.5-2.62-1.7-3.18-1.73-1.35-.14-2.64.8-3.33.8-.69 0-1.74-.78-2.86-.76-1.47.02-2.83.86-3.59 2.17-1.53 2.66-.39 6.59 1.1 8.75.73 1.05 1.6 2.24 2.73 2.2 1.1-.04 1.51-.71 2.84-.71 1.32 0 1.7.71 2.86.69 1.18-.02 1.93-1.07 2.65-2.13.84-1.22 1.18-2.4 1.2-2.46-.03-.01-2.3-.88-2.32-3.5zM14.2 6.13c.6-.73 1.01-1.75.9-2.76-.87.04-1.92.58-2.54 1.31-.56.65-1.05 1.68-.92 2.67.97.08 1.96-.49 2.56-1.22z"/></svg><span><small>App Store에서</small><b>무료로 받기</b></span></a>'
             ' <a class="store gp" href="https://play.google.com/store/apps/details?id=com.dansuki.android" aria-label="Google Play에서 단숙이 받기"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.2 2.6c-.2.2-.3.6-.3 1v16.8c0 .4.1.8.3 1l9.4-9.4zM14.6 13l2.6 2.6-11.1 6.3c-.4.2-.8.3-1.1.2zm3.9-3.9 2.9 1.7c.8.5.8 1.8 0 2.3l-2.9 1.6-2.8-2.8zM6.1 2.1l11.1 6.3L14.6 11 5 1.9c.3-.1.7 0 1.1.2z"/></svg><span><small>Google Play에서</small><b>무료로 받기</b></span></a>')
    body = f'''<main class="research-main"><article class="wrap narrow research-article" id="post">
<header class="article-head"><p class="crumb"><a href="/">단숙이</a> › <a href="/blog/">블로그</a> › <a href="/blog/category/{a.category}/">{e(cat_name)}</a></p><div class="series">{e(cat_name)}</div><h1>{a.h1}</h1><p class="deck">{e(a.deck)}</p><div class="byline">글 · 단숙이를 만든 사람 <span aria-hidden="true">·</span> <time datetime="{day}">{now.year}년 {now.month}월 {now.day}일</time></div></header>
<!-- TOC -->
<!-- BODY -->
<div class="article-app"><h2>하루 20개, <br>단숙이가 순서를 챙겨 줄게요.</h2><p>단숙이는 교육부 기본 어휘로 만든 무료 중고등 영단어 · 숙어 앱이에요. 새 단어는 4초 안에 떠올리는 문제로 익히고, 외운 단어는 2일 · 7일 · 21일 뒤에 다시 물어봐요.</p><p>광고와 가입 없이 바로 시작할 수 있어요. 지금 몇 개 아는지 궁금하면 <a href="/test/">2분 영단어 테스트</a>부터 해 보세요.</p><p>{store} &nbsp; <a href="/try/">1분 체험해 보기</a></p></div>
<section class="article-refs" aria-label="참고 자료"><h2>참고 자료</h2><!-- REFS --><p>단숙이 개발자가 쓴 공부법 글이에요. 연구진이 단숙이를 검증하거나 추천했다는 뜻은 아니고, 앱을 쓰면 성적이 얼마나 오른다고 약속하는 글도 아니에요.</p></section>
</article></main>'''
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(head + nav + body + tail, encoding='utf-8')
    print(f'만듦: {out.relative_to(D.parent)} — <!-- TOC --> · <!-- BODY --> · <!-- REFS --> 를 채우세요')


if __name__ == '__main__':
    main()
