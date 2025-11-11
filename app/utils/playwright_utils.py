from playwright.async_api import async_playwright, Browser, Playwright
from typing import Optional

_browser: Optional[Browser] = None
_playwright: Optional[Playwright] = None

async def startup_browser():
    global _browser, _playwright
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)

async def get_browser() -> Browser:
    if _browser is None:
        raise RuntimeError("Browser not started. Call startup_browser() first.")
    return _browser

async def shutdown_browser():
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
