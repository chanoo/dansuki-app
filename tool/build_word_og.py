"""기본 어휘 목록 · 중학 영단어 공부법 공유 이미지(1200×630). build_research_og.py와 같은 모양(2026-11-03).
실행: uv run --with pillow python tool/build_word_og.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent.parent
PAGES = [
    ('basic-words-og.png', '단숙이 영단어 목록', '교육부 기본 어휘 3,000개,', '학교급별로 한눈에',
     '초등 800 · 중학 1,200 · 고등 1,000 · 뜻과 함께', '2022 개정 교육과정 기본 어휘 전체 목록'),
    ('middle-school-words-og.png', '단숙이 공부 이야기', '중학 영단어,', '하루 20개를 오래 남기는 법',
     '먼저 떠올리기 · 2일 · 7일 · 21일 뒤 다시 보기', '중학생 기본 어휘 2,000개를 외우는 순서'),
]


def font(name, size):
    return ImageFont.truetype(str(R / 'brand' / name), size)


serif = font('MaruBuri-Bold.ttf', 63)
sans = font('Pretendard-Regular.otf', 26)
bold = font('Pretendard-Bold.otf', 32)
small = font('Pretendard-Regular.otf', 20)
icon = Image.open(R / 'docs/icon.png').convert('RGBA').resize((52, 52))
for name, kicker, line1, line2, sub, foot in PAGES:
    im = Image.new('RGB', (1200, 630), '#F6F1E7')
    d = ImageDraw.Draw(im)
    for x in range(0, 1200, 24):
        for y in range(0, 630, 24):
            d.ellipse((x, y, x + 2, y + 2), fill='#E6DECF')
    im.paste(icon, (66, 46), icon)
    d.text((134, 54), kicker, font=bold, fill='#23211E')
    d.text((66, 168), line1, font=serif, fill='#23211E')
    w = d.textlength(line2, font=serif)
    d.rounded_rectangle((65, 296, 66 + w + 4, 337), radius=5, fill='#F3D66B')
    d.text((66, 260), line2, font=serif, fill='#23211E')
    d.text((69, 386), sub, font=sans, fill='#6A645B')
    d.line((66, 488, 1134, 488), fill='#E6DECF', width=2)
    d.text((69, 533), foot, font=sans, fill='#23211E')
    d.text((978, 538), 'dansuki.com', font=small, fill='#6A645B')
    out = R / 'docs/img' / name
    im.save(out, optimize=True)
    print('saved', out.relative_to(R))
