"""블로그 빌드(2026-11-03). 새 글을 올리거나 고친 뒤 한 번 돌리면 아래를 모두 맞춘다.
- /blog/ 목록(20개씩 /blog/page/N/) · 카테고리 /blog/category/<memorize|daily|basics|parents>/
- RSS /blog/rss.xml(최근 30편) — 네이버 서치어드바이저 · 구글에 제출
- 글마다 '함께 읽으면 좋은 글'(같은 카테고리 3편) · 이전 글 / 다음 글 (<!-- blog:related --> 묶음을 다시 씀)
- 홈의 '블로그 새 글' 3편(<!-- blog:latest --> 묶음)
- sitemap.xml(빠진 블로그 주소 추가) · llms.txt '## 블로그' 묶음
글: docs/blog/<slug>/index.html(새 글은 tool/new_post.py로 뼈대를 만든다) + 블로그 전에 생긴 글(blog_common.LEGACY).
실행: python3 tool/register_articles.py
"""
import datetime as dt
import email.utils
import html
import re
import shutil

from blog_common import CATEGORIES, D, LEGACY, SITE, e, meta, page_head, template

PER_PAGE = 20


def read_post(f, path, cat):
    s = f.read_text(encoding='utf-8')
    if 'noindex' in meta(s, name='robots'):
        return None
    title = re.sub(r'\s*\|\s*단숙이.*$', '', html.unescape(re.search(r'<title>(.*?)</title>', s, re.S).group(1)).strip())
    pub = meta(s, prop='article:published_time')
    if not pub:
        m = re.search(r'"datePublished":\s*"([^"]+)"', s)
        pub = m.group(1) if m else ''
    if not pub:
        m = re.search(rf'<loc>{re.escape(SITE + path)}</loc>\s*<lastmod>([^<]+)</lastmod>', (D / 'sitemap.xml').read_text(encoding='utf-8'))
        pub = m.group(1) if m else '2026-10-01'
    return {'file': f, 'path': path, 'url': SITE + path, 'title': title, 'desc': meta(s, name='description'),
            'date': pub[:10], 'pub': pub, 'cat': cat}


def posts():
    out = []
    for f in sorted((D / 'blog').glob('*/index.html')):
        if f.parent.name in ('page', 'category'):
            continue
        cat = meta(f.read_text(encoding='utf-8'), name='dansuki:category')
        p = read_post(f, f'blog/{f.parent.name}/', cat if cat in CATEGORIES else 'memorize')
        if p:
            out.append(p)
    for slug, cat in LEGACY.items():
        f = D / slug / 'index.html'
        if f.exists():
            p = read_post(f, f'{slug}/', cat)
            if p:
                out.append(p)
    return sorted(out, key=lambda p: (p['pub'], p['path']), reverse=True)


CARD_CSS = '''<style>
.post-list{list-style:none;margin:22px 0 0;padding:0;display:grid;gap:12px}
.post-list a{display:grid;gap:6px;padding:18px 20px;border-radius:18px;background:var(--surface);border:1px solid var(--line);text-decoration:none;color:var(--text)}
.post-list a:hover{border-color:var(--text)}
.post-list b{font-family:'MaruBuri',serif;font-weight:400;font-size:20px;line-height:1.4}
.post-list span{color:var(--muted);font-size:15px}
.post-list small{color:var(--faint);font-size:13px}
.cats{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0}
.cats a{padding:7px 14px;border-radius:999px;border:1px solid var(--line);background:var(--surface);text-decoration:none;color:var(--text);font-size:14px;font-weight:600}
.cats a[aria-current]{background:var(--text);color:var(--canvas);border-color:var(--text)}
.pager{display:flex;justify-content:space-between;gap:16px;margin-top:22px;font-weight:600}
</style>'''


def card(p):
    cname = CATEGORIES[p['cat']][0]
    return (f'<li><a href="/{p["path"]}"><b>{e(p["title"])}</b><span>{e(p["desc"])}</span>'
            f'<small>{cname} · <time datetime="{p["date"]}">{p["date"].replace("-", ". ")}</time></small></a></li>')


def chips(active):
    cur = ' aria-current="page"'
    out = [f'<a href="/blog/"{cur if active is None else ""}>전체</a>']
    for k, (n, _) in CATEGORIES.items():
        out.append(f'<a href="/blog/category/{k}/"{cur if active == k else ""}>{n}</a>')
    return '<nav class="cats" aria-label="블로그 카테고리">' + ''.join(out) + '</nav>'


def list_page(path, title, h1, deck, items, active, crumb, prev=None, nxt=None, noindex=False):
    _, _, nav, tail = template()
    url = SITE + path
    desc = re.sub(r'<[^>]+>', ' ', deck).replace('  ', ' ').strip()
    if active is None:
        main_node = {'@type': 'Blog', '@id': url + '#blog', 'url': url, 'name': title, 'description': desc, 'inLanguage': 'ko-KR',
                     'isPartOf': {'@id': 'https://dansuki.com/#website'}, 'publisher': {'@id': 'https://dansuki.com/#org'},
                     'blogPost': [{'@type': 'BlogPosting', 'headline': p['title'], 'url': p['url'], 'datePublished': p['pub']} for p in items]}
    else:
        main_node = {'@type': 'CollectionPage', '@id': url + '#webpage', 'url': url, 'name': title, 'description': desc, 'inLanguage': 'ko-KR',
                     'isPartOf': {'@id': 'https://dansuki.com/#website'},
                     'mainEntity': {'@type': 'ItemList', 'itemListElement': [
                         {'@type': 'ListItem', 'position': i + 1, 'url': p['url'], 'name': p['title']} for i, p in enumerate(items)]}}
    ld = {'@context': 'https://schema.org', '@graph': [main_node, {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(crumb)]}]}
    head = page_head(url=url, title=title, desc=desc, og_type='website', ld=ld, extra=CARD_CSS)
    if noindex:
        head = head.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex, follow">')
    pager = ''
    if prev or nxt:
        pager = '<div class="pager">' + (f'<a href="/{prev}">← 최신 글</a>' if prev else '<span></span>') + (f'<a href="/{nxt}">지난 글 →</a>' if nxt else '') + '</div>'
    crumbs = ' › '.join(f'<a href="/{u}">{n}</a>' if i < len(crumb) - 1 else n for i, (n, u) in enumerate(crumb))
    body = f'''<main class="research-main"><article class="wrap narrow research-article" id="post">
<header class="article-head"><p class="crumb">{crumbs}</p><div class="series">단숙이 블로그 · {len(items)}편</div><h1>{h1}</h1><p class="deck">{deck}</p></header>
{chips(active)}<ul class="post-list">{"".join(card(p) for p in items)}</ul>{pager}
<p style="margin-top:28px">지금 몇 개 아는지 궁금하면 <a href="/test/">2분 영단어 테스트</a>, 전체 단어는 <a href="/basic-words/">교육부 기본 어휘 3000 목록</a>에서 볼 수 있어요. 새 글은 <a href="/blog/rss.xml">RSS</a>로도 받아 볼 수 있어요.</p>
</article></main>'''
    f = D / path / 'index.html'
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(head + nav + body + tail, encoding='utf-8')


def build_lists(ps):
    pages = [ps[i:i + PER_PAGE] for i in range(0, len(ps), PER_PAGE)] or [[]]
    shutil.rmtree(D / 'blog/page', ignore_errors=True)
    for n, chunk in enumerate(pages, 1):
        path = 'blog/' if n == 1 else f'blog/page/{n}/'
        prev = None if n == 1 else ('blog/' if n == 2 else f'blog/page/{n - 1}/')
        nxt = f'blog/page/{n + 1}/' if n < len(pages) else None
        list_page(path, '단숙이 블로그 · 영단어 공부법 글' + ('' if n == 1 else f' {n}쪽') + ' | 단숙이',
                  '단숙이 <span class="mark">블로그</span>', '영단어 외우는 법, 하루 분량, 기초 다지기까지. <br>단숙이가 정리한 영단어 공부 글이에요.',
                  chunk, None, [('단숙이', ''), ('블로그', 'blog/')], prev, nxt, noindex=n > 1)
    shutil.rmtree(D / 'blog/category', ignore_errors=True)
    for k, (n, intro) in CATEGORIES.items():
        items = [p for p in ps if p['cat'] == k]
        list_page(f'blog/category/{k}/', f'{n} · 영단어 공부 글 | 단숙이 블로그', e(n), e(intro) + '.', items, k,
                  [('단숙이', ''), ('블로그', 'blog/'), (n, f'blog/category/{k}/')], noindex=not items)


def related(ps):
    """글마다 같은 카테고리 3편 + 이전 · 다음 글을 끼워 넣는다."""
    chrono = sorted(ps, key=lambda p: p['pub'])
    for i, p in enumerate(chrono):
        s = p['file'].read_text(encoding='utf-8')
        s = re.sub(r'<!-- blog:related -->.*?<!-- /blog:related -->\n?', '', s, flags=re.S)
        anchor = '<div class="article-app">'
        if anchor not in s:
            continue  # 공부법 · 난이도처럼 글 틀이 다른 페이지는 목록에만 넣는다
        same = [q for q in ps if q['cat'] == p['cat'] and q is not p][:3]
        if len(same) < 3:
            same += [q for q in ps if q is not p and q not in same][:3 - len(same)]
        older = chrono[i - 1] if i > 0 else None
        newer = chrono[i + 1] if i + 1 < len(chrono) else None
        block = ('<!-- blog:related --><section class="post-more" aria-label="함께 읽으면 좋은 글"><h2>함께 읽으면 좋은 글</h2><ul class="post-list">'
                 + ''.join(card(q) for q in same) + '</ul><div class="pager">'
                 + (f'<a href="/{older["path"]}" rel="prev">← {e(older["title"])}</a>' if older else '<span></span>')
                 + (f'<a href="/{newer["path"]}" rel="next">{e(newer["title"])} →</a>' if newer else '')
                 + '</div><p style="margin-top:14px"><a href="/blog/">블로그 전체 보기</a></p></section><!-- /blog:related -->\n')
        s = s.replace(anchor, block + anchor, 1)
        if '.post-list{' not in s:
            s = s.replace('</head>', CARD_CSS + '</head>', 1)
        p['file'].write_text(s, encoding='utf-8')


def rss(ps):
    now = email.utils.format_datetime(dt.datetime.now(dt.timezone.utc))

    def rfc(p):
        try:
            return email.utils.format_datetime(dt.datetime.fromisoformat(p['pub'] if 'T' in p['pub'] else p['pub'] + 'T09:00:00+09:00'))
        except ValueError:
            return now
    items = ''.join(
        f'<item><title>{e(p["title"])}</title><link>{p["url"]}</link><guid isPermaLink="true">{p["url"]}</guid>'
        f'<description>{e(p["desc"])}</description><category>{e(CATEGORIES[p["cat"]][0])}</category><pubDate>{rfc(p)}</pubDate></item>\n'
        for p in ps[:30])
    x = (f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
         f'<title>단숙이 블로그</title><link>{SITE}blog/</link><atom:link href="{SITE}blog/rss.xml" rel="self" type="application/rss+xml"/>'
         f'<description>영단어 외우는 법 · 하루 분량 · 기초 다지기 — 무료 중고등 영단어 앱 단숙이의 공부 글</description><language>ko</language>'
         f'<lastBuildDate>{now}</lastBuildDate>\n{items}</channel></rss>\n')
    (D / 'blog').mkdir(exist_ok=True)
    (D / 'blog/rss.xml').write_text(x, encoding='utf-8')


def home_latest(ps):
    f = D / 'index.html'
    s = f.read_text(encoding='utf-8')
    s = re.sub(r'\s*<!-- blog:latest -->.*?<!-- /blog:latest -->', '', s, flags=re.S)
    cards = ''.join(f'<a class="latest-card" href="/{p["path"]}"><small>{CATEGORIES[p["cat"]][0]} · {p["date"].replace("-", ". ")}</small><b>{e(p["title"])}</b><span>{e(p["desc"])}</span></a>' for p in ps[:3])
    block = (f'\n    <!-- blog:latest --><section id="blog-latest"><div class="wrap"><h2>블로그 새 글</h2>'
             f'<p class="sub">영단어 외우는 법, 하루 분량, 기초 다지기를 꾸준히 정리하고 있어요.</p><div class="latest">{cards}</div>'
             f'<p class="more"><a href="/blog/">블로그 전체 보기 ›</a></p></div></section><!-- /blog:latest -->')
    s = s.replace('\n    <!-- 자주 묻는 질문 -->', block + '\n\n    <!-- 자주 묻는 질문 -->', 1)
    if 'application/rss+xml' not in s:
        s = s.replace('</head>', f'  <link rel="alternate" type="application/rss+xml" title="단숙이 블로그" href="{SITE}blog/rss.xml">\n</head>', 1)
    f.write_text(s, encoding='utf-8')


def sitemap(ps):
    p = D / 'sitemap.xml'
    s = p.read_text(encoding='utf-8')
    s = re.sub(r'\s*<url>\s*<loc>https://dansuki.com/articles/</loc>.*?</url>', '', s, flags=re.S)
    want = [('blog/', ps[0]['date'] if ps else '2026-11-03')]
    want += [(f'blog/category/{k}/', max(q['date'] for q in ps if q['cat'] == k)) for k in CATEGORIES if any(q['cat'] == k for q in ps)]
    want += [(q['path'], q['date']) for q in ps]
    # 지운 블로그 글 · 비어 버린 카테고리는 사이트맵에서도 뺀다
    keep = {SITE + path for path, _ in want}
    s = re.sub(r'\s*<url>\s*<loc>(https://dansuki.com/blog/[^<]*)</loc>.*?</url>', lambda m: m.group(0) if m.group(1) in keep else '', s, flags=re.S)
    added = 0
    for path, day in want:
        loc = SITE + path
        if f'<loc>{loc}</loc>' not in s:
            s = s.replace('</urlset>', f'  <url>\n    <loc>{loc}</loc>\n    <lastmod>{day}</lastmod>\n  </url>\n</urlset>')
            added += 1
    p.write_text(s, encoding='utf-8')
    return added


def llms(ps):
    p = D / 'llms.txt'
    s = p.read_text(encoding='utf-8')
    s = re.sub(r'## 공부 글\n.*?<!-- articles:end -->\n*', '', s, flags=re.S)
    block = ('<!-- blog:start (tool/register_articles.py가 다시 씀) -->\n'
             + '\n'.join(f'- [{q["title"]}]({q["url"]}): {q["desc"]}' for q in ps) + '\n<!-- blog:end -->')
    if '<!-- blog:start' in s:
        s = re.sub(r'<!-- blog:start.*?<!-- blog:end -->', block, s, flags=re.S)
    else:
        s = s.replace('## Optional', f'## 블로그\n\n- [단숙이 블로그]({SITE}blog/) · RSS {SITE}blog/rss.xml\n{block}\n\n## Optional', 1)
    p.write_text(s, encoding='utf-8')


def old_hub():
    """예전 '공부 글 모음'(/articles/) 주소는 블로그로 넘긴다."""
    f = D / 'articles/index.html'
    f.parent.mkdir(exist_ok=True)
    f.write_text(f'<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><title>단숙이 블로그로 옮겼어요</title>'
                 f'<meta name="robots" content="noindex, follow"><link rel="canonical" href="{SITE}blog/">'
                 f'<meta http-equiv="refresh" content="0; url=/blog/"><script>location.replace("/blog/"+location.hash)</script></head>'
                 f'<body><p><a href="/blog/">단숙이 블로그</a>로 옮겼어요.</p></body></html>\n', encoding='utf-8')


def main():
    ps = posts()
    rss(ps)
    build_lists(ps)
    related(ps)
    home_latest(ps)
    added = sitemap(ps)
    llms(ps)
    old_hub()
    print(f'blog posts {len(ps)} · sitemap added {added}')
    for p in ps:
        print(' ', p['date'], CATEGORIES[p['cat']][0], p['path'], p['title'])


if __name__ == '__main__':
    main()
