"""Build the sharing image for the spaced-review article using brand assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent.parent
im=Image.new('RGB',(1200,630),'#F6F1E7');d=ImageDraw.Draw(im)
for x in range(0,1200,24):
 for y in range(0,630,24):d.ellipse((x,y,x+2,y+2),fill='#E6DECF')
def font(name,size):return ImageFont.truetype(str(R/'brand'/name),size)
serif=font('MaruBuri-Bold.ttf',63);sans=font('Pretendard-Regular.otf',26);bold=font('Pretendard-Bold.otf',32)
icon=Image.open(R/'docs/icon.png').convert('RGBA').resize((52,52))
im.paste(icon,(66,46),icon);d.text((134,54),'단숙이 공부 이야기',font=bold,fill='#23211E')
d.text((66,168),'오늘 외운 단어를,',font=serif,fill='#23211E')
d.rounded_rectangle((65,296,950,337),radius=5,fill='#F3D66B')
d.text((66,260),'단숙이가 다시 묻는 이유',font=serif,fill='#23211E')
d.text((69,386),'실험 48개 · 학습자 3,411명으로 살펴본 간격 학습',font=sans,fill='#6A645B')
d.line((66,488,1134,488),fill='#E6DECF',width=2)
d.text((69,533),'오늘의 새 단어와, 전에 외운 단어를 함께.',font=sans,fill='#23211E')
d.text((978,538),'dansuki.com',font=font('Pretendard-Regular.otf',20),fill='#6A645B')
im.save(R/'docs/img/research/spaced-review-og.png',optimize=True)
print('Generated 1200×630 article sharing image.')
