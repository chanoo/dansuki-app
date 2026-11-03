"""블로그 공통 부품(2026-11-03). register_articles.py(블로그 빌드)와 new_post.py(새 글 뼈대)가 함께 쓴다.
사이트 공통 머리말 · 메뉴 · 푸터는 docs/spaced-review/index.html에서 빌려 온다(손으로 만든 원본이라 생성기에 덮이지 않음).
"""
import html
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parent.parent
D = R / 'docs'
SITE = 'https://dansuki.com/'
e = lambda s: html.escape(s, quote=True)

# 카테고리: 이름 · 주소 · 한 줄 소개
CATEGORIES = {
    'memorize': ('외우는 법', '떠올리기 · 간격 복습 · 소리 내어 읽기처럼 오래 남는 방법'),
    'daily': ('하루 분량', '하루에 몇 개, 복습까지 몇 분 — 끊기지 않는 양 정하기'),
    'basics': ('기초 다지기', '교육부 기본 어휘부터, 비어 있는 단어 채우기'),
    'parents': ('학부모', '아이 영단어 공부를 곁에서 돕는 법'),
}
# 블로그 폴더 밖에 먼저 생긴 글(주소는 그대로 두고 블로그 목록에만 넣는다)
LEGACY = {
    'middle-school-words': 'daily',
    'spaced-review': 'memorize',
    'method': 'memorize',
    'difficulty': 'memorize',
    'basic-words': 'basics',
}


def template():
    t = (D / 'spaced-review/index.html').read_text(encoding='utf-8')
    head = t[:t.index('<script type="application/ld+json">')]
    # 머리말 꼬리(navigation.js · robots · 트위터 대체 글 등): 구조화 데이터 뒤 ~ </head>
    after = t.index('</script>', t.index('<script type="application/ld+json">')) + len('</script>')
    head_tail = t[after:t.index('</head>')]
    nav = t[t.index('<nav class="top">'):t.index('<main')].replace(' aria-current="page"', '')
    tail = t[t.index('</article></main>') + len('</article></main>'):]
    return head, head_tail, nav, tail


def page_head(*, url, title, desc, og_type='article', image='https://dansuki.com/og.jpg', ld=None, extra='', published=None):
    head, head_tail, _, _ = template()
    sub = lambda pat, rep, s: re.sub(pat, lambda m: rep, s, flags=re.S)
    head = sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', head)
    head = sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', head)
    head = sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head)
    head = sub(r'<meta property="og:type" content="[^"]*">', f'<meta property="og:type" content="{og_type}">', head)
    for k, v in (('og:url', url), ('og:title', title), ('og:description', desc), ('og:image', image)):
        head = sub(rf'<meta property="{k}" content="[^"]*">', f'<meta property="{k}" content="{e(v)}">', head)
    for k, v in (('twitter:title', title), ('twitter:description', desc), ('twitter:image', image)):
        head = sub(rf'<meta name="{k}" content="[^"]*">', f'<meta name="{k}" content="{e(v)}">', head)
    head = re.sub(r'<meta property="og:image:(alt|width|height)" content="[^"]*">', '', head)
    head = re.sub(r'<meta property="article:[a-z_]+" content="[^"]*">', '', head)
    if published:
        head += f'<meta property="article:published_time" content="{published}">'
    head += f'<link rel="alternate" type="application/rss+xml" title="단숙이 블로그" href="{SITE}blog/rss.xml">'
    ld_html = f'<script type="application/ld+json">\n{json.dumps(ld, ensure_ascii=False, indent=2)}\n</script>' if ld else ''
    head_tail = re.sub(r'<meta name="twitter:image:alt" content="[^"]*">', '', head_tail)
    head_tail = re.sub(r'<meta property="article:modified_time" content="[^"]*">', '', head_tail)
    return head + extra + ld_html + head_tail + '</head><body>'


def meta(s, prop=None, name=None):
    key = f'property="{prop}"' if prop else f'name="{name}"'
    m = re.search(rf'<meta {key} content="([^"]*)"', s)
    return html.unescape(m.group(1)) if m else ''
