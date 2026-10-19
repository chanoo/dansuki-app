"""Check study navigation with real browser input.
Run: uv run --with playwright python tool/test_study_navigation.py [base_url]
"""
import re, sys
from playwright.sync_api import sync_playwright, expect
BASE=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8767').rstrip('/')
PAGES=['/','/method.html','/spaced-review.html','/difficulty.html','/privacy.html','/404.html']
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
    context=browser.new_context()
    page=context.new_page();errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    for width in [1440,390,320]:
        page.set_viewport_size({'width':width,'height':900})
        for path in PAGES:
            page.goto(BASE+path,wait_until='load')
            nav=page.locator('nav.top')
            toggle=nav.get_by_role('button',name='공부 방법',exact=True).filter(visible=True)
            expect(toggle).to_have_count(1,timeout=1000)
            toggle.click();expect(toggle).to_have_attribute('aria-expanded','true')
            study=nav.get_by_role('link',name=re.compile('^단숙이 공부법')).filter(visible=True)
            research=nav.get_by_role('link',name=re.compile('^복습 연구 이야기')).filter(visible=True)
            expect(study).to_be_visible();expect(research).to_be_visible()
            page.keyboard.press('Tab');expect(study).to_be_focused()
            page.keyboard.press('Tab');expect(research).to_be_focused()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,path)
            box=research.bounding_box();assert box['x']>=0 and box['x']+box['width']<=width,(width,path,box)
            page.keyboard.press('Escape');expect(research).to_be_hidden();expect(toggle).to_be_focused()
            page.keyboard.press('Space');expect(research).to_be_visible()
            page.mouse.click(width-2,800);expect(research).to_be_hidden()
            toggle.click();research.click();expect(page).to_have_url(re.compile('/spaced-review.html$'))
            article_nav=page.locator('nav.top');article_toggle=article_nav.get_by_role('button',name='공부 방법',exact=True).filter(visible=True)
            article_toggle.click();current=article_nav.locator('a[aria-current="page"]').filter(visible=True)
            expect(current).to_have_attribute('href',re.compile('spaced-review.html$'))
    page.goto(BASE+'/method.html',wait_until='load')
    page.set_viewport_size({'width':1440,'height':900})
    page.get_by_role('button',name='공부 방법',exact=True).filter(visible=True).click()
    page.set_viewport_size({'width':390,'height':900})
    expect(page.locator('nav .study-menu[open]')).to_have_count(0)
    page.emulate_media(color_scheme='dark')
    toggle=page.get_by_role('button',name='공부 방법',exact=True).filter(visible=True);toggle.click()
    current=page.locator('nav a[aria-current="page"]').filter(visible=True)
    page.keyboard.press('Tab');expect(current).to_be_focused();assert current.evaluate('(e)=>getComputedStyle(e).outlineStyle')=='solid'
    assert not errors,errors
    browser.close()
print('PASS: 6 pages × 3 widths; click/keyboard navigation, Escape/focus, outside click, current-page link and mobile popup bounds.')
