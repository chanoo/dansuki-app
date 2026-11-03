"""공부 글 디자인 검수(2026-11-03 콘텐츠 자동화). 실제 브라우저(Chromium)로 글을 열어 본다.
- 휴대폰 390px · PC 1280px × 라이트 · 다크 = 4가지로 연다
- 가로로 넘치는 요소, 깨진 이미지, 콘솔 오류, 12px보다 작은 글씨, 대비가 낮은 글자(WCAG 4.5:1, 큰 글씨 3:1)
- 제목 글꼴(마루부리 부분 글꼴)에 없는 글자 — 있으면 그 글자만 다른 글꼴로 섞여 보인다
- 글자 크기 · 줄 간격 · 글꼴이 기존 글(middle-school-words)과 같은지 — 글마다 제멋대로 스타일을 넣지 않게
- 화면 캡처를 남긴다(사람 · Claude가 눈으로 보는 용도): <shots>/<slug>-{mobile,desktop}-{light,dark}.png
필요: pip install playwright fonttools brotli && python -m playwright install --with-deps chromium
실행: python tool/check_design.py <slug> [--shots 폴더]   → 문제가 있으면 1로 끝난다
"""
import argparse
import functools
import http.server
import re
import sys
import threading
from pathlib import Path

from fontTools.ttLib import TTFont
from playwright.sync_api import sync_playwright

R = Path(__file__).resolve().parent.parent
D = R / 'docs'
REF = 'middle-school-words'
VIEWS = [('mobile', 390, 844), ('desktop', 1280, 900)]
SCHEMES = ['light', 'dark']

PROBE = r'''() => {
  const vw = innerWidth, out = {overflow: [], images: [], tiny: [], contrast: [], serif: ''};
  const scrollable = (el) => { for (let p = el.parentElement; p; p = p.parentElement) { const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') return true; } return false; };
  const art = document.querySelector('article') || document.body;
  const fixedish = (el) => { for (let p = el; p; p = p.parentElement) { const s = getComputedStyle(p).position; if (s === 'fixed' || s === 'sticky') return true; } return false; };
  const name = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '');
  out.pageOverflow = document.documentElement.scrollWidth - vw;
  for (const el of art.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width && r.right > vw + 1 && !scrollable(el) && !fixedish(el)) out.overflow.push(name(el) + ' → ' + Math.round(r.right - vw) + 'px');
  }
  for (const img of document.images) if (!(img.complete && img.naturalWidth > 0) && img.loading !== 'lazy') out.images.push(img.getAttribute('src'));
  // 색 대비: 글자가 직접 들어 있는 요소만
  const rgb = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const v = m[1].split(',').map(Number); return {r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1}; };
  const lum = (c) => { const f = (x) => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const bgOf = (el) => { for (let p = el; p; p = p.parentElement) { const s = getComputedStyle(p); if (s.backgroundImage !== 'none' && s.backgroundImage.includes('gradient') && p.tagName !== 'BODY') return null; const c = rgb(s.backgroundColor); if (c && c.a > 0.9) return c; } return rgb(getComputedStyle(document.body).backgroundColor) || {r: 255, g: 255, b: 255}; };
  for (const el of art.querySelectorAll('p,li,h1,h2,h3,h4,a,span,b,strong,td,th,small,time,figcaption,summary')) {
    // 글자(한글 · 영문 · 숫자)가 직접 든 요소만 — 빈칸 · ★ 같은 장식 기호는 빼고
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && /[\p{L}\p{N}]/u.test(n.textContent));
    if (!own || !el.offsetParent || el.closest('.katex')) continue;  // 수식 아래첨자는 원래 작다
    const s = getComputedStyle(el), fs = parseFloat(s.fontSize);
    if (fs < 12) out.tiny.push(name(el) + ' ' + fs + 'px: ' + el.textContent.trim().slice(0, 20));
    const fg = rgb(s.color), bg = bgOf(el);
    if (!fg || !bg) continue;
    const L1 = lum(fg), L2 = lum(bg), ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    const big = fs >= 24 || (fs >= 18.66 && parseInt(s.fontWeight) >= 700);
    if (ratio < (big ? 3 : 4.5)) out.contrast.push(name(el) + ' ' + ratio.toFixed(2) + ':1 "' + el.textContent.trim().slice(0, 18) + '"');
  }
  // 제목 글꼴(마루부리)로 그려지는 글자 모으기
  for (const el of document.querySelectorAll('body *')) {
    if (!el.offsetParent) continue;
    if (!/MaruBuri/.test(getComputedStyle(el).fontFamily)) continue;
    for (const n of el.childNodes) if (n.nodeType === 3) out.serif += n.textContent;
  }
  const pick = (sel) => { const el = art.querySelector(sel); if (!el) return null; const s = getComputedStyle(el); return [s.fontFamily.split(',')[0], s.fontSize, s.lineHeight, s.fontWeight].join(' / '); };
  out.styles = {h1: pick('h1'), h2: pick(':scope > h2'), p: pick(':scope > p:not([class])'), li: pick('.study li')};
  return out;
}'''


def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(D))
    http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    ap.add_argument('--shots', default=str(R / '.design-shots'))
    a = ap.parse_args()
    slug = a.slug.strip('/').removeprefix('docs/').removesuffix('/index.html')
    shots = Path(a.shots); shots.mkdir(parents=True, exist_ok=True)
    cmap = set(TTFont(str(D / 'fonts/MaruBuri-sub.woff2')).getBestCmap())
    srv = serve()
    base = f'http://127.0.0.1:{srv.server_address[1]}'
    bad, seen_serif = [], ''
    with sync_playwright() as p:
        br = p.chromium.launch()
        ref_styles = {}
        for view, w, h in VIEWS:
            pg = br.new_page(viewport={'width': w, 'height': h}, color_scheme='light')
            pg.goto(f'{base}/{REF}/', wait_until='networkidle'); pg.evaluate('document.fonts.ready')
            ref_styles[view] = pg.evaluate(PROBE)['styles']
            pg.close()
        for view, w, h in VIEWS:
            for scheme in SCHEMES:
                tag = f'{view}-{scheme}'
                pg = br.new_page(viewport={'width': w, 'height': h}, color_scheme=scheme, device_scale_factor=2 if view == 'mobile' else 1)
                errs = []
                pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
                pg.on('pageerror', lambda e: errs.append(str(e)))
                resp = pg.goto(f'{base}/{slug}/', wait_until='networkidle')
                if not resp or resp.status != 200:
                    bad.append(f'{tag}: 페이지를 못 엶({resp.status if resp else "없음"})'); pg.close(); continue
                pg.evaluate('document.fonts.ready')
                r = pg.evaluate(PROBE)
                seen_serif += r['serif']
                if r['pageOverflow'] > 1:
                    bad.append(f'{tag}: 페이지가 가로로 {r["pageOverflow"]}px 넘침')
                for x in r['overflow'][:5]:
                    bad.append(f'{tag}: 화면 밖으로 넘치는 요소 {x}')
                for x in r['images']:
                    bad.append(f'{tag}: 깨진 이미지 {x}')
                for x in r['tiny'][:5]:
                    bad.append(f'{tag}: 너무 작은 글씨 {x}')
                for x in r['contrast'][:5]:
                    bad.append(f'{tag}: 대비 낮음 {x}')
                for x in errs[:3]:
                    if 'preload' not in x and 'WebGPU' not in x:
                        bad.append(f'{tag}: 콘솔 오류 {x[:120]}')
                if scheme == 'light':
                    for k, v in r['styles'].items():
                        if v and ref_styles[view].get(k) and v != ref_styles[view][k]:
                            bad.append(f'{tag}: {k} 스타일이 기존 글과 다름({v} ≠ {ref_styles[view][k]})')
                pg.screenshot(path=str(shots / f'{slug.replace("/", "-")}-{tag}.png'), full_page=True)
                pg.close()
        br.close()
    srv.shutdown()
    missing = sorted({c for c in seen_serif if not c.isspace() and ord(c) not in cmap})
    if missing:
        bad.append(f'제목 글꼴에 없는 글자 {len(missing)}개: {"".join(missing[:30])} → bash tool/subset_fonts.sh')
    print(f'{slug}: 디자인 검수 — 휴대폰 · PC × 라이트 · 다크, 캡처 {shots}/{slug.replace("/", "-")}-*.png')
    for b in bad:
        print('  ✗', b)
    if bad:
        sys.exit(1)
    print('  디자인 검수 통과')


if __name__ == '__main__':
    main()
