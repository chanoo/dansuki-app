#!/bin/bash
# 마루부리(제목 글꼴)를 사이트에 쓰는 글자만 담아 docs/fonts/MaruBuri-sub.woff2로 만든다.
# 원본 431KB를 통째로 받던 것을 줄여 휴대폰 첫 화면을 빠르게(2026-10-16 SEO 점검).
# 필요: fonttools + brotli (pip install fonttools brotli). 글자를 새로 쓰면 다시 돌린다.
set -e
cd "$(dirname "$0")/.."
SRC=${SRC:-/tmp/MaruBuri-Regular.woff2}
[ -f "$SRC" ] || curl -s -o "$SRC" https://hangeul.pstatic.net/hangeul_static/webfont/MaruBuri/MaruBuri-Regular.woff2
PY=${PY:-python3}
$PY - <<'PYEOF' > /tmp/dansuki-chars.txt
import html, re
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
docs = Path('docs')
paths = [docs / '404.html']
for node in ET.parse(docs / 'sitemap.xml').iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
    path = docs / urlsplit(node.text).path.lstrip('/')
    paths.append(path / 'index.html' if path.is_dir() else path)
t = ''.join(p.read_text(encoding='utf-8') for p in paths)
t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
# 한글 음절 전부 + 기본 라틴 · 숫자 · 기호
chars = set(t) | set(chr(c) for c in range(0x20, 0x7f)) | set('·→←…“”‘’—–')
print(''.join(sorted(c for c in chars if c.isprintable())))
PYEOF
${PYFTSUBSET:-pyftsubset} "$SRC" --text-file=/tmp/dansuki-chars.txt --flavor=woff2 \
  --layout-features='*' --output-file=docs/fonts/MaruBuri-sub.woff2
ls -la docs/fonts/MaruBuri-sub.woff2
