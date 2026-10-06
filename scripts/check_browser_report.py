"""Optional Playwright smoke check for a generated local report.

Install playwright and its Chromium browser separately; neither is a runtime dependency.
"""

from pathlib import Path
import sys

from playwright.sync_api import sync_playwright


def check(path: Path):
    errors = []
    requests = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1360, "height": 1000})
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append(request.url))
        page.goto(path.resolve().as_uri())
        page.wait_for_selector('#rows tr')
        count = page.locator('#rows tr').count()
        assert count > 0
        page.select_option('#outcome', 'failed')
        failures = page.locator('#rows tr').count()
        assert 0 < failures < count
        page.select_option('#category', 'temporary')
        assert page.locator('#rows tr').count() == 7
        page.select_option('#category', 'revoke')
        assert page.locator('#rows tr').count() == 11
        page.select_option('#category', '')
        page.locator('#rows button').first.click()
        assert page.locator('#detail .answer.bad').count() == 1
        assert page.locator('#rows button[aria-pressed="true"]').evaluate('(button) => button === document.activeElement')
        page.select_option('#policy', 'scoped_state')
        assert page.locator('#rows tr').count() == 0
        assert page.locator('#empty').is_visible()
        page.select_option('#outcome', 'passed')
        assert page.locator('#rows tr').count() > 0
        page.select_option('#scenario', 'temporary_05')
        assert page.locator('#rows tr').count() == 4
        page.locator('#rows button').first.click()
        assert page.locator('#detail .timeline li').count() == 3
        page.select_option('#language', 'en')
        assert page.locator('html').get_attribute('lang') == 'en'
        assert page.locator('#policy').input_value() == 'scoped_state'
        assert page.locator('#scenario').input_value() == 'temporary_05'
        assert page.locator('#detail h3').first.inner_text() == 'Events available at this query'
        assert page.locator('header img').evaluate('(img) => img.complete && img.naturalWidth > 0')
        for width in (390, 768, 1360):
            page.set_viewport_size({'width': width, 'height': 900})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), width
        assert not errors, errors
        assert not any(url.startswith(('http://', 'https://')) for url in requests), requests
        browser.close()
    print(f'Browser report checked: {count} rows, {failures} mismatches, filters, language, history, offline assets, and responsive layouts.')


if __name__ == '__main__':
    check(Path(sys.argv[1]))
