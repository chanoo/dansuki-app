"""Audit the public site before/after publishing.
Run: uv run --with beautifulsoup4 python tool/check_seo.py [https://dansuki.com]
Checks technical consistency; this is not a ranking or rich-results guarantee.
"""
from pathlib import Path
from urllib.parse import urljoin,urlsplit,unquote
import json,sys,urllib.request,xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
D=Path(__file__).resolve().parent.parent/'docs';SITE='https://dansuki.com/'
PAGES=['index.html','method/index.html','difficulty/index.html','spaced-review/index.html','privacy/index.html','help/index.html','android/index.html','404.html']
def route(name):
 return '' if name=='index.html' else name.removesuffix('index.html') if name.endswith('/index.html') else name
base=sys.argv[1].rstrip('/')+'/' if len(sys.argv)>1 else None
errors=[];out=[];seen_titles=set();seen_desc=set()
def check(ok,message):
 if not ok:errors.append(message)
def load(name):
 if base:
  url=base+route(name)
  with urllib.request.urlopen(url,timeout=20) as response:return response.read().decode()
 return (D/name).read_text()
for name in PAGES:
 soup=BeautifulSoup(load(name),'html.parser');prefix=name+': '
 title=soup.title.get_text(strip=True) if soup.title else ''
 check(bool(title),prefix+'missing title');check(title not in seen_titles,prefix+'duplicate title');seen_titles.add(title)
 check(len(soup.select('h1'))==1,prefix+'expected one H1')
 check(soup.html and soup.html.get('lang','').startswith('ko'),prefix+'missing Korean language')
 robots=soup.select_one('meta[name="robots"]');robot_value=robots.get('content','') if robots else ''
 if name=='404.html':
  check('noindex' in robot_value,prefix+'404 should be noindex')
  check(not soup.select('link[rel="canonical"]'),prefix+'404 must not claim a valid-page canonical')
  og=soup.select_one('meta[property="og:title"]');check(og and og.get('content')==title,prefix+'incorrect 404 share title')
  continue
 description=soup.select_one('meta[name="description"]');description=description.get('content','') if description else ''
 check(bool(description),prefix+'missing description');check(description not in seen_desc,prefix+'duplicate description');seen_desc.add(description)
 canonical=SITE+route(name)
 tags=soup.select('link[rel="canonical"]');check(len(tags)==1 and tags[0].get('href')==canonical,prefix+'incorrect canonical')
 check('noindex' not in robot_value,prefix+'unexpected noindex')
 check('max-image-preview:large' in robot_value,prefix+'large image preview not allowed explicitly')
 for prop,expected in [('og:title',title),('og:description',description),('og:url',canonical)]:
  tag=soup.select_one(f'meta[property="{prop}"]');check(tag and tag.get('content')==expected,prefix+prop+' mismatch')
 nodes=[]
 for block in soup.select('script[type="application/ld+json"]'):
  try:
   data=json.loads(block.string or block.get_text());nodes+=data.get('@graph',[data])
  except Exception as e:errors.append(prefix+'invalid JSON-LD '+str(e))
 check(bool(nodes),prefix+'missing schema')
 for node in nodes:
  if node.get('@type') in ['WebPage','Article','BlogPosting']:
   check(node.get('inLanguage')=='ko-KR',prefix+'schema missing language')
   check(node.get('url')==canonical,prefix+'schema URL mismatch')
 for el in soup.select('a[href],img[src],script[src],link[rel="stylesheet"][href],link[rel="preload"][href],source[srcset]'):
  value=el.get('href') or el.get('src') or el.get('srcset');url=urljoin(canonical,value);u=urlsplit(url)
  if u.netloc!='dansuki.com':continue
  file=D/(unquote(u.path).lstrip('/') or 'index.html')
  if file.is_dir():file=file/'index.html'
  check(file.exists(),prefix+'missing local target '+value)
  if u.fragment and file.suffix=='.html':
   target=BeautifulSoup(file.read_text(),'html.parser');check(target.find(id=u.fragment) is not None,prefix+'missing fragment '+value)
 if name=='spaced-review/index.html':
  article=next((n for n in nodes if n.get('@type') in ['Article','BlogPosting']),None)
  check(bool(article),prefix+'missing article schema')
  check(bool(soup.select('.article-toc a[href^="#"]')),prefix+'missing article navigation')
  check(bool(soup.select('.byline time[datetime]')),prefix+'missing machine-readable byline date')
  if article:check(isinstance(article.get('mainEntityOfPage'),dict),prefix+'article webpage relationship missing')
 out.append({'page':canonical,'title':title,'description_length':len(description),'schema_types':[n.get('@type') for n in nodes]})
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','image':'http://www.google.com/schemas/sitemap-image/1.1'}
sitemap=load('sitemap.xml');root=ET.fromstring(sitemap)
urls=[e.text for e in root.findall('s:url/s:loc',ns)]
check(set(urls)=={SITE+route(n) for n in PAGES if n!='404.html'},'Sitemap canonical URL set mismatch')
for e in root.findall('s:url/image:image/image:loc',ns):check((D/urlsplit(e.text).path.lstrip('/')).exists(),'Missing sitemap image '+e.text)
check('Sitemap: '+SITE+'sitemap.xml' in load('robots.txt'),'robots sitemap reference missing')
report={'scope':'live' if base else 'local','pages':out,'errors':errors,'status':'PASS' if not errors else 'FAIL'}
print(json.dumps(report,ensure_ascii=False,indent=2))
sys.exit(1 if errors else 0)
