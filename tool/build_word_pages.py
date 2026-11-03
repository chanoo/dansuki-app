"""dansuki.com 검색용 글 두 편을 만든다(2026-11-03).
- /basic-words/            교육부 기본 어휘 3000 목록(2022 개정, 학교급별 · 2015에만 있던 213개)
- /middle-school-words/    중학 영단어 공부법
spaced-review/index.html의 머리 · 메뉴 · 푸터를 그대로 빌려 쓴다.
사용: python3 tool/build_word_pages.py docs   (단어 사전 수정판이 바뀌면 vocab 파일 이름 · 글꼴(subset_fonts.sh)도 함께)
"""
import html
import json
import re
import sys
from pathlib import Path

DOCS = Path(sys.argv[1]).expanduser()
TPL = (DOCS / 'spaced-review/index.html').read_text(encoding='utf-8')
DATA = json.loads((DOCS / 'vocab/csat_v2.r16.json').read_text(encoding='utf-8'))
NOW = '2026-11-03T12:00:00+09:00'
DAY = '2026-11-03'
APP = 'https://apps.apple.com/kr/app/id6819707350'
e = lambda s: html.escape(s, quote=True)

# ── 템플릿 조각 ──────────────────────────────────────────────
nav = TPL[TPL.index('<nav class="top">'):TPL.index('<main')]
nav = nav.replace(' aria-current="page"', '')
tail = TPL[TPL.index('</article></main>') + len('</article></main>'):]
store_btn = re.search(r'<a class="store" href="https://apps\.apple\.com[^"]*" aria-label="App Store에서 단숙이 받기">.*?</a>', TPL, re.S).group(0)


def head(*, path, title, desc, og_alt, ld, extra_css=''):
    url = f'https://dansuki.com/{path}'
    return f'''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><meta name="theme-color" content="#F6F1E7"><meta property="og:type" content="article"><meta property="og:site_name" content="단숙이"><meta property="og:locale" content="ko_KR"><meta property="og:url" content="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:image" content="https://dansuki.com/og.jpg"><meta property="og:image:alt" content="{e(og_alt)}"><meta property="article:published_time" content="{NOW}"><meta property="article:modified_time" content="{NOW}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="https://dansuki.com/og.jpg"><meta name="twitter:image:alt" content="{e(og_alt)}"><meta name="apple-itunes-app" content="app-id=6819707350"><meta name="robots" content="index, follow, max-image-preview:large"><link rel="icon" href="/icon.png"><link rel="apple-touch-icon" href="/icon.png"><link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link rel="preload" href="/fonts/MaruBuri-sub.woff2?v=20261103" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.min.css"><link rel="stylesheet" href="/site.css?v=20261103"><link rel="stylesheet" href="/article.css?v=20261019seo">{extra_css}<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script><script src="/navigation.js?v=20261020" defer></script></head><body>'''


def ld(*, path, title, desc, headline, crumb_name, extra=None):
    url = f'https://dansuki.com/{path}'
    org = {'@id': 'https://dansuki.com/#org', '@type': 'Organization', 'name': '단숙이', 'url': 'https://dansuki.com/'}
    art = {
        '@type': 'Article', '@id': url + '#article', 'url': url, 'mainEntityOfPage': {'@id': url + '#webpage'},
        'headline': headline, 'description': desc, 'inLanguage': 'ko-KR', 'datePublished': NOW, 'dateModified': NOW,
        'image': {'@type': 'ImageObject', 'url': 'https://dansuki.com/og.jpg'},
        'author': org, 'publisher': {**org, 'logo': {'@type': 'ImageObject', 'url': 'https://dansuki.com/icon.png'}},
        'isPartOf': {'@id': 'https://dansuki.com/#website'},
    }
    if extra:
        art.update(extra)
    return {'@context': 'https://schema.org', '@graph': [
        {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': title, 'description': desc, 'inLanguage': 'ko-KR',
         'isPartOf': {'@id': 'https://dansuki.com/#website'}, 'mainEntity': {'@id': url + '#article'}, 'dateModified': NOW},
        art,
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': '단숙이', 'item': 'https://dansuki.com/'},
            {'@type': 'ListItem', 'position': 2, 'name': '공부 방법', 'item': 'https://dansuki.com/method/'},
            {'@type': 'ListItem', 'position': 3, 'name': crumb_name, 'item': url}]},
    ]}


def app_box(h2, ps):
    body = ''.join(f'<p>{p}</p>' for p in ps)
    return f'<div class="article-app"><h2>{h2}</h2>{body}<p>{store_btn} &nbsp; <a href="/try/">1분 체험해 보기</a></p></div>'


# ── 단어 데이터 ──────────────────────────────────────────────
words = DATA['words']
cur = [w for w in words if w.get('cell2022')]
LEVELS = [('elementary', '초등', 'elem'), ('middle', '중학', 'middle'), ('high', '고등', 'high')]
by = {k: sorted((w for w in cur if w.get('grade2022') == k), key=lambda w: w['word'].lower()) for k, _, _ in LEVELS}
only2015 = sorted((w for w in words if w.get('grade2015') and not w.get('cell2022')), key=lambda w: w['word'].lower())
new2022 = [w for w in cur if not w.get('grade2015')]
N = {k: len(v) for k, v in by.items()}
assert sum(N.values()) == len(cur) == 3000, N


def word_list(ws, slug):
    groups = {}
    for w in ws:
        ch = w['word'][0].upper()
        groups.setdefault(ch if ch.isalpha() else '#', []).append(w)
    letters = ''.join(f'<a href="#{slug}-{c.lower()}">{c}</a>' for c in groups)
    out = [f'<nav class="az" aria-label="알파벳으로 찾기">{letters}</nav>']
    for c, g in groups.items():
        items = ''.join(
            f'<li><b lang="en">{e(w["word"])}</b><span>{e(w["meaning"])}</span></li>' for w in g)
        out.append(f'<div class="wgroup"><h4 id="{slug}-{c.lower()}">{c}</h4><ul class="wlist">{items}</ul></div>')
    return ''.join(out)


WORDS_CSS = '''<style>
.research-article .lv-chips{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 8px}
.research-article .lv-chips a{display:inline-flex;align-items:baseline;gap:6px;padding:8px 14px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--text);text-decoration:none;font-size:14px;font-weight:600}
.research-article .lv-chips a small{color:var(--muted);font-weight:500;font-size:12.5px}
.research-article .finder{position:sticky;top:8px;z-index:5;margin:18px 0 6px;padding:10px;border:1px solid var(--line);border-radius:16px;background:var(--canvas);box-shadow:var(--shadow)}
.research-article .finder input{width:100%;box-sizing:border-box;font:inherit;font-size:16px;padding:10px 14px;border:1px solid var(--line);border-radius:12px;background:var(--surface);color:var(--text)}
.research-article .finder p{margin:6px 4px 0;font-size:13px;color:var(--muted)}
.research-article .level{margin:36px 0 0}
.research-article .level>h3{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.research-article .level>h3 small{font-family:inherit;font-size:14px;color:var(--muted);font-weight:500}
.research-article .az{display:flex;flex-wrap:wrap;gap:4px;margin:10px 0 4px}
.research-article .az a{min-width:28px;padding:4px 0;text-align:center;border-radius:8px;font-size:13px;font-weight:600;color:var(--muted);text-decoration:none;background:var(--surface);border:1px solid var(--line)}
.research-article .wgroup h4{margin:18px 0 6px;font-size:15px;color:var(--muted);scroll-margin-top:96px}
.research-article .wlist{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 20px}
.research-article .wlist li{display:flex;gap:10px;align-items:baseline;padding:7px 0;border-bottom:1px solid var(--line);font-size:14.5px;line-height:1.45;min-width:0}
.research-article .wlist b{flex:0 0 auto;max-width:48%;font-weight:700;overflow-wrap:anywhere}
.research-article .wlist span{color:var(--muted);overflow-wrap:anywhere;word-break:keep-all}
.research-article details.old{margin:36px 0 0;border:1px solid var(--line);border-radius:18px;padding:4px 18px 14px;background:var(--surface)}
.research-article details.old summary{cursor:pointer;padding:12px 0;font-weight:700}
[hidden]{display:none!important}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.research-article .empty{display:none;padding:18px 0;color:var(--muted)}
@media (max-width:640px){.research-article .wlist{grid-template-columns:1fr}}
</style>'''

FIND_JS = '''<script>
// 단어 찾기: 영어나 뜻 일부로 거른다. 스크립트가 없어도 목록은 다 보인다(검색엔진 · 오래된 브라우저).
(() => {
  const box = document.getElementById('find'), info = document.getElementById('find-info');
  if (!box) return;
  const items = [...document.querySelectorAll('.wlist li')];
  items.forEach(li => li.dataset.k = li.textContent.toLowerCase());
  const groups = [...document.querySelectorAll('.wgroup')], levels = [...document.querySelectorAll('.level, details.old')];
  const empty = document.querySelector('.empty');
  let t;
  const run = () => {
    const q = box.value.trim().toLowerCase();
    let n = 0;
    items.forEach(li => { const on = !q || li.dataset.k.includes(q); li.hidden = !on; if (on) n++; });
    groups.forEach(g => g.hidden = !!q && !g.querySelector('li:not([hidden])'));
    levels.forEach(l => { l.hidden = !!q && !l.querySelector('li:not([hidden])'); if (q && l.tagName === 'DETAILS' && !l.hidden) l.open = true; });
    document.querySelectorAll('.az').forEach(a => a.hidden = !!q);
    info.textContent = q ? (n ? `${n.toLocaleString()}개 찾았어요` : '') : '영어나 뜻 일부를 써 보세요. 예: environment, 환경';
    empty.style.display = q && !n ? 'block' : 'none';
  };
  box.addEventListener('input', () => { clearTimeout(t); t = setTimeout(run, 120); });
})();
</script>'''


def build_words():
    path = 'basic-words/'
    title = '교육부 기본 어휘 3000 목록 · 초등 · 중학 · 고등 영단어 뜻 정리 | 단숙이'
    desc = ('2022 개정 교육과정 영어 기본 어휘 3,000개를 초등 800 · 중학 1,200 · 고등 1,000개로 나눠 뜻과 함께 정리했어요. '
            '2015 개정에만 있던 213개도 함께 볼 수 있어요.')
    headline = '교육부 기본 어휘 3,000개, 학교급별로 한눈에'
    data = ld(path=path, title=title, desc=desc, headline=headline, crumb_name='기본 어휘 3000 목록')
    chips = ''.join(f'<a href="#{s}">{n} <small>{N[k]:,}개</small></a>' for k, n, s in LEVELS)
    chips += f'<a href="#only-2015">2015에만 <small>{len(only2015)}개</small></a>'
    levels = ''
    blurb = {
        'elementary': '초등학교에서 배우는 기초 단어예요. 중학생이라도 여기서 막히는 단어가 있다면 먼저 채워 두는 게 좋아요.',
        'middle': '중학교 교과서와 시험에 자주 나오는 단어예요. 고등 단어의 바탕이 돼요.',
        'high': '고등학교 교과서와 수능 · 모의고사 지문의 바탕이 되는 단어예요.',
    }
    for k, n, s in LEVELS:
        levels += (f'<section class="level" id="{s}"><h3>{n} 기본 어휘 <small>{N[k]:,}개</small></h3>'
                   f'<p>{blurb[k]}</p>{word_list(by[k], s)}</section>')
    old = (f'<details class="old" id="only-2015"><summary>2015 개정에만 있던 단어 {len(only2015)}개</summary>'
           f'<p>2022 개정 목록에서 빠졌지만 예전 교재나 기출 지문에서는 여전히 만날 수 있는 단어예요. 단숙이에는 이 단어도 들어 있어요.</p>'
           f'{word_list(only2015, "old")}</details>')
    sample_new = ', '.join(w['word'] for w in sorted(new2022, key=lambda w: w['word'])[:8])
    body = f'''<main class="research-main"><article class="wrap narrow research-article" id="post">
<header class="article-head"><p class="crumb"><a href="/">단숙이</a> › <a href="/method/">공부 방법</a> › 기본 어휘 목록</p><div class="series">교육부 기본 어휘 · 2022 개정 교육과정</div><h1>교육부 기본 어휘 3,000개,<br><span class="mark">학교급별로 한눈에</span></h1><p class="deck">초등 800 · 중학 1,200 · 고등 1,000.<br>뜻과 함께 정리하고, 찾아볼 수 있게 했어요.</p><div class="byline">글 · 단숙이를 만든 사람 <span aria-hidden="true">·</span> <time datetime="{DAY}">2026년 11월 3일</time></div></header>
<nav class="article-toc" aria-label="이 글의 내용"><p>이 글에서 살펴볼 내용</p><ol><li><a href="#what">기본 어휘가 뭔가요</a></li><li><a href="#count">학교급별로 몇 개인가요</a></li><li><a href="#diff">2015 개정과 무엇이 달라졌나요</a></li><li><a href="#list">3,000개 전체 목록</a></li><li><a href="#how">이 목록, 어떻게 외우면 좋을까요</a></li></ol></nav>
<p class="opening">단어장마다 고른 단어가 달라서<br>무엇부터 외워야 할지 헷갈릴 때가 있어요.</p>
<p>그럴 때 기준이 되는 목록이 있어요. 교육부가 영어과 교육과정에 함께 고시하는 <strong>기본 어휘 목록</strong>이에요. 교과서와 시험 문제를 만들 때 바탕이 되는 단어들이라, 기초를 다질 때 가장 먼저 챙길 만한 단어예요.</p>
<h2 id="what">기본 어휘는<br>어떤 단어인가요?</h2>
<p>기본 어휘는 영어 교육과정 문서 끝에 붙은 단어 목록이에요. 지금 학교에서 쓰는 것은 <strong>2022 개정 교육과정(교육부 고시 제2022-33호)</strong>의 목록이고, 그 전에는 <strong>2015 개정 교육과정(교육부 고시 제2015-74호)</strong>의 목록을 썼어요.</p>
<p>목록에는 단어만 있고 뜻은 없어요. 이 페이지의 뜻은 단숙이 앱에서 쓰는 대표 뜻이에요. 뜻이 여러 개인 단어는 자주 쓰는 뜻을 먼저 적었어요.</p>
<h2 id="count">학교급별로<br>몇 개를 알아야 할까요?</h2>
<p>단숙이는 2022 개정 기본 어휘 3,000개를 이렇게 나눠 담았어요.</p>
<div class="stats" aria-label="학교급별 기본 어휘 수"><div class="stat"><b>{N["elementary"]:,}개</b><span>초등</span></div><div class="stat"><b>{N["middle"]:,}개</b><span>중학</span></div><div class="stat"><b>{N["high"]:,}개</b><span>고등</span></div></div>
<p>중학생이라면 초등 800개와 중학 1,200개, 모두 <strong>2,000개</strong>가 기본이에요. 고등학생은 여기에 고등 1,000개를 더해 3,000개가 바탕이 돼요.</p>
<h2 id="diff">2015 개정과는<br>무엇이 달라졌나요?</h2>
<p>두 목록은 대부분 같아요. 2022 개정 3,000개 중 <strong>{3000 - len(new2022):,}개</strong>는 2015 개정에도 있던 단어예요. 2022 개정에서 새로 들어온 단어가 <strong>{len(new2022)}개</strong>, 2015 개정에만 있던 단어가 <strong>{len(only2015)}개</strong>예요.</p>
<p>새로 들어온 단어에는 {e(sample_new)} 같은 일상 단어가 많아요. 2015 개정에만 있던 단어는 목록 맨 아래에 따로 모아 뒀어요.</p>
<h2 id="list">기본 어휘<br>3,000개 전체 목록</h2>
<div class="lv-chips">{chips}</div>
<div class="finder" role="search"><label class="sr-only" for="find">단어 찾기</label><input id="find" type="search" placeholder="단어 찾기 (영어나 뜻)" autocomplete="off" enterkeyhint="search"><p id="find-info" aria-live="polite">영어나 뜻 일부를 써 보세요. 예: environment, 환경</p></div>
<p class="empty">찾는 단어가 없어요. 철자를 한 번 더 확인해 보세요.</p>
{levels}{old}
<h2 id="how">이 목록,<br>어떻게 외우면 좋을까요?</h2>
<p>3,000개를 한 번에 외우려 하면 금방 지쳐요. 하루에 조금씩, 대신 매일 하는 쪽이 오래 가요.</p>
<div class="study"><h3>기본 어휘를 외우는 순서</h3><ul><li><strong>초등 단어부터 훑어보기</strong><br>아는 단어는 빠르게 넘기고, 막히는 단어만 골라 두세요.</li><li><strong>보기 전에 먼저 떠올리기</strong><br>뜻을 가리고 떠올려 본 뒤 확인하면, 그냥 읽을 때보다 오래 남아요.</li><li><strong>잊을 때쯤 다시 보기</strong><br>외운 단어는 며칠 뒤, 일주일 뒤, 몇 주 뒤에 다시 확인해요.</li></ul></div>
<p>자세한 방법은 <a href="/middle-school-words/">중학 영단어 공부법</a>과 <a href="/spaced-review/">복습 간격 연구 이야기</a>에 정리해 뒀어요.</p>
{app_box("기본 어휘 3,000개,<br>하루 20개씩 단숙이로.", ["단숙이는 이 목록을 바탕으로 만든 무료 영단어 · 숙어 앱이에요. 하루 단어 20개를 먼저 떠올리고 고르는 방식으로 익히고, 외운 단어는 2일 · 7일 · 21일 뒤에 다시 물어봐요.", "외운 단어는 셜록 홈스, 오즈의 마법사 같은 이야기에서 다시 만나요. 광고와 가입 없이 바로 시작할 수 있어요."])}
<section class="article-refs" aria-label="출처"><h2>출처</h2><p>교육부 고시 제2022-33호 영어과 교육과정의 기본 어휘 목록, 교육부 고시 제2015-74호 영어과 교육과정의 기본 어휘 목록.</p><p>뜻은 단숙이가 앱에서 쓰려고 정리한 것이에요. 학교급 나누기는 단숙이 기준이에요. 교육부, 한국교육과정평가원과는 관계없이 개인이 만든 페이지예요.</p></section>
</article></main>'''
    page = head(path=path, title=title, desc=desc, og_alt='교육부 기본 어휘 3,000개 학교급별 목록', ld=data, extra_css=WORDS_CSS) + nav + body + tail.replace('</body>', FIND_JS + '</body>')
    (DOCS / path).mkdir(exist_ok=True)
    (DOCS / path / 'index.html').write_text(page, encoding='utf-8')


def build_middle():
    path = 'middle-school-words/'
    title = '중학 영단어 공부법 · 하루 몇 개, 어떻게 외울까 | 단숙이'
    desc = ('중학생이 알아야 할 기본 영단어 2,000개를 하루 20개씩, 먼저 떠올리고 간격을 두고 다시 보는 방법으로 외우는 법을 정리했어요. '
            '바로 써먹을 수 있는 하루 공부 순서도 담았어요.')
    headline = '중학 영단어, 하루 20개를 오래 남기는 방법'
    data = ld(path=path, title=title, desc=desc, headline=headline, crumb_name='중학 영단어 공부법')
    mid = by['middle']
    pick = ['achieve', 'environment', 'experience', 'opinion', 'prepare', 'communicate', 'decide', 'imagine']
    m = {w['word']: w['meaning'] for w in mid + by['elementary']}
    sample = ''.join(f'<li><b lang="en">{e(k)}</b><span>{e(m[k])}</span></li>' for k in pick if k in m)
    body = f'''<main class="research-main"><article class="wrap narrow research-article" id="post">
<header class="article-head"><p class="crumb"><a href="/">단숙이</a> › <a href="/method/">공부 방법</a> › 중학 영단어 공부법</p><div class="series">중학 영단어 · 공부법</div><h1>중학 영단어,<br><span class="mark">하루 20개를 오래 남기는</span> 방법</h1><p class="deck">몇 개를 외워야 하는지, 하루에 얼마나 할지,<br>어떻게 해야 안 잊는지 차례로 정리했어요.</p><div class="byline">글 · 단숙이를 만든 사람 <span aria-hidden="true">·</span> <time datetime="{DAY}">2026년 11월 3일</time></div></header>
<nav class="article-toc" aria-label="이 글의 내용"><p>이 글에서 살펴볼 내용</p><ol><li><a href="#how-many">중학생은 몇 개를 알아야 할까</a></li><li><a href="#per-day">하루에 몇 개가 좋을까</a></li><li><a href="#recall">읽기보다 먼저 떠올리기</a></li><li><a href="#spacing">잊을 때쯤 다시 보기</a></li><li><a href="#context">문장과 이야기에서 다시 만나기</a></li><li><a href="#routine">하루 15분 공부 순서</a></li></ol></nav>
<p class="opening">어제 외운 단어가<br>오늘 시험지에서 생각나지 않을 때가 있어요.</p>
<p>단어를 열심히 봤는데도 잘 떠오르지 않는다면, 외운 시간보다 <strong>외우는 방법</strong>을 바꿔 볼 때예요. 중학 영단어는 고등 영어의 바탕이 되니까, 지금 오래 남는 방식으로 쌓아 두면 나중이 훨씬 편해요.</p>
<h2 id="how-many">중학생은 영단어를<br>몇 개나 알아야 할까요?</h2>
<p>기준으로 삼기 좋은 건 교육부가 고시한 <a href="/basic-words/">기본 어휘 목록</a>이에요. 2022 개정 교육과정의 기본 어휘 3,000개 중 초등 단어 {N["elementary"]:,}개와 중학 단어 {N["middle"]:,}개, 모두 <strong>2,000개</strong>가 중학생의 기본이에요.</p>
<div class="stats" aria-label="중학생 기본 어휘"><div class="stat"><b>{N["elementary"]:,}개</b><span>초등 기본 어휘</span></div><div class="stat"><b>{N["middle"]:,}개</b><span>중학 기본 어휘</span></div><div class="stat"><b>약 100일</b><span>하루 20개씩</span></div></div>
<p>초등 단어 중에 모르는 게 있다면 거기서부터 시작해도 괜찮아요. 기초가 비어 있으면 중학 단어도 잘 붙지 않아요.</p>
<ul class="wlist" aria-label="중학 기본 어휘 예시">{sample}</ul>
<h2 id="per-day">하루에 몇 개씩<br>외우는 게 좋을까요?</h2>
<p>한 번에 100개를 몰아서 외우는 것보다 <strong>하루 20개쯤을 매일</strong> 하는 쪽을 권해요. 양이 적으면 매일 이어 가기 쉽고, 다음 날 복습할 단어도 감당할 만큼만 쌓여요.</p>
<div class="quote">많이 외운 날보다,<br>빠지지 않은 날이 더 중요해요.</div>
<p>하루 20개씩이면 중학 기본 어휘 2,000개를 100일쯤에 한 번 다 만나요. 바쁜 날엔 다섯 개만 해도 괜찮아요. 끊기지 않는 게 먼저예요.</p>
<h2 id="recall">눈으로 읽기보다<br>먼저 떠올려 보기</h2>
<p>단어장을 여러 번 읽으면 아는 것 같은 느낌이 들어요. 그런데 시험에서는 단어를 보고 뜻을 <strong>스스로 꺼내야</strong> 해요. 그래서 공부할 때도 뜻을 가리고 먼저 떠올려 본 뒤 확인하는 게 좋아요.</p>
<div class="study"><h3>떠올리기를 공부에 넣는 법</h3><ul><li><strong>영어를 보고 뜻을, 뜻을 보고 영어를</strong><br>두 방향을 다 해 봐야 읽기와 쓰기에서 모두 떠올라요.</li><li><strong>모르면 바로 정답과 예문 보기</strong><br>틀린 단어는 조금 뒤에 한 번 더 물어보세요.</li><li><strong>빨리 떠오르는지도 보기</strong><br>한참 생각해야 떠오르는 단어는 아직 덜 외운 단어예요.</li></ul></div>
<p>단숙이가 이 방법을 어떻게 담았는지는 <a href="/method/">단숙이 공부법</a>에 연구와 함께 정리해 뒀어요.</p>
<h2 id="spacing">잊을 때쯤<br>다시 보기</h2>
<p>오늘 외운 단어는 며칠 지나면 흐려져요. 이때 다시 떠올려 보면 그 단어는 더 오래 남아요. 그래서 새 단어만 늘리지 말고, <strong>예전에 외운 단어를 다시 볼 날</strong>도 정해 두는 게 좋아요.</p>
<p>단숙이는 외운 단어를 <strong>2일 · 7일 · 21일</strong> 뒤에 다시 물어봐요. 간격을 두고 다시 공부하는 방식이 왜 도움이 되는지는 <a href="/spaced-review/">복습 간격 연구 이야기</a>에서 논문과 함께 볼 수 있어요.</p>
<h2 id="context">문장과 이야기에서<br>다시 만나기</h2>
<p>단어만 따로 외우면 어디에 쓰는지 잘 와닿지 않아요. 외운 단어가 들어간 예문을 소리 내어 읽거나, 짧은 이야기 속에서 다시 만나면 뜻이 더 또렷해져요.</p>
<p>단숙이에는 셜록 홈스, 오즈의 마법사 같은 이야기 19편을 중학 · 고등 영어로 다시 쓴 이야기 탭이 있어요. 외운 단어에는 형광펜이 칠해져서, 외울수록 이야기가 술술 읽혀요.</p>
<h2 id="routine">바로 해 보는<br>하루 15분 공부 순서</h2>
<div class="study"><h3>오늘부터 이렇게</h3><ul><li><strong>어제 · 지난주 단어 다시 떠올리기 (5분)</strong><br>뜻을 가리고 먼저 떠올린 뒤 확인해요. 틀린 단어는 따로 표시해요.</li><li><strong>새 단어 20개 (8분)</strong><br>다섯 개씩 끊어서 보고, 바로 그 다섯 개를 가리고 떠올려 봐요.</li><li><strong>틀린 단어만 한 번 더 (2분)</strong><br>오늘 틀린 단어를 마지막에 한 번 더 물어보고 끝내요.</li></ul></div>
<p>처음 며칠은 복습할 단어가 적어서 금방 끝나요. 일주일쯤 지나면 복습이 자리를 잡고, 그때부터 외운 단어가 눈에 띄게 남기 시작해요.</p>
{app_box("하루 20개,<br>단숙이가 순서를 챙겨 줄게요.", ["단숙이는 교육부 기본 어휘로 만든 무료 중고등 영단어 · 숙어 앱이에요. 새 단어는 플래시카드로 먼저 보고, 뜻을 떠올린 뒤 고르는 문제로 익혀요. 외운 단어는 2일 · 7일 · 21일 뒤에 다시 물어봐요.", "단어 하나를 외울 때마다 키링에 조각이 하나씩 끼워져요. 광고와 가입 없이 바로 시작할 수 있어요."])}
<p class="endline">오늘 외운 스무 개가,<br>다음 주에도 떠오르도록.</p>
<section class="article-refs" aria-label="더 읽기"><h2>더 읽기</h2><p><a href="/basic-words/">교육부 기본 어휘 3,000개 목록</a> · <a href="/method/">단숙이 공부법과 참고 연구</a> · <a href="/spaced-review/">복습 간격 연구 이야기</a></p><p>단숙이 개발자가 쓴 공부법 소개 글이에요. 앱을 쓰면 성적이 얼마나 오른다고 약속하는 글은 아니에요.</p></section>
</article></main>'''
    page = head(path=path, title=title, desc=desc, og_alt='중학 영단어 공부법: 하루 20개, 떠올리기와 간격 복습', ld=data,
                extra_css=WORDS_CSS) + nav + body + tail
    (DOCS / path).mkdir(exist_ok=True)
    (DOCS / path / 'index.html').write_text(page, encoding='utf-8')


build_words()
build_middle()
print('ok', N, len(only2015), len(new2022))
