"""dansuki.com 검색용 페이지를 만든다(2026-11-03).
- /test/                   영단어 테스트(+ test/words.json)
- /basic-words/            교육부 기본 어휘 3000 목록(2022 개정, 학교급별 · 파생어 · 2022에서 빠진 100개)
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
PUBLISHED = '2026-11-03T14:15:38+09:00'  # 처음 올린 시각(git)
NOW = '2026-11-03T17:00:00+09:00'  # 고칠 때마다 바꾼다
DAY = '2026-11-03'
APP = 'https://apps.apple.com/kr/app/id6819707350'
e = lambda s: html.escape(s, quote=True)

# ── 템플릿 조각 ──────────────────────────────────────────────
nav = TPL[TPL.index('<nav class="top">'):TPL.index('<main')]
nav = nav.replace(' aria-current="page"', '')
tail = TPL[TPL.index('</article></main>') + len('</article></main>'):]
store_btn = re.search(r'<a class="store" href="https://apps\.apple\.com[^"]*" aria-label="App Store에서 단숙이 받기">.*?</a>', TPL, re.S).group(0)
store_btn += ' ' + re.search(r'<a class="store gp" href="https://play\.google\.com[^"]*"[^>]*>.*?</a>', TPL, re.S).group(0)  # 2026-11-04 Google Play 출시


def head(*, path, title, desc, og_alt, ld, og, extra_css=''):
    url = f'https://dansuki.com/{path}'
    return f'''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><meta name="theme-color" content="#F6F1E7"><meta property="og:type" content="article"><meta property="og:site_name" content="단숙이"><meta property="og:locale" content="ko_KR"><meta property="og:url" content="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:image" content="https://dansuki.com/img/{og}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{e(og_alt)}"><meta property="article:published_time" content="{PUBLISHED}"><meta property="article:modified_time" content="{NOW}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="https://dansuki.com/img/{og}"><meta name="twitter:image:alt" content="{e(og_alt)}"><meta name="apple-itunes-app" content="app-id=6819707350"><meta name="robots" content="index, follow, max-image-preview:large"><link rel="icon" href="/icon.png"><link rel="apple-touch-icon" href="/icon.png"><link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link rel="preload" href="/fonts/MaruBuri-sub.woff2?v=a7f3670f" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.min.css"><link rel="stylesheet" href="/site.css?v=45ca61e7"><link rel="stylesheet" href="/article.css?v=77964510">{extra_css}<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script><script src="/navigation.js?v=1058b464" defer></script></head><body>'''


def ld(*, path, title, desc, headline, crumb_name, og, keywords, extra=None):
    url = f'https://dansuki.com/{path}'
    org = {'@id': 'https://dansuki.com/#org', '@type': 'Organization', 'name': '단숙이', 'url': 'https://dansuki.com/'}
    art = {
        '@type': 'Article', '@id': url + '#article', 'url': url, 'mainEntityOfPage': {'@id': url + '#webpage'},
        'headline': headline, 'description': desc, 'inLanguage': 'ko-KR', 'datePublished': PUBLISHED, 'dateModified': NOW,
        'image': {'@type': 'ImageObject', 'url': f'https://dansuki.com/img/{og}', 'width': 1200, 'height': 630},
        'keywords': keywords,
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
# 2022 고시는 대표형 3,000개 옆 괄호에 파생어를 적는다(예: study (student)). 앱 데이터는 파생어를 따로 두고
# family2022로 대표형을 가리킨다. 칸(cell2022)마다 같은 단어군의 다른 단어를 괄호로 붙인다.
fam_key = lambda w: w.get('family2022') or w['word']
cell_of = {fam_key(w): w['word'] for w in cur}
DERIV = {}
for w in words:
    if w.get('grade2022') and not w.get('cell2022'):
        DERIV.setdefault(cell_of[fam_key(w)], []).append(w['word'])
only2015 = sorted((w for w in words if w.get('grade2015') and not w.get('grade2022')), key=lambda w: w['word'].lower())
n_deriv = sum(len(v) for v in DERIV.values())
new2022 = [w for w in cur if not w.get('grade2015')]
N = {k: len(v) for k, v in by.items()}
assert sum(N.values()) == len(cur) == 3000, N


def wslug(word):
    return re.sub(r'[^a-z0-9-]', '', word.lower().replace(' ', '-'))


def deriv(w):
    d = DERIV.get(w['word'])
    return f' <small class="deriv">({e(", ".join(sorted(d)))})</small>' if d else ''


def word_list(ws, slug):
    groups = {}
    for w in ws:
        ch = w['word'][0].upper()
        groups.setdefault(ch if ch.isalpha() else '#', []).append(w)
    letters = ''.join(f'<a href="#{slug}-{c.lower()}">{c}</a>' for c in groups)
    out = [f'<nav class="az" aria-label="알파벳으로 찾기">{letters}</nav>']
    for c, g in groups.items():
        items = ''.join(
            (f'<li><b lang="en"><a href="/words/{wslug(w["word"])}/">{e(w["word"])}</a>{deriv(w)}</b><span>{e(w["meaning"])}</span></li>' if w.get('cell2022') else f'<li><b lang="en">{e(w["word"])}{deriv(w)}</b><span>{e(w["meaning"])}</span></li>') for w in g)
        out.append(f'<div class="wgroup" style="--h1:{len(g) * 37 + 49}px;--h2:{(len(g) + 1) // 2 * 38 + 49}px"><h4 id="{slug}-{c.lower()}">{c}</h4><ul class="wlist">{items}</ul></div>')
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
/* 화면 밖 단어 묶음은 그리지 않는다(줄 수로 높이 어림, 한 번 그리면 실제 높이 기억). 부드러운 스크롤은 그리면서 높이가 바뀔 때
   바로가기 자리를 놓쳐서 이 페이지만 끈다(2026-11-03 속도 점검). */
html{scroll-behavior:auto}
.research-article .wgroup{content-visibility:auto;contain-intrinsic-size:auto var(--h2,600px)}
@media (max-width:640px){.research-article .wgroup{contain-intrinsic-size:auto var(--h1,1200px)}}
.research-article .wgroup h4{margin:18px 0 6px;font-size:15px;color:var(--muted);scroll-margin-top:96px}
.research-article .wlist{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 20px}
.research-article .wlist li{display:flex;gap:10px;align-items:baseline;padding:7px 0;border-bottom:1px solid var(--line);font-size:14.5px;line-height:1.45;min-width:0}
.research-article .wlist b{flex:0 0 auto;max-width:48%;font-weight:700;overflow-wrap:anywhere}
.research-article .wlist b small.deriv{font-weight:500;color:var(--muted);font-size:13px}
.research-article .wlist span{color:var(--muted);overflow-wrap:anywhere;word-break:keep-all}
.research-article details.old{margin:36px 0 0;border:1px solid var(--line);border-radius:18px;padding:4px 18px 14px;background:var(--surface)}
.research-article details.old summary{cursor:pointer;padding:12px 0;font-weight:700}
[hidden]{display:none!important}
.research-article.searching .wlist li:not(.hit),.research-article.searching .wgroup:not(.hit),.research-article.searching .level:not(.hit),.research-article.searching details.old:not(.hit),.research-article.searching .az{display:none}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.research-article .empty{display:none;padding:18px 0;color:var(--muted)}
@media (max-width:640px){.research-article .wlist{grid-template-columns:1fr}}
</style>'''

FIND_JS = '''<script>
// 단어 찾기: 영어나 뜻 일부로 거른다. 스크립트가 없어도 목록은 다 보인다(검색엔진 · 오래된 브라우저).
// 3,213줄이라 빠르게(2026-11-03 속도 점검): 줄마다 숨기지 않고, 맞는 줄에만 .hit를 달고 글 전체에 .searching 하나를
// 켠다(CSS가 나머지를 숨김). 지울 때는 .searching만 끈다. 찾기 목록은 처음 쓸 때 만들고, 바뀐 줄만 고친다.
(() => {
  const box = document.getElementById('find'), info = document.getElementById('find-info');
  if (!box) return;
  const root = document.getElementById('post'), empty = document.querySelector('.empty');
  const groups = [...document.querySelectorAll('.wgroup')], secs = [...document.querySelectorAll('.level, details.old')];
  const hint = info.textContent;
  let idx = null, last = '', t;
  const build = () => {
    idx = [];
    for (const g of groups) {
      g._s = g.closest('.level, details.old'); g._on = false;
      for (const li of g.querySelectorAll('li')) idx.push({ li, k: li.textContent.toLowerCase(), g, on: false });
    }
    for (const s of secs) s._on = false;
  };
  const mark = (o, on) => { if (o._on !== on) { o._on = on; (o.li || o).classList.toggle('hit', on); } };
  const run = () => {
    const q = box.value.trim().toLowerCase();
    if (q === last) return;
    last = q;
    if (!q) { root.classList.remove('searching'); info.textContent = hint; empty.style.display = 'none'; return; }
    if (!idx) build();
    const liveG = new Set();
    let n = 0;
    for (const o of idx) {
      const on = o.k.includes(q);
      if (o.on !== on) { o.on = on; o.li.classList.toggle('hit', on); }
      if (on) { n++; liveG.add(o.g); }
    }
    const liveS = new Set();
    for (const g of groups) { const on = liveG.has(g); mark(g, on); if (on) liveS.add(g._s); }
    for (const s of secs) { const on = liveS.has(s); mark(s, on); if (on && s.tagName === 'DETAILS') s.open = true; }
    root.classList.add('searching');
    info.textContent = n ? `${n.toLocaleString()}개 찾았어요` : '';
    empty.style.display = n ? 'none' : 'block';
    // 목록 깊이 내려와 찾으면 목록이 짧아져 결과가 화면 위로 사라진다(찾기 칸은 붙어 따라오므로 그대로 보임)
    // → 찾기 칸 바로 위 학교급 칩이 지나갔으면 그 자리로 올려, 찾기 칸 아래에 결과가 오게 한다.
    const top = document.querySelector('.lv-chips');
    if (top && top.getBoundingClientRect().bottom < 0) top.scrollIntoView({ block: 'start' });
  };
  box.addEventListener('focus', () => { if (!idx) build(); }, { once: true });
  box.addEventListener('input', () => { clearTimeout(t); t = setTimeout(run, 120); });
  // 바로가기(A~Z · 학교급)로 간 뒤, 그 사이 그려진 묶음의 높이가 어림과 달라 자리가 밀리면 한 번 더 맞춘다.
  const settle = () => {
    const el = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (!el || !el.closest('.level, details.old')) return;
    let n = 0;
    const fix = () => { el.scrollIntoView({ block: 'start' }); if (++n < 3) requestAnimationFrame(() => requestAnimationFrame(fix)); };
    requestAnimationFrame(fix);
  };
  addEventListener('hashchange', settle);
  if (location.hash) addEventListener('load', settle, { once: true });
})();
</script>'''


def build_words():
    path = 'basic-words/'
    title = '교육부 기본 어휘 3000 목록 · 초등 · 중학 · 고등 영단어 뜻 정리 | 단숙이'
    desc = ('2022 개정 교육과정 영어 기본 어휘 3,000개를 초등 800 · 중학 1,200 · 고등 1,000개로 나눠 뜻과 함께 정리했어요. '
            '2022 개정에서 빠진 단어와 파생어도 함께 정리했어요.')
    headline = '교육부 기본 어휘 3,000개, 학교급별로 한눈에'
    data = ld(path=path, title=title, desc=desc, headline=headline, crumb_name='기본 어휘 3000 목록', og='basic-words-og.png',
              keywords=['교육부 기본 어휘', '기본 어휘 3000', '2022 개정 교육과정 기본 어휘', '중학 영단어', '고등 영단어', '초등 영단어'])
    chips = ''.join(f'<a href="#{s}">{n} <small>{N[k]:,}개</small></a>' for k, n, s in LEVELS)
    chips += f'<a href="#only-2015">2022에서 빠짐 <small>{len(only2015)}개</small></a>'
    levels = ''
    blurb = {
        'elementary': '초등학교에서 배우는 기초 단어예요. 중학생이라도 여기서 막히는 단어가 있다면 먼저 채워 두는 게 좋아요.',
        'middle': '중학교 교과서와 시험에 자주 나오는 단어예요. 고등 단어의 바탕이 돼요.',
        'high': '고등학교 교과서와 수능 · 모의고사 지문의 바탕이 되는 단어예요.',
    }
    for k, n, s in LEVELS:
        levels += (f'<section class="level" id="{s}"><h3>{n} 기본 어휘 <small>{N[k]:,}개</small></h3>'
                   f'<p>{blurb[k]}</p>{word_list(by[k], s)}</section>')
    old = (f'<details class="old" id="only-2015"><summary>2022 개정에서 빠진 단어 {len(only2015)}개(2015 개정에만 있음)</summary>'
           f'<p>2022 개정 목록에서는 빠졌지만 예전 교재나 기출 지문에서는 여전히 만날 수 있는 단어예요. 단숙이에는 이 단어도 들어 있어요.</p>'
           f'{word_list(only2015, "old")}</details>')
    _nw = sorted(new2022, key=lambda w: w['word'])
    sample_new = ', '.join(w['word'] for w in _nw[::max(1, len(_nw) // 8)][:8])
    body = f'''<main class="research-main"><article class="wrap narrow research-article" id="post">
<header class="article-head"><p class="crumb"><a href="/">단숙이</a> › <a href="/method/">공부 방법</a> › 기본 어휘 목록</p><div class="series">교육부 기본 어휘 · 2022 개정 교육과정</div><h1>교육부 기본 어휘 3,000개,<br><span class="mark">학교급별로 한눈에</span></h1><p class="deck">초등 800 · 중학 1,200 · 고등 1,000.<br>뜻과 함께 정리하고, 찾아볼 수 있게 했어요.</p><div class="byline">글 · 단숙이를 만든 사람 <span aria-hidden="true">·</span> <time datetime="{DAY}">2026년 11월 3일</time></div></header>
<nav class="article-toc" aria-label="이 글의 내용"><p>이 글에서 살펴볼 내용</p><ol><li><a href="#what">기본 어휘가 뭔가요</a></li><li><a href="#count">학교급별로 몇 개인가요</a></li><li><a href="#diff">2015 개정과 무엇이 달라졌나요</a></li><li><a href="#list">3,000개 전체 목록</a></li><li><a href="#how">이 목록, 어떻게 외우면 좋을까요</a></li></ol></nav>
<p class="opening">단어장마다 고른 단어가 달라서<br>무엇부터 외워야 할지 헷갈릴 때가 있어요.</p>
<p>그럴 때 기준이 되는 목록이 있어요. 교육부가 영어과 교육과정에 함께 고시하는 <strong>기본 어휘 목록</strong>이에요. 교과서와 시험 문제를 만들 때 바탕이 되는 단어들이라, 기초를 다질 때 가장 먼저 챙길 만한 단어예요.</p>
<h2 id="what">기본 어휘는<br>어떤 단어인가요?</h2>
<p>기본 어휘는 영어 교육과정 문서 끝에 붙은 단어 목록이에요. 지금 학교에서 쓰는 것은 <strong>2022 개정 교육과정(교육부 고시 제2022-33호)</strong>의 목록이고, 그 전에는 <strong>2015 개정 교육과정(교육부 고시 제2015-74호)</strong>의 목록을 썼어요.</p>
<p>목록에는 대표 단어 3,000개가 있고, student 같은 파생어는 대표 단어 옆 괄호에 들어 있어요(예: study (student)). 이 페이지도 같은 방식으로 적었어요. 목록에는 뜻이 없어서, 이 페이지의 뜻은 단숙이 앱에서 쓰는 대표 뜻이에요. 뜻이 여러 개인 단어는 자주 쓰는 뜻을 먼저 적었어요.</p>
<h2 id="count">학교급별로<br>몇 개를 알아야 할까요?</h2>
<p>고시 원문은 3,000개 중 800개에 *, 1,200개에 ** 표시를 해 두었어요. *는 초등학교에서, **는 중학교와 고등학교 공통 과목에서 권장하는 단어예요. 이 페이지는 이 표시를 따라 초등 · 중학 · 고등으로 나눴어요.</p>
<div class="stats" aria-label="학교급별 기본 어휘 수"><div class="stat"><b>{N["elementary"]:,}개</b><span>초등</span></div><div class="stat"><b>{N["middle"]:,}개</b><span>중학</span></div><div class="stat"><b>{N["high"]:,}개</b><span>고등</span></div></div>
<p>중학생이라면 * 800개와 ** 1,200개, 모두 <strong>2,000개</strong>를 먼저 챙기면 돼요. 고등학생은 여기에 나머지 1,000개를 더해 3,000개가 바탕이 돼요.</p>
<p>교육과정은 학교에서 배우고 평가하는 어휘의 90% 이상(초 · 중학교와 고등학교 공통 · 일반 선택과목)을 이 기본 어휘 목록에서 쓰도록 권장해요. 기본 어휘부터 외우면 교과서와 시험 문제에 나오는 단어 대부분을 먼저 챙기는 셈이에요.</p>
<h2 id="diff">2015 개정과는<br>무엇이 달라졌나요?</h2>
<p>두 목록은 대부분 같아요. 2022 개정 대표 단어 3,000개 중 <strong>{3000 - len(new2022):,}개</strong>는 2015 개정에도 있던 단어예요. 2022 개정에서 새로 들어온 단어는 <strong>{len(new2022)}개</strong>예요.</p>
<p>2015 개정에서 따로 한 칸이던 단어 중 <strong>{n_deriv}개</strong>는 2022 개정에서 대표 단어 옆 괄호로 들어갔어요. student는 study 옆에, decision은 decide 옆에 있는 식이에요. 목록에서 아예 빠진 단어는 <strong>{len(only2015)}개</strong>예요.</p>
<p>새로 들어온 단어에는 {e(sample_new)} 같은 일상 단어가 많아요. 빠진 {len(only2015)}개는 목록 맨 아래에 따로 모아 뒀어요.</p>
<h2 id="list">기본 어휘<br>3,000개 전체 목록</h2>
<div class="lv-chips">{chips}</div>
<div class="finder" role="search"><label class="sr-only" for="find">단어 찾기</label><input id="find" type="search" aria-label="단어 찾기" placeholder="단어 찾기 (영어나 뜻)" autocomplete="off" enterkeyhint="search"><p id="find-info" aria-live="polite">영어나 뜻 일부를 써 보세요. 예: environment, 환경</p></div>
<p class="empty">찾는 단어가 없어요. 철자를 한 번 더 확인해 보세요.</p>
{levels}{old}
<h2 id="how">이 목록,<br>어떻게 외우면 좋을까요?</h2>
<p>3,000개를 한 번에 외우려 하면 금방 지쳐요. 하루에 조금씩, 대신 매일 하는 쪽이 오래 가요.</p>
<div class="study"><h3>기본 어휘를 외우는 순서</h3><ul><li><strong>초등 단어부터 훑어보기</strong><br>아는 단어는 빠르게 넘기고, 막히는 단어만 골라 두세요.</li><li><strong>보기 전에 먼저 떠올리기</strong><br>뜻을 가리고 떠올려 본 뒤 확인하면, 그냥 읽을 때보다 오래 남아요.</li><li><strong>잊을 때쯤 다시 보기</strong><br>외운 단어는 며칠 뒤, 일주일 뒤, 몇 주 뒤에 다시 확인해요.</li></ul></div>
<p>자세한 방법은 <a href="/middle-school-words/">중학 영단어 공부법</a>과 <a href="/spaced-review/">복습 간격 연구 이야기</a>에 정리해 뒀어요.</p>
{app_box("기본 어휘 3,000개,<br>하루 20개씩 단숙이로.", ["단숙이는 이 목록을 바탕으로 만든 무료 영단어 · 숙어 앱이에요. 하루 단어 20개를 먼저 떠올리고 고르는 방식으로 익히고, 외운 단어는 2일 · 7일 · 21일 뒤에 다시 물어봐요.", "외운 단어는 셜록 홈스, 오즈의 마법사 같은 이야기에서 다시 만나요. 광고와 가입 없이 바로 시작할 수 있어요."])}
<section class="article-refs" aria-label="출처"><h2>출처</h2><p>교육부 고시 제2022-33호 [별책 14] 영어과 교육과정 [별표 3] 기본 어휘 목록, 교육부 고시 제2015-74호 [별책 14] 영어과 교육과정 기본 어휘 목록. 원문은 <a href="https://ncic.re.kr/" target="_blank" rel="noopener">국가교육과정정보센터</a>에서 받을 수 있어요.</p><p>학교급은 고시 원문의 *, ** 표시를 따랐고, 뜻은 단숙이가 앱에서 쓰려고 정리한 것이에요. 교육부, 한국교육과정평가원과는 관계없이 개인이 만든 페이지예요.</p></section>
</article></main>'''
    page = head(path=path, title=title, desc=desc, og_alt='교육부 기본 어휘 3,000개 학교급별 목록', ld=data, og='basic-words-og.png', extra_css=WORDS_CSS) + nav.replace(f'<a href="/{path}">', f'<a href="/{path}" aria-current="page">') + body + tail.replace('</body>', FIND_JS + '</body>')
    (DOCS / path).mkdir(exist_ok=True)
    (DOCS / path / 'index.html').write_text(page, encoding='utf-8')


def build_middle():
    path = 'middle-school-words/'
    title = '중학 영단어 공부법 · 하루 몇 개, 어떻게 외울까 | 단숙이'
    desc = ('중학생 영단어는 하루 몇 개가 좋을까요? 교육부 기본 어휘 2,000개 기준, 복습량 계산표, 먼저 떠올리기와 간격 복습 연구, '
            '자주 하는 실수와 하루 15분 공부 순서를 정리했어요.')
    headline = '중학 영단어, 하루 20개를 오래 남기는 방법'
    data = ld(path=path, title=title, desc=desc, headline=headline, crumb_name='중학 영단어 공부법', og='middle-school-words-og.png',
              keywords=['중학 영단어 공부법', '중학생 영단어', '영단어 외우는 법', '영단어 하루 몇 개', '간격 반복', '영단어 암기'])
    mid = by['middle']
    pick = ['achieve', 'experience', 'opinion', 'prepare', 'communicate', 'imagine', 'improve', 'protect']
    m = {w['word']: w['meaning'] for w in mid + by['elementary']}
    sample = ''.join(f'<li><b lang="en">{e(k)}</b><span>{e(m[k])}</span></li>' for k in pick if k in m)
    body = f'''<main class="research-main"><article class="wrap narrow research-article" id="post">
<header class="article-head"><p class="crumb"><a href="/">단숙이</a> › <a href="/method/">공부 방법</a> › 중학 영단어 공부법</p><div class="series">중학 영단어 · 공부법</div><h1>중학 영단어, <br><span class="mark">하루 20개를 오래 남기는</span> 방법</h1><p class="deck">몇 개를 외워야 하는지, 하루에 얼마나 할지, <br>어떻게 해야 안 잊는지 차례로 정리했어요.</p><div class="byline">글 · 단숙이를 만든 사람 <span aria-hidden="true">·</span> <time datetime="{DAY}">2026년 11월 3일</time> <span aria-hidden="true">·</span> 교육부 고시 제2022-33호 · Karpicke &amp; Roediger(2008) · Kim &amp; Webb(2022)</div></header>
<nav class="article-toc" aria-label="이 글의 내용"><p>이 글에서 살펴볼 내용</p><ol><li><a href="#how-many">중학생은 몇 개를 알아야 할까</a></li><li><a href="#diagnose">어디서부터 시작할까: 5분 진단</a></li><li><a href="#per-day">하루에 몇 개가 좋을까: 복습량 계산</a></li><li><a href="#recall">읽기보다 먼저 떠올리기</a></li><li><a href="#spacing">잊을 때쯤 다시 보기</a></li><li><a href="#sound">소리 내어 읽고, 철자도 떠올리기</a></li><li><a href="#mistakes">자주 하는 실수 다섯 가지</a></li><li><a href="#context">문장과 이야기에서 다시 만나기</a></li><li><a href="#routine">하루 15분 공부 순서</a></li><li><a href="#faq">자주 묻는 질문</a></li></ol></nav>
<p class="opening">어제 외운 단어가 <br>오늘 시험지에서 생각나지 않을 때가 있어요.</p>
<p>단어를 열심히 봤는데도 잘 떠오르지 않는다면, 외운 시간보다 <strong>외우는 방법</strong>을 바꿔 볼 때예요. 중학 영단어는 고등 영어의 바탕이 되니까, 지금 오래 남는 방식으로 쌓아 두면 나중이 훨씬 편해요.</p>
<h2 id="how-many">중학생은 영단어를 <br>몇 개나 알아야 할까요?</h2>
<p>기준으로 삼기 좋은 건 교육부가 영어과 교육과정과 함께 고시한 <a href="/basic-words/">기본 어휘 목록</a>이에요. 2022 개정 교육과정(교육부 고시 제2022-33호)의 기본 어휘는 3,000개이고, 원문은 그중 일부에 이렇게 표시해 두었어요.</p>
<div class="stats" aria-label="기본 어휘 표시"><div class="stat"><b>{N["elementary"]:,}개</b><span>* 초등학교 권장</span></div><div class="stat"><b>{N["middle"]:,}개</b><span>** 중학교 · 고1 공통과목 권장</span></div><div class="stat"><b>1,500</b><span>중학교 학습 어휘 수(이내)</span></div></div>
<p>* 표시 <a href="/basic-words/#elem">{N["elementary"]:,}개</a>는 초등학교에서, ** 표시 <a href="/basic-words/#middle">{N["middle"]:,}개</a>는 중학교와 고등학교 공통과목(고1 공통영어 등)에서 쓰기를 권장해요. 교육과정은 따로 학년군마다 배울 <strong>학습 어휘 수</strong>도 정해 두었는데, 중학교 1~3학년은 1,500단어 이내예요.</p>
<p>정리하면 중학생은 * · ** 표시 단어 <strong>2,000개</strong>를 3년에 걸쳐 익혀 두면, 중학교 교과서는 물론 고1 공통영어까지 바탕이 이어져요. 교육과정은 학교에서 배우고 평가하는 어휘의 90% 이상을 이 기본 어휘 목록에서 쓰도록 권장하고 있어요.</p>
<ul class="wlist" aria-label="** 중학 기본 어휘 예시">{sample}</ul>
<h2 id="diagnose">어디서부터 시작할까요? <br>5분 진단</h2>
<p>몇 학년인지보다 <strong>지금 아는 단어</strong>가 출발점이에요. 5분이면 알아볼 수 있어요.</p>
<div class="study"><h3>5분 진단</h3><ul><li><strong>초등 단어 20개 떠올려 보기</strong><br><a href="/basic-words/#elem">초등 기본 어휘</a>에서 아무 곳이나 20개를 골라 뜻을 손으로 가리고 떠올려 보세요.</li><li><strong>3개 넘게 막히면 초등 단어부터</strong><br>기초가 비어 있으면 중학 단어도 잘 붙지 않아요. 초등 단어는 빨리 지나가니 부담 갖지 않아도 돼요.</li><li><strong>거의 다 알면 중학 단어로</strong><br><a href="/basic-words/#middle">중학 기본 어휘</a>에서 같은 방법으로 20개를 떠올려 보고, 막히는 단어부터 시작해요.</li></ul></div>
<h2 id="per-day">하루에 몇 개씩 <br>외우는 게 좋을까요?</h2>
<p>하루 30~50개를 권하는 글도 많아요. 그런데 숫자를 정할 때는 <strong>새 단어</strong>만 볼 게 아니라, 며칠 뒤 다시 볼 <strong>복습 단어</strong>까지 같이 세어야 해요.</p>
<p>외운 단어를 2일 · 7일 · 21일 뒤에 한 번씩 다시 확인한다고 해 볼게요. 그러면 3주쯤 지난 날부터는 날마다 새 단어에 더해, 이틀 전 · 일주일 전 · 3주 전에 외운 단어가 함께 돌아와요.</p>
<div class="chart-table-wrap"><table class="chart-table"><caption class="sr-only">하루 새 단어 수에 따른 3주 뒤 하루 공부량</caption><thead><tr><th>하루 새 단어</th><th>3주 뒤 복습 단어</th><th>3주 뒤 하루 합계</th><th>2,000개 한 번 보기</th></tr></thead><tbody><tr><td>10개</td><td>약 30개</td><td>약 40개</td><td>약 200일</td></tr><tr><td><strong>20개</strong></td><td><strong>약 60개</strong></td><td><strong>약 80개</strong></td><td><strong>약 100일</strong></td></tr><tr><td>30개</td><td>약 90개</td><td>약 120개</td><td>약 67일</td></tr><tr><td>50개</td><td>약 150개</td><td>약 200개</td><td>약 40일</td></tr></tbody></table></div>
<p><small>외운 단어를 한 번에 다 맞힌다고 칠 때의 어림이에요. 틀린 단어가 다시 나오면 조금 더 늘어요.</small></p>
<p>하루 50개는 처음 며칠은 할 만하지만, 3주쯤 지나면 하루 200개가 돼요. 그때부터 복습을 건너뛰기 쉽고, 복습을 빼면 외운 단어가 다시 흐려져요. 하루 20개면 3주 뒤에도 80개 안팎이라 매일 이어 가기 쉬워요. 그래서 단숙이는 하루 단어 20개 · 숙어 5개를 하루 몫으로 정했어요.</p>
<div class="quote">많이 외운 날보다, <br>빠지지 않은 날이 더 중요해요.</div>
<p>바쁜 날엔 다섯 개만 해도 괜찮아요. 끊기지 않는 게 먼저예요.</p>
<h2 id="recall">눈으로 읽기보다 <br>먼저 떠올려 보기</h2>
<p>단어장을 여러 번 읽으면 아는 것 같은 느낌이 들어요. 그런데 시험에서는 단어를 보고 뜻을 <strong>스스로 꺼내야</strong> 해요. 그래서 공부할 때도 뜻을 가리고 먼저 떠올려 본 뒤 확인하는 게 좋아요.</p>
<p>Karpicke와 Roediger(2008)는 대학생들에게 외국어 단어 40쌍을 외우게 하고, 한 번 맞힌 단어를 그 뒤에도 계속 떠올리게 한 경우와 다시 읽기만 한 경우를 비교했어요. 일주일 뒤 시험에서 계속 떠올린 쪽은 약 80%를 기억했고, 맞힌 뒤 떠올리기를 멈춘 쪽은 약 35%였어요. 다시 읽은 횟수는 결과에 거의 영향이 없었어요. <a href="#reference-1" aria-label="참고 논문 1">[1]</a></p>
<div class="study"><h3>떠올리기를 공부에 넣는 법</h3><ul><li><strong>영어를 보고 뜻을, 뜻을 보고 영어를</strong><br>두 방향을 다 해 봐야 읽기와 쓰기에서 모두 떠올라요.</li><li><strong>모르면 바로 정답과 예문 보기</strong><br>틀린 단어는 조금 뒤에 한 번 더 물어보세요.</li><li><strong>빨리 떠오르는지도 보기</strong><br>한참 생각해야 떠오르는 단어는 아직 덜 외운 단어예요.</li></ul></div>
<p>단숙이가 이 방법을 어떻게 담았는지는 <a href="/method/">단숙이 공부법</a>에 연구와 함께 정리해 뒀어요.</p>
<h2 id="spacing">잊을 때쯤 <br>다시 보기</h2>
<p>오늘 외운 단어는 며칠 지나면 흐려져요. 이때 다시 떠올려 보면 그 단어는 더 오래 남아요. 그래서 새 단어만 늘리지 말고, <strong>예전에 외운 단어를 다시 볼 날</strong>도 정해 두는 게 좋아요.</p>
<p>Kim과 Webb(2022)은 제2언어 학습 실험 48개(학습자 3,411명)를 모아 분석했어요. 몰아서 연습하는 것보다 간격을 두고 연습하는 쪽이 도움이 됐고, 특히 시간이 지난 뒤 본 시험에서 차이가 컸어요. <a href="#reference-2" aria-label="참고 논문 2">[2]</a></p>
<p>단숙이는 외운 단어를 <strong>2일 · 7일 · 21일</strong> 뒤에 다시 물어봐요. 자세한 내용은 <a href="/spaced-review/">복습 간격 연구 이야기</a>에서 도표와 함께 볼 수 있어요.</p>
<h2 id="sound">소리 내어 읽고, <br>철자도 떠올리기</h2>
<p>소리를 모르는 단어는 들어도 못 알아듣고, 읽을 때도 머릿속에서 멈칫해요. 새 단어는 발음을 한 번 듣고 <strong>소리 내어 따라 읽는</strong> 게 좋아요.</p>
<p>철자가 필요한 단어는 뜻을 보고 영어를 떠올린 다음, 한 번만 직접 써 보세요. 같은 단어를 열 번 베껴 쓰는 것보다, 가린 채로 한 번 떠올려 쓰는 쪽이 앞에서 본 떠올리기에 가까워요.</p>
<h2 id="mistakes">자주 하는 실수 <br>다섯 가지</h2>
<div class="study"><h3>이렇게 하면 금방 잊어요</h3><ul><li><strong>깜지처럼 여러 번 쓰기만 하기</strong><br>손은 바쁘지만 머리는 뜻을 꺼내지 않아요. 쓰더라도 가리고 떠올린 뒤 써요.</li><li><strong>영어 → 뜻 한 방향만 연습하기</strong><br>뜻을 보고 영어를 떠올리는 연습을 안 하면 쓰기와 말하기에서 막혀요.</li><li><strong>시험 전날 몰아서 하기</strong><br>다음 날 시험은 버텨도, 몇 주 뒤엔 대부분 흐려져요.</li><li><strong>뜻을 하나만 외우기</strong><br>자주 쓰는 뜻 두세 개는 함께 봐 두면 지문에서 덜 헷갈려요.</li><li><strong>외운 단어는 다시 안 보기</strong><br>한 번 맞혔다고 끝이 아니에요. 며칠 뒤 다시 떠올려야 오래 남아요.</li></ul></div>
<h2 id="context">문장과 이야기에서 <br>다시 만나기</h2>
<p>단어만 따로 외우면 어디에 쓰는지 잘 와닿지 않아요. 외운 단어가 들어간 예문을 소리 내어 읽거나, 짧은 이야기 속에서 다시 만나면 뜻이 더 또렷해져요.</p>
<p>단숙이에는 셜록 홈스, 오즈의 마법사 같은 이야기 19편을 중학 · 고등 영어로 다시 쓴 이야기 탭이 있어요. 외운 단어에는 형광펜이 칠해져서, 외울수록 이야기가 술술 읽혀요.</p>
<h2 id="routine">바로 해 보는 <br>하루 15분 공부 순서</h2>
<div class="study"><h3>오늘부터 이렇게</h3><ul><li><strong>어제 · 지난주 단어 다시 떠올리기 (5분)</strong><br>뜻을 가리고 먼저 떠올린 뒤 확인해요. 틀린 단어는 따로 표시해요.</li><li><strong>새 단어 20개 (8분)</strong><br>다섯 개씩 끊어서 보고, 바로 그 다섯 개를 가리고 떠올려 봐요. 발음도 한 번씩 소리 내어 읽어요.</li><li><strong>틀린 단어만 한 번 더 (2분)</strong><br>오늘 틀린 단어를 마지막에 한 번 더 물어보고 끝내요.</li></ul></div>
<p>처음 며칠은 복습할 단어가 적어서 금방 끝나요. 3주쯤 지나 복습이 자리를 잡으면, 위 표처럼 하루 80개 안팎을 다시 만나게 돼요.</p>
<h2 id="faq">자주 묻는 질문</h2>
<h3>중1인데 중학 단어부터 해야 하나요?</h3>
<p>위의 5분 진단을 먼저 해 보세요. 초등 단어에서 3개 넘게 막히면 초등 단어부터 하는 게 결국 더 빨라요.</p>
<h3>하루 50개씩 하면 더 빨리 끝나지 않나요?</h3>
<p>처음엔 빠르지만, 3주쯤 지나면 복습까지 하루 200개 안팎이 돼요. 복습을 건너뛰기 시작하면 외운 단어가 다시 흐려지니, 오래 이어 갈 수 있는 양을 고르는 게 좋아요.</p>
<h3>바쁜 날에 하루 빠지면요?</h3>
<p>다음 날 복습 단어부터 하면 돼요. 새 단어는 줄이거나 하루 쉬어도 괜찮아요. 단숙이에서는 1분만(다섯 문제) 해도 공부한 날로 쳐요.</p>
<h3>단어장과 앱 중 무엇이 좋나요?</h3>
<p>무엇을 쓰든 먼저 떠올리기와 다시 보기가 들어 있으면 돼요. 단어장이라면 뜻을 가리는 종이와 복습 날짜 표를 함께 쓰세요. 앱은 복습할 날을 대신 챙겨 준다는 점이 편해요.</p>
<h3>뜻이 여러 개인 단어는요?</h3>
<p>처음엔 가장 자주 쓰는 뜻 하나로 시작하고, 예문에서 다른 뜻을 만나면 그때 더해 가세요.</p>
{app_box("하루 20개, <br>단숙이가 순서를 챙겨 줄게요.", ["단숙이는 교육부 기본 어휘로 만든 무료 중고등 영단어 · 숙어 앱이에요. 새 단어는 플래시카드로 먼저 보고, 뜻을 떠올린 뒤 고르는 문제로 익혀요. 외운 단어는 2일 · 7일 · 21일 뒤에 다시 물어봐요.", "단어 하나를 외울 때마다 키링에 조각이 하나씩 끼워져요. 광고와 가입 없이 바로 시작할 수 있어요."])}
<p class="endline">오늘 외운 스무 개가, <br>다음 주에도 떠오르도록.</p>
<section class="article-refs" aria-label="참고 자료"><h2>참고 자료</h2><p id="reference-1">[1] Karpicke, J. D., &amp; Roediger, H. L. (2008). <em>The Critical Importance of Retrieval for Learning.</em> Science, 319(5865), 966–968.<br><a href="https://doi.org/10.1126/science.1152408" target="_blank" rel="noopener">https://doi.org/10.1126/science.1152408</a></p><p id="reference-2">[2] Kim, S. K., &amp; Webb, S. (2022). <em>The Effects of Spaced Practice on Second Language Learning: A Meta-Analysis.</em> Language Learning, 72(1), 269–319.<br><a href="https://doi.org/10.1111/lang.12479" target="_blank" rel="noopener">https://doi.org/10.1111/lang.12479</a></p><p>[3] 교육부 고시 제2022-33호 [별책 14] 영어과 교육과정, 기본 어휘 관련 지침과 [별표 3] 기본 어휘 목록. 원문은 <a href="https://ncic.re.kr/" target="_blank" rel="noopener">국가교육과정정보센터</a>에서 받을 수 있어요.</p><p>더 읽기: <a href="/basic-words/">교육부 기본 어휘 3,000개 목록</a> · <a href="/method/">단숙이 공부법과 참고 연구</a> · <a href="/spaced-review/">복습 간격 연구 이야기</a></p><p>단숙이 개발자가 쓴 공부법 소개 글이에요. 연구진이 단숙이를 검증하거나 추천했다는 뜻은 아니고, 앱을 쓰면 성적이 얼마나 오른다고 약속하는 글도 아니에요.</p></section>
</article></main>'''
    page = head(path=path, title=title, desc=desc, og_alt='중학 영단어 공부법: 하루 20개, 떠올리기와 간격 복습', ld=data, og='middle-school-words-og.png',
                extra_css=WORDS_CSS) + nav.replace(f'<a href="/{path}">', f'<a href="/{path}" aria-current="page">') + body + tail
    (DOCS / path).mkdir(exist_ok=True)
    (DOCS / path / 'index.html').write_text(page, encoding='utf-8')


build_words()
build_middle()
# ── /test/ 영단어 테스트(2026-11-03) ──────────────────────────────
# 기본 어휘 3,000개(2022 대표형)를 초등 6 · 중학 8 · 고등 6문제로 뽑아 아는 단어 수를 어림한다.
# 찍기 보정: 맞힘 R, 틀림 W(모르겠어요 · 시간 초과는 빼고), 보기 4개 → 아는 비율 = max(0, (R - W/3) / n).
# 단어 데이터는 시작할 때 /test/words.json으로 받는다(첫 화면 가볍게).
import random as _random

TEST_N = {'elementary': 6, 'middle': 8, 'high': 6}


def build_test_data():
    pool = {k: [] for k, _, _ in LEVELS}
    for w in cur:
        if len(w['word']) < 3 or w['meaning'].startswith('~') or w['word'].startswith(('twenty-', 'thirty-')):  # 서수 풀어 쓴 말은 문제로 뜻이 적다
            continue
        d = w['distractors']
        near = d['enKo'][:d.get('nearEnKo', 0)]
        rest = d['enKo'][d.get('nearEnKo', 0):]
        opts = []
        for m in near[:1] + rest:
            if m != w['meaning'] and m not in opts:
                opts.append(m)
            if len(opts) >= 4:
                break
        if len(opts) < 3:
            continue
        pool[w['grade2022']].append([w['word'], w['meaning'], opts])
    # 「빨간 머리 연맹」 전체에서 기본 어휘가 나온 횟수(학교급별) → 읽히는 % 어림
    byid = {w['id']: w for w in words}
    book = json.loads((DOCS / 'stories/red_headed_league.r1.json').read_text(encoding='utf-8'))
    cnt = {k: 0 for k, _, _ in LEVELS}
    for c in book['chapters']:
        for p in c['paragraphs']:
            for tok in p['en']:
                x = byid.get(tok[1]) if tok[1] else None
                if x and x.get('grade2022'):
                    cnt[x['grade2022']] += 1
    out = {'v': 1, 'N': N, 'ask': TEST_N, 'pool': pool, 'book': {'title': book['titleKo'], 'count': cnt}}
    (DOCS / 'test').mkdir(exist_ok=True)
    (DOCS / 'test/words.json').write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    return {k: len(v) for k, v in pool.items()}, cnt


TEST_CSS = '''<style>
/* 영단어 테스트(2026-11-04 다시 만듦): 표지 → 집중 풀이 화면 → 채점된 결과표 */
.quiz{scroll-margin-top:84px;--ok:#2F7D4F;--ok-bg:#DDEFE3;--no:#B8324E;--no-bg:#F7DDE2;margin:0 0 8px;border:1px solid var(--line);border-radius:28px;background:var(--surface);box-shadow:var(--shadow);padding:32px 28px 26px}
@media (prefers-color-scheme:dark){.quiz{--ok:#7FCB9A;--ok-bg:#1E3527;--no:#F09AAB;--no-bg:#3E2027}}
.quiz [hidden]{display:none!important}
.quiz .qtag{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:700;letter-spacing:.02em;padding:6px 13px;border-radius:999px;background:var(--text);color:var(--canvas)}
.quiz .go:focus-visible,.quiz .opt:focus-visible,.quiz .skip:focus-visible,.quiz .x:focus-visible,.quiz .acts button:focus-visible{outline:3px solid var(--highlight);outline-offset:2px}
/* 표지 */
.cover{text-align:center}
.cover .friend{margin:0 0 18px;padding:12px 14px;border-radius:14px;background:var(--mark);font-weight:600;font-size:15px}
.cover h1{margin:18px 0 0;font-size:clamp(30px,7vw,42px);line-height:1.32;word-break:keep-all}
.cover .mascot{display:flex;align-items:center;justify-content:center;gap:12px;margin:22px auto 0;max-width:430px}
.cover .mascot img{width:60px;height:60px;border-radius:17px;flex:0 0 auto;box-shadow:var(--shadow)}
.cover .bubble{position:relative;margin:0;text-align:left;font-size:15px;line-height:1.55;padding:11px 14px;border-radius:16px;background:var(--canvas);border:1px solid var(--line);word-break:keep-all}
.cover .bubble::before{content:'';position:absolute;left:-7px;top:50%;width:12px;height:12px;margin-top:-6px;background:var(--canvas);border-left:1px solid var(--line);border-bottom:1px solid var(--line);transform:rotate(45deg)}
.spec{display:grid;grid-template-columns:repeat(3,1fr);margin:26px 0 0;border:1px solid var(--line);border-radius:18px;background:var(--canvas)}
.spec div{padding:14px 6px 12px}
.spec div+div{border-left:1px dashed var(--line)}
.spec dt{font-size:13px;color:var(--muted)}
.spec dd{margin:2px 0 0;font-family:'MaruBuri',serif;font-size:28px;line-height:1.3;font-variant-numeric:tabular-nums}
.spec dd small{font-size:15px;margin-left:2px}
.quiz .rules{display:block;margin:22px 0 0;text-align:left;grid-template-columns:none}
.rules h2{margin:0 0 10px;font-size:15px;font-family:inherit;font-weight:700;letter-spacing:0}
.rules ol{list-style:none;margin:0;padding:0;display:grid;gap:9px}
.rules li{display:flex;gap:10px;align-items:baseline;font-size:15px;line-height:1.55;color:var(--muted);word-break:keep-all}
.rules li b{flex:0 0 auto;display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:var(--highlight);color:#23211E;font-size:12.5px}
.rules li strong{color:var(--text);font-weight:600}
.quiz .go{margin-top:24px;font:inherit;font-weight:700;font-size:17.5px;border:0;border-radius:18px;padding:18px 20px;background:var(--text);color:var(--canvas);cursor:pointer;width:100%;display:flex;align-items:center;justify-content:center;gap:8px}
.quiz .go svg{width:20px;height:20px}
.quiz .go[disabled]{opacity:.6;cursor:progress}
.research-article .cover .fine{display:block;margin:12px 0 0;padding:0;border:0;font-size:13px;line-height:1.6;color:var(--muted)}
.research-article .cover .fine span{margin:0 5px}
.quiz .err{color:var(--no);font-size:15px;margin:14px 0 0}
/* 풀이: 시작하면 화면 전체를 덮는다(메뉴 · 받기 띠 · 아래 글은 안 보이게). 앱 문제 화면처럼 카드 한 장에 단어 · 보기 · 시간 막대 */
body.testing{overflow:hidden}
body.testing .quiz{position:fixed;inset:0;z-index:1000;margin:0;border:0;border-radius:0;box-shadow:none;padding:0;background:var(--canvas);overflow-y:auto;overscroll-behavior:contain}
.solve{display:flex;flex-direction:column;min-height:100vh;min-height:100dvh;max-width:560px;margin:0 auto;padding:max(10px,env(safe-area-inset-top)) 16px max(16px,env(safe-area-inset-bottom))}
.qhead{display:grid;grid-template-columns:44px 1fr auto;align-items:center;gap:10px}
.quiz .x{width:44px;height:44px;margin-left:-8px;border-radius:50%;border:0;background:none;color:var(--text);cursor:pointer;display:grid;place-items:center;padding:0}
.quiz .x svg{width:24px;height:24px}
.qhead .qn{font-size:15px;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.qhead .qn b{color:var(--text)}
.dots{display:grid;grid-template-columns:repeat(20,1fr);gap:3px;list-style:none;margin:0;padding:0}
.dots li{height:6px;border-radius:99px;background:var(--line)}
.dots li.now{background:var(--text)}
.dots li.ok{background:var(--ok)}
.dots li.no{background:var(--no)}
.dots li.sk{background:var(--faint)}
.qcard{position:relative;flex:1;display:flex;flex-direction:column;justify-content:center;margin:22px 0 0;padding:28px 20px 18px;background:var(--surface);border:1px solid var(--line);border-radius:30px;box-shadow:var(--shadow)}
.qcard::before{content:'';position:absolute;left:22px;right:22px;top:-11px;height:40px;border:1px solid var(--line);border-bottom:0;border-radius:24px 24px 0 0;background:var(--surface);z-index:-1}
.qtop{display:flex;flex-direction:column;align-items:center;text-align:center}
.qtop .lv{font-size:13px;font-weight:700;color:var(--muted);border-radius:999px;padding:4px 11px;background:var(--canvas)}
.qtop img{width:52px;height:52px;border-radius:15px;margin:16px 0 0}
.quiz .word{margin:10px 0 0;font-family:'MaruBuri',serif;font-weight:400;font-size:46px;line-height:1.2;overflow-wrap:anywhere}
.quiz .hint{margin:8px 0 0;color:var(--muted);font-size:14.5px;min-height:1.6em}
.quiz .hint.ok{color:var(--ok);font-weight:700}
.quiz .hint.no{color:var(--no);font-weight:700}
.opts{display:grid;gap:10px;margin:18px 0 0}
.opts.wait,.skip.wait{visibility:hidden}
.quiz .opt{font:inherit;font-size:17px;line-height:1.45;text-align:left;border:1.5px solid transparent;border-radius:18px;padding:14px 16px 14px 14px;background:var(--canvas);color:var(--text);cursor:pointer;min-height:62px;word-break:keep-all;display:flex;align-items:center;gap:14px;transition:background-color .15s,border-color .15s,opacity .2s,transform .08s}
.opts.in .opt{animation:optin .22s ease-out both}
.opts.in .opt:nth-child(2){animation-delay:.04s}.opts.in .opt:nth-child(3){animation-delay:.08s}.opts.in .opt:nth-child(4){animation-delay:.12s}
@keyframes optin{from{opacity:0;transform:translateY(8px)}}
.quiz .opt .k{flex:0 0 auto;width:30px;height:30px;border-radius:9px;display:grid;place-items:center;font-size:14px;font-weight:700;color:var(--muted);background:var(--sunk)}
@media (hover:hover){.quiz .opt:not([disabled]):hover{border-color:var(--line)}}
.quiz .opt:not([disabled]):active{transform:scale(.985)}
.quiz .opt[disabled]{cursor:default}
.quiz .opt.ok{background:var(--ok-bg);border-color:var(--ok)}
.quiz .opt.ok .k{background:var(--ok);color:var(--surface)}
.quiz .opt.no{background:var(--no-bg);border-color:var(--no)}
.quiz .opt.no .k{background:var(--no);color:var(--surface)}
.quiz .opt.dim{opacity:.45}
.qtimer{height:5px;margin:16px 2px 0;border-radius:99px;background:var(--line);overflow:hidden}
.qtimer i{display:block;height:100%;background:var(--muted);border-radius:99px;transform-origin:left}
.qtimer.low i{background:var(--no)}
.quiz .skip{display:block;margin:8px auto 0;font:inherit;font-weight:600;font-size:16px;border:0;border-radius:12px;background:none;color:var(--muted);cursor:pointer;padding:12px 18px}
@media (hover:hover){.quiz .skip:hover{color:var(--text)}}
@media (min-width:640px){.quiz .word{font-size:54px}.qcard{flex:0 0 auto;margin-top:8vh;padding:40px 36px 22px}}
/* 결과표 */
.report .rtop{display:flex;justify-content:space-between;align-items:center;gap:12px;padding-bottom:16px;border-bottom:1px dashed var(--line)}
.report .rtop time{font-size:13.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.report .of{margin:20px 0 0;color:var(--muted);font-size:15.5px}
.report .big{margin:4px 0 0;font-family:'MaruBuri',serif;font-size:60px;line-height:1.15;font-variant-numeric:tabular-nums}
.report .big small{font-size:22px;margin-left:4px}
.report .stage-l{margin:12px 0 0;display:inline-flex;gap:8px;align-items:center;font-size:15px;padding:7px 13px;border-radius:12px;background:var(--mark)}
.report .stage-l b{font-weight:700}
.sheet{margin:22px 0 0;padding:16px 14px 12px;border-radius:18px;background:var(--canvas);border:1px solid var(--line)}
.sheet .sh-h{display:flex;justify-content:space-between;align-items:baseline;gap:10px;font-size:15px;padding:0 4px}
.sheet .sh-h span{color:var(--muted);font-size:14px;font-variant-numeric:tabular-nums}
.sheet ol{list-style:none;margin:12px 0 0;padding:0;display:grid;grid-template-columns:repeat(10,1fr);row-gap:6px}
.sheet li{display:grid;justify-items:center;gap:5px;padding:6px 0;font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.mk{display:block;position:relative;width:18px;height:18px}
.mk.m-ok{border:2.5px solid var(--ok);border-radius:50%}
.mk.m-no::before,.mk.m-no::after{content:'';position:absolute;left:50%;top:-1px;width:2.5px;height:20px;margin-left:-1.25px;background:var(--no);border-radius:2px;transform:rotate(45deg)}
.mk.m-no::after{transform:rotate(-45deg)}
.mk.m-skip::before{content:'';position:absolute;left:3px;right:3px;top:50%;height:2.5px;margin-top:-1.25px;background:var(--faint);border-radius:2px}
.sheet .legend{display:flex;justify-content:center;flex-wrap:wrap;gap:6px 16px;margin:10px 0 0;padding:10px 0 0;border-top:1px dashed var(--line);font-size:13px;color:var(--muted)}
.sheet .legend span{display:inline-flex;align-items:center;gap:6px}
.sheet .legend .mk{width:13px;height:13px}
.sheet .legend .mk.m-ok{border-width:2px}
.sheet .legend .mk.m-no::before,.sheet .legend .mk.m-no::after{height:15px;width:2px;margin-left:-1px}
.report .tiers{display:grid;gap:12px;margin:22px 0 0}
.report .tier{display:grid;grid-template-columns:40px 1fr auto;gap:10px;align-items:center;font-size:14.5px}
.report .tier .tb{height:10px;border-radius:99px;background:var(--line);overflow:hidden}
.report .tier .tb i{display:block;height:100%;width:0;background:var(--text);border-radius:99px;transition:width .8s ease-out}
.report .tier span:last-child{color:var(--muted);font-variant-numeric:tabular-nums;min-width:92px;text-align:right}
.report .read{margin:22px 0 0;padding:16px;border-radius:16px;background:var(--canvas);border:1px solid var(--line)}
.report .read b{font-family:'MaruBuri',serif;font-weight:400;font-size:26px}
.report .read p{margin:4px 0 0;font-size:15px;color:var(--muted)}
.report .next{margin:16px 0 0;font-size:15.5px}
.report .acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:20px}
.report .acts button{font:inherit;font-weight:700;font-size:15.5px;border-radius:14px;padding:15px 12px;cursor:pointer;border:1px solid var(--text)}
.report .acts .share{background:var(--highlight);border-color:var(--highlight);color:#23211E}
.report .acts .again{background:none;color:var(--text)}
.report .done{min-height:1.4em;margin:8px 0 0;font-size:13.5px;color:var(--muted)}
.report details{margin-top:12px;font-size:15px}
.report details summary{cursor:pointer;font-weight:600}
.report details ul{list-style:none;margin:8px 0 0;padding:0}
.report details li{display:flex;gap:10px;padding:6px 0;border-bottom:1px solid var(--line)}
.report details li b{flex:0 0 auto}
.report details li span{color:var(--muted)}
.report .note{margin:16px 0 0;font-size:13px;color:var(--muted)}
@media (max-width:600px){.quiz{padding:26px 18px 20px;border-radius:22px;margin:0 -4px 8px}.cover h1{font-size:30px}.spec dd{font-size:25px}.report .big{font-size:50px}.sheet{padding:14px 8px 10px}}
@media (prefers-reduced-motion:reduce){.report .tier .tb i,.quiz .opt{transition:none}.opts.in .opt{animation:none}}
</style>'''

TEST_JS = r'''<script>
// 영단어 테스트: 결과는 이 브라우저 안에서만 계산하고 어디에도 보내거나 저장하지 않는다.
(() => {
  const $ = (s) => document.querySelector(s);
  const root = $('#quiz'); if (!root) return;
  const view = (id) => root.querySelectorAll('[data-view]').forEach((v) => v.hidden = v.dataset.view !== id);
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const fmt = (n) => n.toLocaleString('ko-KR');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const TIERS = [['elementary', '초등'], ['middle', '중학'], ['high', '고등']];
  const TNAME = Object.fromEntries(TIERS);
  const ORDER = ['elementary', 'elementary', 'middle', 'elementary', 'middle', 'middle', 'elementary', 'middle', 'high', 'middle',
    'elementary', 'high', 'middle', 'high', 'middle', 'elementary', 'high', 'high', 'middle', 'high'];
  const LIMIT = 4000, SHOW_AFTER = 700;
  let data = null, qs = [], i = 0, res = [], timer = 0, t0 = 0, raf = 0, locked = true, popIgnore = false;

  // 친구가 보낸 결과(?r=1240) — 0~3000만 믿는다.
  const r = parseInt(new URLSearchParams(location.search).get('r'), 10);
  if (r >= 0 && r <= 3000) { const f = $('#q-friend'); f.textContent = `친구는 약 ${fmt(r)}개였어요. 나는 몇 개일까요?`; f.hidden = false; }

  const load = () => data ? Promise.resolve(data) : fetch('/test/words.json?v=1').then((x) => { if (!x.ok) throw 0; return x.json(); }).then((d) => data = d);
  // 첫 화면이 뜬 뒤 미리 받아 둔다(누르자마자 시작).
  (window.requestIdleCallback || ((f) => setTimeout(f, 1200)))(() => load().catch(() => {}));

  const shuffle = (a) => { for (let k = a.length - 1; k > 0; k--) { const j = Math.floor(Math.random() * (k + 1)); [a[k], a[j]] = [a[j], a[k]]; } return a; };
  const pick = () => {
    const bags = {};
    for (const [t] of TIERS) bags[t] = shuffle(data.pool[t].slice()).slice(0, data.ask[t]);
    return ORDER.map((t) => { const [w, m, d] = bags[t].pop(); return { t, w, m, opts: shuffle([m, ...shuffle(d.slice()).slice(0, 3)]) }; });
  };

  // 집중 화면: 휴대폰 뒤로 가기는 테스트만 닫는다.
  const enter = () => { document.body.classList.add('testing'); try { history.pushState({ dq: 1 }, ''); } catch (e) {} };
  const leave = () => {
    document.body.classList.remove('testing');
    if (history.state && history.state.dq) { popIgnore = true; history.back(); }
  };
  const stop = () => { locked = true; clearTimeout(timer); cancelAnimationFrame(raf); };
  const top = () => root.scrollIntoView({ block: 'start' });
  addEventListener('popstate', () => {
    if (popIgnore) { popIgnore = false; top(); return; }
    if (document.body.classList.contains('testing')) { stop(); document.body.classList.remove('testing'); view('start'); $('#q-start-btn').disabled = false; top(); }
  });

  const start = () => {
    const btn = $('#q-start-btn'); btn.disabled = true; $('#q-start-err').hidden = true;
    load().then(() => {
      qs = pick(); i = 0; res = [];
      $('#q-dots').innerHTML = qs.map(() => '<li></li>').join('');
      view('q'); enter(); root.scrollTop = 0; root.focus({ preventScroll: true }); ask();
    }).catch(() => { $('#q-start-err').hidden = false; btn.disabled = false; });
  };

  const setRing = (left) => {
    $('#q-timer').style.transform = `scaleX(${left})`;
    $('#q-clock').classList.toggle('low', left > 0 && left <= 0.375);
  };

  const ask = () => {
    const q = qs[i]; locked = true;
    $('#q-n').textContent = i + 1;
    $('#q-lv').textContent = `${TNAME[q.t]} 단어`;
    [...$('#q-dots').children].forEach((d, k) => d.classList.toggle('now', k === i));
    $('#q-word').textContent = q.w;
    const h = $('#q-hint'); h.className = 'hint'; h.textContent = '뜻을 먼저 떠올려 보세요';
    const box = $('#q-opts'); box.innerHTML = ''; box.classList.remove('in'); box.classList.add('wait'); $('#q-skip').classList.add('wait');
    setRing(1);
    q.opts.forEach((m, k) => {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'opt'; b.dataset.m = m; b.tabIndex = -1;
      b.innerHTML = `<span class="k" aria-hidden="true">${k + 1}</span><span>${esc(m)}</span>`;
      b.addEventListener('click', () => answer(m, b)); box.appendChild(b);
    });
    clearTimeout(timer); cancelAnimationFrame(raf);
    timer = setTimeout(() => {
      locked = false;
      box.classList.remove('wait'); box.classList.add('in'); $('#q-skip').classList.remove('wait');
      box.querySelectorAll('.opt').forEach((b) => b.tabIndex = 0);
      h.textContent = matchMedia('(hover: hover)').matches ? '4초 안에 골라요 · 키보드 1~4' : '4초 안에 골라요';
      t0 = performance.now();
      const tick = (now) => { const left = Math.max(0, 1 - (now - t0) / LIMIT); setRing(left); if (left > 0 && !locked) raf = requestAnimationFrame(tick); };
      raf = requestAnimationFrame(tick);
      timer = setTimeout(() => answer(null, null, true), LIMIT);
    }, SHOW_AFTER);
  };

  const answer = (m, btn, timeout = false) => {
    if (locked) return; stop();
    const q = qs[i], ok = m === q.m, skip = m === null;
    res.push({ t: q.t, w: q.w, m: q.m, ok, skip });
    const dot = $('#q-dots').children[i]; dot.classList.remove('now'); dot.classList.add(ok ? 'ok' : skip ? 'sk' : 'no');
    for (const b of $('#q-opts').children) {
      b.disabled = true;
      if (b.dataset.m === q.m) { b.classList.add('ok'); b.querySelector('.k').textContent = '✓'; }
      else if (b === btn) { b.classList.add('no'); b.querySelector('.k').textContent = '✕'; }
      else b.classList.add('dim');
    }
    const h = $('#q-hint');
    h.className = 'hint ' + (ok ? 'ok' : 'no');
    h.textContent = ok ? '맞았어요' : timeout ? '시간이 지났어요' : skip ? '괜찮아요, 다음 단어' : '아쉬워요';
    setTimeout(() => { i++; if (i < qs.length) ask(); else finish(); }, ok ? 420 : 1000);
  };

  const finish = () => {
    const p = {}; let est = 0;
    for (const [t] of TIERS) {
      const a = res.filter((x) => x.t === t), R = a.filter((x) => x.ok).length, W = a.filter((x) => !x.ok && !x.skip).length;
      p[t] = Math.max(0, Math.min(1, (R - W / 3) / a.length));
      est += data.N[t] * p[t];
    }
    est = Math.round(est / 10) * 10;
    const c = data.book.count, tot = c.elementary + c.middle + c.high;
    const read = Math.round(100 * (c.elementary * p.elementary + c.middle * p.middle + c.high * p.high) / tot);
    view('r'); leave(); top();
    $('#r-date').textContent = new Date().toLocaleDateString('ko-KR');
    const big = $('#r-big');
    if (reduce) big.textContent = fmt(est); else {
      const s = performance.now(); const run = (now) => { const k = Math.min(1, (now - s) / 900); big.textContent = fmt(Math.round(est * (1 - Math.pow(1 - k, 3)) / 10) * 10); if (k < 1) requestAnimationFrame(run); }; requestAnimationFrame(run);
    }
    const where = p.elementary < 0.8 ? ['초등 단어 채우는 중', '초등 단어부터 채우면 좋아요.', 'elem', '초등 기본 어휘']
      : p.middle < 0.7 ? ['중학 단어 쌓는 중', '다음은 중학 단어(**) 차례예요.', 'middle', '중학 기본 어휘']
      : p.high < 0.6 ? ['고등 단어 넓히는 중', '고등 단어로 넓혀 갈 때예요.', 'high', '고등 기본 어휘']
      : ['기본 어휘 거의 다 앎', '남은 고등 단어만 채우면 돼요.', 'high', '고등 기본 어휘'];
    $('#r-stage').textContent = where[0];
    const nOk = res.filter((x) => x.ok).length, nNo = res.filter((x) => !x.ok && !x.skip).length, nSkip = res.length - nOk - nNo;
    $('#r-score').textContent = `${res.length}문제 중 ${nOk}개 맞힘`;
    $('#r-sheet').innerHTML = res.map((x, k) => `<li title="${esc(x.w)}"><span class="mk ${x.ok ? 'm-ok' : x.skip ? 'm-skip' : 'm-no'}"></span>${k + 1}</li>`).join('');
    $('#r-legend').innerHTML = `<span><i class="mk m-ok"></i>맞힘 ${nOk}</span><span><i class="mk m-no"></i>틀림 ${nNo}</span><span><i class="mk m-skip"></i>모름 · 시간 초과 ${nSkip}</span>`;
    $('#r-tiers').innerHTML = TIERS.map(([t, n]) => `<div class="tier"><span>${n}</span><span class="tb"><i data-w="${Math.round(p[t] * 100)}"></i></span><span>${fmt(Math.round(data.N[t] * p[t] / 10) * 10)} / ${fmt(data.N[t])}</span></div>`).join('');
    requestAnimationFrame(() => requestAnimationFrame(() => root.querySelectorAll('.tier .tb i').forEach((x) => x.style.width = x.dataset.w + '%')));
    $('#r-read').textContent = `${read}%`;
    $('#r-book').textContent = `셜록 홈스 「${data.book.title}」에 나오는 기본 어휘 중 이만큼을 알 것 같아요.`;
    $('#r-next').innerHTML = `${where[1]} <a href="/basic-words/#${where[2]}">${where[3]} 목록 보기</a>`;
    const miss = res.filter((x) => !x.ok);
    $('#r-miss').hidden = !miss.length;
    $('#r-miss-n').textContent = miss.length;
    $('#r-miss-list').innerHTML = miss.map((x) => `<li><b lang="en">${esc(x.w)}</b><span>${esc(x.m)}</span></li>`).join('');
    root.dataset.est = est; root.dataset.read = read;
    $('#r-done').textContent = '';
  };

  const share = async () => {
    const est = +root.dataset.est, read = +root.dataset.read;
    const url = `https://dansuki.com/test/?r=${est}`;
    const text = `영단어 테스트 해 봤는데 기본 영단어 3,000개 중 약 ${fmt(est)}개 안대. 셜록 홈스도 ${read}% 읽을 수 있대! 너는 몇 개야?`;
    if (navigator.share) { try { await navigator.share({ title: '단숙이 영단어 테스트', text, url }); return; } catch (e) { if (e && e.name === 'AbortError') return; } }
    try { await navigator.clipboard.writeText(`${text} ${url}`); $('#r-done').textContent = '결과와 링크를 복사했어요. 친구에게 붙여 넣어 보내 보세요.'; }
    catch (e) { $('#r-done').textContent = `이 주소를 보내 주세요: ${url}`; }
  };

  const quit = () => { stop(); view('start'); $('#q-start-btn').disabled = false; leave(); top(); };
  $('#q-start-btn').addEventListener('click', start);
  $('#q-exit').addEventListener('click', quit);
  $('#q-skip').addEventListener('click', () => answer(null, null));
  $('#r-share').addEventListener('click', share);
  $('#r-again').addEventListener('click', () => { view('start'); $('#q-start-btn').disabled = false; top(); });
  addEventListener('keydown', (e) => {
    if (!document.body.classList.contains('testing')) return;
    if (e.key === 'Escape') { e.preventDefault(); quit(); return; }
    if (locked) return;
    const box = $('#q-opts'), k = parseInt(e.key, 10);
    if (k >= 1 && k <= 4 && box.children[k - 1]) { e.preventDefault(); box.children[k - 1].click(); }
    else if (e.key === '0') { e.preventDefault(); answer(null, null); }
  });
  view('start');
})();
</script>'''


def build_test():
    sizes, cnt = build_test_data()
    path = 'test/'
    title = '영단어 테스트 · 기본 영단어 3,000개 중 나는 몇 개 알까? | 단숙이'
    desc = ('20문제 · 2분이면 교육부 기본 어휘 3,000개 중 아는 단어 수를 어림해요. 4초 안에 뜻을 떠올리는 방식이고, '
            '셜록 홈스 이야기를 몇 % 읽을 수 있는지도 알려 줘요. 가입 없이 무료.')
    headline = '기본 영단어 3,000개 중, 나는 몇 개 알까?'
    data = ld(path=path, title=title, desc=desc, headline=headline, crumb_name='영단어 테스트', og='test-og.png',
              keywords=['영단어 테스트', '영어 어휘력 테스트', '중학생 영단어 테스트', '기본 어휘 테스트', '영단어 레벨 테스트', '영어 단어 실력'])
    play = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8 5.6v12.8a1 1 0 0 0 1.5.86l10.2-6.4a1 1 0 0 0 0-1.72L9.5 4.74A1 1 0 0 0 8 5.6z"/></svg>'
    close = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>'
    quiz = f'''<section class="quiz" id="quiz" aria-label="영단어 테스트" tabindex="-1" data-own-style>
<div data-view="start" class="cover"><p class="friend" id="q-friend" hidden></p>
<span class="qtag">영단어 레벨 테스트</span>
<h1>기본 영단어 3,000개 중, <br><span class="mark">나는 몇 개 알까?</span></h1>
<div class="mascot"><img src="/icon.png" alt="단숙이" width="60" height="60"><p class="bubble">보자마자 떠오르는 단어만 세요. 모르면 찍지 말고 '모르겠어요'!</p></div>
<dl class="spec"><div><dt>문항</dt><dd>20<small>문제</small></dd></div><div><dt>걸리는 시간</dt><dd>2<small>분</small></dd></div><div><dt>문항당</dt><dd>4<small>초</small></dd></div></dl>
<div class="rules"><h2>푸는 방법</h2><ol><li><b>1</b><span><strong>영어 단어가 먼저 떠요.</strong> 보기가 나오기 전에 뜻을 떠올려 보세요.</span></li><li><b>2</b><span><strong>보기 4개 중 4초 안에</strong> 골라요. 시간이 지나면 다음 문제로 넘어가요.</span></li><li><b>3</b><span><strong>찍어서 맞힌 몫은 빼고</strong> 어림해요. 모르면 '모르겠어요'가 더 정확해요.</span></li></ol></div>
<p class="err" id="q-start-err" hidden>단어를 불러오지 못했어요. 인터넷 연결을 확인하고 다시 눌러 주세요.</p>
<button class="go" type="button" id="q-start-btn">{play}테스트 시작하기</button>
<p class="fine byline">초등 6 · 중학 8 · 고등 6문제 <span aria-hidden="true">·</span> 가입 없음 · 무료 <span aria-hidden="true">·</span> <time datetime="{DAY}">2026년 11월 3일</time></p></div>
<div data-view="q" class="solve" hidden><div class="qhead"><button class="x" type="button" id="q-exit" aria-label="테스트 그만하기">{close}</button><ol class="dots" id="q-dots" aria-hidden="true"></ol><span class="qn"><b id="q-n">1</b> / 20</span></div>
<div class="qcard"><div class="qtop"><span class="lv" id="q-lv">초등 단어</span><img src="/icon.png" alt="" width="52" height="52"><p class="word" id="q-word" lang="en" aria-live="polite"></p><p class="hint" id="q-hint" aria-live="polite"></p></div>
<div class="opts" id="q-opts"></div><div class="qtimer" id="q-clock" aria-hidden="true"><i id="q-timer"></i></div><button class="skip" type="button" id="q-skip">모르겠어요</button></div></div>
<div data-view="r" class="report" hidden><div class="rtop"><span class="qtag">결과표</span><time id="r-date"></time></div>
<p class="of">기본 영단어 3,000개 중 아는 단어</p><p class="big" aria-live="polite">약 <span id="r-big">0</span><small>개</small></p>
<p class="stage-l">지금 단계 <b id="r-stage"></b></p>
<div class="sheet"><div class="sh-h"><b>채점</b><span id="r-score"></span></div><ol id="r-sheet"></ol><p class="legend" id="r-legend"></p></div>
<div class="tiers" id="r-tiers"></div>
<div class="read"><b id="r-read">0%</b><p id="r-book"></p></div>
<p class="next" id="r-next"></p>
<div class="acts"><button class="share" type="button" id="r-share">친구에게 자랑하기</button><button class="again" type="button" id="r-again">다시 하기</button></div><p class="done" id="r-done" aria-live="polite"></p>
<details id="r-miss"><summary>몰랐던 단어 <span id="r-miss-n">0</span>개 다시 보기</summary><ul id="r-miss-list"></ul></details>
<p class="note">20문제로 어림한 값이라, 다시 하면 조금 달라질 수 있어요. 결과는 이 화면에서만 계산하고 어디에도 저장하거나 보내지 않아요.</p></div>
<noscript><p>테스트는 자바스크립트를 켜야 할 수 있어요.</p></noscript>
</section>'''
    tot = sum(cnt.values())
    body = f'''<main class="research-main"><article class="wrap narrow research-article" id="post">
<p class="crumb"><a href="/">단숙이</a> › <a href="/method/">공부 방법</a> › 영단어 테스트</p>
{quiz}
<h2 id="how">이 테스트는 <br>이렇게 어림해요</h2>
<p>문제는 교육부 기본 어휘(2022 개정) 3,000개에서 나와요. 초등 권장 단어(*) {N["elementary"]:,}개, 중학교 · 고1 공통과목 권장 단어(**) {N["middle"]:,}개, 나머지 {N["high"]:,}개에서 각각 6 · 8 · 6개를 무작위로 골라요. 학교급마다 맞힌 비율을 그 학교급 단어 수에 곱해 더한 값이 결과예요.</p>
<div class="study"><h3>정직하게 세려고 한 것</h3><ul><li><strong>4초 안에 골라야 맞힘</strong><br>한참 생각해야 떠오르는 단어는 글을 읽을 때 멈추게 해요. 그래서 단숙이 앱처럼 4초를 기준으로 했어요.</li><li><strong>찍어서 맞힌 몫은 빼기</strong><br>보기가 4개라 찍어도 4번에 1번은 맞아요. 틀린 답 3개마다 맞힌 1개를 빼서, 찍은 몫이 점수에 들어가지 않게 했어요. '모르겠어요'와 시간 초과는 빼지 않아요.</li><li><strong>보자마자 떠올리기</strong><br>보기는 0.7초 뒤에 나와요. 그 사이 뜻을 먼저 떠올려 보세요.</li></ul></div>
<p>셜록 홈스 「빨간 머리 연맹」의 %는, 이 이야기에 기본 어휘가 나오는 {tot:,}번(초등 {cnt["elementary"]:,} · 중학 {cnt["middle"]:,} · 고등 {cnt["high"]:,}) 중 아는 단어일 것 같은 비율이에요. 단숙이 앱의 이야기 탭이 '외운 단어로 글의 몇 %가 읽히는지' 보여 주는 것과 같은 셈법이에요.</p>
<p>20문제로 어림한 값이라 오차가 있어요. 정확한 실력 검사가 아니라, 어디서부터 공부할지 정하는 출발점으로 봐 주세요.</p>
<h2 id="next">결과를 보고 <br>어디서부터 할까요?</h2>
<p>초등 단어를 80% 넘게 알지 못했다면 <a href="/basic-words/#elem">초등 기본 어휘</a>부터 채우는 게 결국 더 빨라요. 초등 단어는 알고 중학 단어가 70%에 못 미치면 <a href="/basic-words/#middle">중학 기본 어휘</a>가 다음 차례예요. 하루에 몇 개씩, 어떤 순서로 할지는 <a href="/middle-school-words/">중학 영단어 공부법</a>에 정리해 뒀어요.</p>
{app_box("모르는 단어부터, <br>하루 20개씩.", ["단숙이는 이 테스트와 같은 방식(4초 안에 떠올리기)으로 기본 어휘를 외우는 무료 영단어 · 숙어 앱이에요. 외운 단어는 2일 · 7일 · 21일 뒤에 다시 물어봐요.", "외운 단어는 셜록 홈스 같은 이야기에서 다시 만나고, 외울수록 읽히는 %가 올라가요. 광고와 가입 없이 바로 시작할 수 있어요."])}
<section class="article-refs" aria-label="출처"><h2>출처</h2><p>문제 단어: 교육부 고시 제2022-33호 [별책 14] 영어과 교육과정 [별표 3] 기본 어휘 목록. 뜻과 보기는 단숙이 앱의 것을 썼어요. 교육부, 한국교육과정평가원과는 관계없이 개인이 만든 테스트예요.</p></section>
</article></main>'''
    page = head(path=path, title=title, desc=desc, og_alt='기본 영단어 3,000개 중 나는 몇 개 알까? 영단어 테스트', ld=data, og='test-og.png',
                extra_css=TEST_CSS) + nav.replace(f'<a href="/{path}">', f'<a href="/{path}" aria-current="page">') + body + tail.replace('</body>', TEST_JS + '</body>')
    (DOCS / path / 'index.html').write_text(page, encoding='utf-8')
    return sizes


test_sizes = build_test()
print('test pool', test_sizes)
# ── /words/<단어>/ 단어별 페이지(2026-11-03 SEO 자동화) ─────────────────
# 예문은 단숙이가 직접 쓴 것만: 이야기 19편 속 문장(덩어리 해석을 이어 붙인 한국어) + 자체 작성 예문
# (2015 초등 권장 800개 · 2022 신규 단어). 다른 예문은 바깥 자료라 싣지 않는다(이용 허락 미확인, 2026-11-03 사용자 결정).
import re as _re

TIER_KO = {'elementary': ('초등', '*', 'elem'), 'middle': ('중학', '**', 'middle'), 'high': ('고등', '', 'high')}
WORD_LABELS = '뜻 발음 듣기 이야기 속 문장 예문 헷갈리는 단어 비슷한 말 반대말 같은 칸 단어 같은 학교급 단어 기본 어휘 목록으로'



def story_examples():
    """칸 단어 → [(문장 en 조각들, 한국어, 책 제목, 장 번호)] 후보."""
    man = json.loads((DOCS / 'stories/manifest.json').read_text(encoding='utf-8'))
    byid = {w['id']: w for w in words}
    cell_word = {}
    for w in words:
        if w.get('cell2022'):
            cell_word[w['id']] = w['word']
        elif w.get('grade2022'):
            c = cell_of.get(fam_key(w))
            if c:
                cell_word[w['id']] = c
    out = {}
    for b in man['books']:
        book = json.loads((DOCS / 'stories' / b['url']).read_text(encoding='utf-8'))
        btitle = book['titleKo']
        for ch in book['chapters']:
            for para in ch['paragraphs']:
                toks = para['en']
                text = ''.join(t[0] for t in toks)
                # 덩어리(영어 · 한국어)의 자리
                spans, pos = [], 0
                for c in para.get('chunks', []):
                    i = text.find(c[0], pos)
                    if i < 0:
                        continue
                    spans.append((i, i + len(c[0]), c[1])); pos = i + len(c[0])
                # 문장 경계
                ends = [m.end() for m in _re.finditer(r'(?<!\bMr)(?<!\bMrs)(?<!\bMs)(?<!\bDr)(?<!\bSt)(?<!\bMt)[.!?]["”’]?(?=\s|$)', text)] or [len(text)]
                if ends[-1] < len(text.rstrip()):
                    ends.append(len(text))
                starts = [0] + ends[:-1]
                off = 0
                for t in toks:
                    s0, e0 = off, off + len(t[0]); off = e0
                    cw = cell_word.get(t[1]) if t[1] else None
                    if not cw:
                        continue
                    k = next((j for j, e in enumerate(ends) if s0 < e), len(ends) - 1)
                    ss, se = starts[k], ends[k]
                    sent = text[ss:se].strip()
                    if not (30 <= len(sent) <= 170):
                        continue
                    ko = ' '.join(c[2] for c in spans if c[0] < se and c[1] > ss)
                    if not ko:
                        continue
                    lead = len(text[ss:se]) - len(text[ss:se].lstrip())
                    a, z = s0 - ss - lead, e0 - ss - lead
                    out.setdefault(cw, []).append((sent[:a], sent[a:z], sent[z:], ko, btitle, ch['n'], bool(byid[t[1]].get('cell2022'))))
    return out


WORDS_PAGE_CSS = '<link rel="stylesheet" href="/words/w.css?v=e5dd241b">'
W_CSS = '''/* 단어별 페이지(/words/…) 공통 — tool/build_word_pages.py가 만든다 */
.entry .def{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 14px;margin:6px 0 4px}
.entry .def .w{font-family:'MaruBuri',serif;font-size:40px;line-height:1.2}
.entry .def .m{font-size:22px;font-weight:700;line-height:1.45}
.entry .say{font:inherit;font-size:14px;font-weight:600;border:1px solid var(--line);background:var(--surface);color:var(--text);border-radius:999px;padding:5px 12px;cursor:pointer}
.entry .say:focus-visible{outline:3px solid var(--highlight);outline-offset:2px}
.entry .tags{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 0}
.entry .tags span,.entry .tags a{font-size:13px;padding:3px 10px;border-radius:999px;background:var(--surface);border:1px solid var(--line);text-decoration:none;color:var(--muted)}
.entry .senses{margin:12px 0 0;padding-left:20px}
.entry .ex{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:12px}
.entry .ex li p{margin:0}
.entry .ex li{padding:14px 16px;border-radius:16px;background:var(--surface);border:1px solid var(--line)}
.entry .ex .en{font-size:17px;line-height:1.6}
.entry .ex mark{background:linear-gradient(transparent 55%,var(--mark) 55%);color:inherit;padding:0 1px}
.entry .ex .ko{margin-top:4px;color:var(--muted);font-size:15px}
.entry .ex .src{margin-top:6px;color:var(--faint);font-size:12.5px}
.entry .rel{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:0}
.entry .rel li{display:flex;gap:12px;align-items:baseline;padding:8px 0;border-bottom:1px solid var(--line);font-size:15.5px}
.entry .rel li b{flex:0 0 auto;font-weight:700}
.entry .rel li span{color:var(--muted)}
.entry .near{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.entry .near a{padding:6px 12px;border-radius:12px;background:var(--surface);border:1px solid var(--line);text-decoration:none;font-weight:600}
.entry .near a small{color:var(--muted);font-weight:400;margin-left:4px}
@media (max-width:600px){.entry .def .m{font-size:19px}}
'''
SAY_JS = '''<script>
// 발음 듣기: 브라우저에 들어 있는 영어 목소리로 읽는다(서버로 보내지 않음).
(() => { const b = document.querySelector('.say'); if (!b) return;
  if (!('speechSynthesis' in window)) { b.hidden = true; return; }
  b.addEventListener('click', () => { const u = new SpeechSynthesisUtterance(b.dataset.w); u.lang = 'en-US'; u.rate = .9; speechSynthesis.cancel(); speechSynthesis.speak(u); });
})();
</script>'''


def link(x, index):
    return f'<a href="/words/{wslug(x)}/">{e(x)}</a>' if x in index else e(x)


def build_entries():
    ex = story_examples()
    alpha = {k: sorted(by[k], key=lambda w: w['word'].lower()) for k, _, _ in LEVELS}
    index = {w['word']: w for w in cur}
    (DOCS / 'words').mkdir(exist_ok=True)
    (DOCS / 'words/w.css').write_text(W_CSS, encoding='utf-8')
    urls, thin = [], 0
    keep = set()
    for k, _, _ in LEVELS:
        lst = alpha[k]
        for i, w in enumerate(lst):
            word, sl = w['word'], wslug(w['word'])
            keep.add(sl)
            tko, mark_, anchor = TIER_KO[k]
            own = w.get('grade2015') == 'elementary' or not w.get('grade2015')
            # 이야기 문장: 짧은 것 위주로, 책이 겹치지 않게 최대 3개
            cands = sorted(ex.get(word, []), key=lambda c: (not c[6], abs(len(c[0] + c[1] + c[2]) - 80)))
            picked, books_seen = [], set()
            for c in cands:
                if c[4] in books_seen:
                    continue
                picked.append(c); books_seen.add(c[4])
                if len(picked) == 3:
                    break
            own_ex = [(w['example'], w['exampleKo'])] if own and w.get('example') else []
            if own and w.get('senses'):
                own_ex = [(s['example'], s['exampleKo']) for s in w['senses'] if s.get('example')][:3] or own_ex
            noindex = not picked and not own_ex
            thin += noindex
            path = f'words/{sl}/'
            url = f'https://dansuki.com/{path}'
            title = f'{word} 뜻 · 예문 | {tko} 기본 어휘 | 단숙이'
            desc = (f"{word} 뜻: {w['meaning']}. 교육부 기본 어휘(2022 개정) {tko} 단어예요. "
                    + (f'셜록 홈스 같은 이야기 속 문장 {len(picked)}개와 ' if picked else '')
                    + '헷갈리는 단어, 발음까지 한 번에 봐요.')
            data = {'@context': 'https://schema.org', '@graph': [
                {'@type': 'WebPage', '@id': url + '#webpage', 'url': url, 'name': title, 'description': desc, 'inLanguage': 'ko-KR',
                 'isPartOf': {'@id': 'https://dansuki.com/#website'}, 'mainEntity': {'@id': url + '#term'}, 'breadcrumb': {'@id': url + '#crumb'}},
                {'@type': 'DefinedTerm', '@id': url + '#term', 'name': word, 'description': w['meaning'], 'inLanguage': 'en', 'url': url,
                 'inDefinedTermSet': {'@type': 'DefinedTermSet', '@id': 'https://dansuki.com/basic-words/#set', 'name': '교육부 기본 어휘(2022 개정)', 'url': 'https://dansuki.com/basic-words/'}},
                {'@type': 'BreadcrumbList', '@id': url + '#crumb', 'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': '단숙이', 'item': 'https://dansuki.com/'},
                    {'@type': 'ListItem', 'position': 2, 'name': '기본 어휘 3000 목록', 'item': 'https://dansuki.com/basic-words/'},
                    {'@type': 'ListItem', 'position': 3, 'name': word, 'item': url}]}]}
            hd = head(path=path, title=title, desc=desc, og_alt=f'{word} 뜻', ld=data, og='basic-words-og.png', extra_css=WORDS_PAGE_CSS)
            hd = hd.replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">')
            if noindex:
                hd = hd.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex, follow">')
            senses = ''
            if len(w.get('senses') or []) > 1:
                senses = '<ol class="senses">' + ''.join(f"<li>{e(s['meaning'])}</li>" for s in w['senses']) + '</ol>'
            tags = [f'<a href="/basic-words/#{anchor}">{tko} 기본 어휘{(" " + mark_) if mark_ else ""}</a>']
            tags.append('<span>2015 · 2022 개정 모두</span>' if w.get('grade2015') else '<span>2022 개정에서 새로 들어옴</span>')
            if DERIV.get(word):
                tags.append(f'<span>같은 칸: {e(", ".join(sorted(DERIV[word])))}</span>')
            ex_html = ''
            if picked:
                ex_html = ('<h2>이야기 속 문장</h2><p class="muted">단숙이 이야기 탭에 나오는 문장이에요.</p><ul class="ex">'
                           + ''.join(f'<li><p class="en" lang="en">{e(a)}<mark>{e(b_)}</mark>{e(z)}</p><p class="ko">{e(ko)}</p><p class="src">「{e(bt)}」 {n}장</p></li>'
                                     for a, b_, z, ko, bt, n, _d in picked) + '</ul>')
            if own_ex:
                ex_html += ('<h2>예문</h2><ul class="ex">' + ''.join(
                    f'<li><p class="en" lang="en">{e(x)}</p><p class="ko">{e(y)}</p></li>' for x, y in own_ex) + '</ul>')
            rel = ''
            conf = [c for c in (w.get('confusables') or []) if c.get('word')]
            if conf:
                rel += '<h2>헷갈리는 단어</h2><ul class="rel">' + ''.join(
                    '<li><b lang="en">' + link(c['word'], index) + '</b><span>' + e(c['meaning']) + '</span></li>'
                    for c in conf[:4]) + '</ul>'
            for lab, key in (('비슷한 말', 'synonyms'), ('반대말', 'antonyms')):
                xs = w.get(key) or []
                if xs:
                    rel += f'<h2>{lab}</h2><div class="near">' + ''.join(
                        (f'<a href="/words/{wslug(x)}/" lang="en">{e(x)}<small>{e(index[x]["meaning"][:14])}</small></a>' if x in index else f'<span lang="en">{e(x)}</span>')
                        for x in xs[:6]) + '</div>'
            nb = [lst[j] for j in range(max(0, i - 3), min(len(lst), i + 4)) if j != i]
            near = (f'<h2>같은 학교급 단어</h2><div class="near">' + ''.join(
                f'<a href="/words/{wslug(x["word"])}/" lang="en">{e(x["word"])}<small>{e(x["meaning"][:12])}</small></a>' for x in nb)
                + f'</div><p style="margin-top:14px"><a href="/basic-words/#{anchor}">{tko} 기본 어휘 {N[k]:,}개 목록으로</a></p>')
            body = f'''<main class="research-main"><article class="wrap narrow research-article entry" id="post">
<header class="article-head"><p class="crumb"><a href="/">단숙이</a> › <a href="/basic-words/">기본 어휘 3000 목록</a> › <a href="/basic-words/#{anchor}">{tko}</a></p><h1 lang="en">{e(word)} <span lang="ko">뜻</span></h1>
<div class="def"><span class="m">{e(w['meaning'])}</span><button class="say" type="button" data-w="{e(word)}" aria-label="{e(word)} 발음 듣기">▶ 발음</button></div>
{senses}<div class="tags">{''.join(tags)}</div></header>
{ex_html}{rel}{near}
{app_box(f"{e(word)}, 4초 안에 <br>떠올릴 수 있나요?", [f"단숙이는 {e(word)} 같은 교육부 기본 어휘를 4초 안에 떠올리는 방식으로 외우는 무료 영단어 · 숙어 앱이에요. 외운 단어는 2일 · 7일 · 21일 뒤에 다시 물어보고, 이야기 속에서 형광펜으로 다시 만나요.", '지금 몇 개 아는지 궁금하면 <a href="/test/">2분 영단어 테스트</a>부터 해 보세요.'])}
</article></main>'''
            page = hd + nav + body + tail.replace('</body>', SAY_JS + '</body>')
            (DOCS / path).mkdir(parents=True, exist_ok=True)
            (DOCS / path / 'index.html').write_text(page, encoding='utf-8')
            if not noindex:
                urls.append(url)
    # 예전에 만들었다가 목록에서 빠진 단어 페이지는 지운다
    import shutil
    for d in (DOCS / 'words').iterdir():
        if d.is_dir() and d.name not in keep:
            shutil.rmtree(d)
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f'  <url><loc>{u}</loc><lastmod>{DAY}</lastmod></url>' for u in urls]
    sm.append('</urlset>')
    (DOCS / 'sitemap-words.xml').write_text('\n'.join(sm) + '\n', encoding='utf-8')
    return len(keep), len(urls), thin


entry_stats = build_entries()
print('word pages', entry_stats)
print('ok', N, len(only2015), len(new2022))
