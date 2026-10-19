"""Browser checks for public routes and legacy-link compatibility.
Run: uv run --with playwright python tool/test_clean_urls.py [base_url]
"""
import sys
from playwright.sync_api import sync_playwright,expect
BASE=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8767').rstrip('/')
SLUGS=['method','difficulty','privacy','spaced-review']
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
    page=browser.new_page(viewport={'width':390,'height':844})
    for slug in SLUGS:
        route='/'+slug+'/'
        response=page.goto(BASE+route,wait_until='load')
        assert response.status==200,(route,response.status)
        assert page.locator('h1').count()==1
        expect(page.locator('link[rel="canonical"]')).to_have_attribute('href','https://dansuki.com'+route)
        expect(page.locator('nav a.get')).to_have_text('무료로 받기')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        for image in page.locator('figure img').all():
            image.scroll_into_view_if_needed();image.evaluate('(e)=>e.decode()')
        page.goto(BASE+'/'+slug+'.html?from=legacy#reference',wait_until='load')
        expect(page).to_have_url(BASE+route+'?from=legacy#reference')
        page.goto(BASE+'/'+slug,wait_until='load');expect(page).to_have_url(BASE+route)
    page.goto(BASE+'/',wait_until='load')
    page.get_by_role('button',name='공부 방법',exact=True).filter(visible=True).click()
    page.locator('nav a[href="/spaced-review/"]').filter(visible=True).click()
    expect(page).to_have_url(BASE+'/spaced-review/')
    fallback=browser.new_context(java_script_enabled=False).new_page()
    fallback.goto(BASE+'/method.html',wait_until='load');expect(fallback).to_have_url(BASE+'/method/')
    browser.close()
print('PASS: clean routes, legacy query/hash preservation, slash normalization, menu links, no-JS redirect and mobile resources.')
