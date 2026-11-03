"""공부 글을 사이트에 자동 등록한다(2026-11-03 콘텐츠 자동화).
docs/<폴더>/index.html 중 og:type이 article이고 noindex가 아닌 글을 찾아
1) sitemap.xml에 없으면 넣고(lastmod = 글의 article:published_time 날짜)
2) '공부 글 모음' 허브 docs/articles/index.html을 새로 그리고(최신 글이 위)
3) docs/llms.txt의 '## 공부 글' 묶음을 다시 쓴다.
매일 글 초안 루틴과 사람이 새 글을 넣을 때 돌린다. 실행: python3 tool/register_articles.py
"""
import html
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parent.parent
D = R / 'docs'
SITE = 'https://dansuki.com/'
INCLUDE = {'method', 'difficulty'}  # og:type은 website지만 공부 글로 모음에 넣는다
SKIP = {'test', 'articles', 'words', 'try', 'stories', 'vocab', 'threads', 'img', 'fonts'}
e = lambda s: html.escape(s, quote=True)


def meta(s, prop=None, name=None):
    key = f'property="{prop}"' if prop else f'name="{name}"'
    m = re.search(rf'<meta {key} content="([^"]*)"', s)
    return html.unescape(m.group(1)) if m else ''


def articles():
    out = []
    for f in sorted(D.glob('*/index.html')):
        if f.parent.name in SKIP:
            continue
        s = f.read_text(encoding='utf-8')
        if (meta(s, prop='og:type') != 'article' and f.parent.name not in INCLUDE) or 'noindex' in meta(s, name='robots'):
            continue
        title = re.sub(r'\s*\|\s*단숙이.*$', '', html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1)).strip())
        pub = meta(s, prop='article:published_time') or ''
        if not pub:
            m = re.search(r'"datePublished":\s*"([^"]+)"', s)
            if not m:
                m = re.search(rf'<loc>{re.escape(SITE + f.parent.name)}/</loc>\s*<lastmod>([^<]+)</lastmod>', (D / 'sitemap.xml').read_text(encoding='utf-8'))
            pub = m.group(1) if m else '2026-10-01'
        out.append({'slug': f.parent.name, 'title': title, 'desc': meta(s, name='description'), 'date': pub[:10]})
    return sorted(out, key=lambda a: (a['date'], a['slug']), reverse=True)


def update_sitemap(items):
    p = D / 'sitemap.xml'
    s = p.read_text(encoding='utf-8')
    added = 0
    for a in items + [{'slug': 'articles', 'date': items[0]['date'] if items else '2026-11-03'}]:
        loc = f'{SITE}{a["slug"]}/'
        if f'<loc>{loc}</loc>' not in s:
            s = s.replace('</urlset>', f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{a["date"]}</lastmod>\n  </url>\n</urlset>')
            added += 1
    p.write_text(s, encoding='utf-8')
    return added


def build_hub(items):
    tpl = (D / 'spaced-review/index.html').read_text(encoding='utf-8')
    head = tpl[:tpl.index('<script type="application/ld+json">')]
    nav = tpl[tpl.index('<nav class="top">'):tpl.index('<main')].replace(' aria-current="page"', '')
    tail = tpl[tpl.index('</article></main>') + len('</article></main>'):]
    title = '영단어 공부 글 모음 | 단숙이'
    desc = f'영단어 외우는 법, 하루 분량, 복습 간격, 교육부 기본 어휘까지 단숙이가 정리한 공부 글 {len(items)}편을 한곳에 모았어요.'
    url = SITE + 'articles/'
    head = re.sub(r'<title>.*?</title>', f'<title>{e(title)}</title>', head, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', head)
    head = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', head)
    for k, v in (('og:url', url), ('og:title', title), ('og:description', desc)):
        head = re.sub(rf'<meta property="{k}" content="[^"]*">', f'<meta property="{k}" content="{e(v)}">', head)
    head = head.replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">')
    for k, v in (('twitter:title', title), ('twitter:description', desc)):
        head = re.sub(rf'<meta name="{k}" content="[^"]*">', f'<meta name="{k}" content="{e(v)}">', head)
    head = re.sub(r'<meta property="article:[a-z_]+" content="[^"]*">', '', head)
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', '@id': url + '#webpage', 'url': url, 'name': title, 'description': desc, 'inLanguage': 'ko-KR',
         'isPartOf': {'@id': 'https://dansuki.com/#website'},
         'mainEntity': {'@type': 'ItemList', 'itemListElement': [
             {'@type': 'ListItem', 'position': i + 1, 'url': f'{SITE}{a["slug"]}/', 'name': a['title']} for i, a in enumerate(items)]}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': '단숙이', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': '공부 글 모음', 'item': url}]}]}
    cards = ''.join(
        f'<li><a href="/{a["slug"]}/"><b>{e(a["title"])}</b><span>{e(a["desc"])}</span><time datetime="{a["date"]}">{a["date"].replace("-", ". ")}</time></a></li>'
        for a in items)
    css = '''<style>
.hub{list-style:none;margin:24px 0 0;padding:0;display:grid;gap:12px}
.hub a{display:grid;gap:6px;padding:18px 20px;border-radius:18px;background:var(--surface);border:1px solid var(--line);text-decoration:none;color:var(--text)}
.hub a:hover{border-color:var(--text)}
.hub b{font-family:'MaruBuri',serif;font-weight:400;font-size:20px;line-height:1.4}
.hub span{color:var(--muted);font-size:15px}
.hub time{color:var(--faint);font-size:13px}
</style>'''
    body = f'''<main class="research-main"><article class="wrap narrow research-article" id="post">
<header class="article-head"><p class="crumb"><a href="/">단숙이</a> › 공부 글 모음</p><div class="series">영단어 공부 · {len(items)}편</div><h1>영단어 공부 글 <span class="mark">모음</span></h1><p class="deck">외우는 법, 하루에 몇 개, 언제 다시 볼지. <br>단숙이가 정리한 공부 글을 한곳에 모았어요.</p></header>
<ul class="hub">{cards}</ul>
<p style="margin-top:28px">지금 몇 개 아는지 궁금하면 <a href="/test/">2분 영단어 테스트</a>, 전체 단어는 <a href="/basic-words/">교육부 기본 어휘 3000 목록</a>에서 볼 수 있어요.</p>
</article></main>'''
    page = head + css + f'<script type="application/ld+json">\n{json.dumps(ld, ensure_ascii=False, indent=2)}\n</script><script src="/navigation.js?v=1058b464" defer></script><meta name="robots" content="index, follow, max-image-preview:large"></head><body>' + nav + body + tail
    page = page.replace('</head><body></head><body>', '</head><body>')
    (D / 'articles').mkdir(exist_ok=True)
    (D / 'articles/index.html').write_text(page, encoding='utf-8')


def update_llms(items):
    p = D / 'llms.txt'
    s = p.read_text(encoding='utf-8')
    block = '<!-- articles:start (tool/register_articles.py가 다시 씀) -->\n' + '\n'.join(
        f'- [{a["title"]}]({SITE}{a["slug"]}/): {a["desc"]}' for a in items) + '\n<!-- articles:end -->'
    if '<!-- articles:start' in s:
        s = re.sub(r'<!-- articles:start.*?<!-- articles:end -->', block, s, flags=re.S)
    else:
        s = s.replace('## Optional', f'## 공부 글\n\n- [영단어 공부 글 모음]({SITE}articles/)\n{block}\n\n## Optional', 1)
    p.write_text(s, encoding='utf-8')


def main():
    items = articles()
    added = update_sitemap(items)
    build_hub(items)
    update_llms(items)
    print(f'articles {len(items)} · sitemap added {added}')
    for a in items:
        print(' ', a['date'], a['slug'], a['title'])


if __name__ == '__main__':
    main()
