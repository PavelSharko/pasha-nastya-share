import asyncio
import os
from playwright.async_api import async_playwright

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")

async def debug_tool(tool_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=AUTH_JSON)
        page = await context.new_page()
        
        print(f"DEBUG: Loading {tool_url}")
        await page.goto(tool_url, wait_until="networkidle")
        await page.wait_for_timeout(10000) # Long wait for JS
        
        # Screenshot
        shot_path = os.path.join(AGENT_DIR, "tool_debug.png")
        await page.screenshot(path=shot_path, full_page=True)
        print(f"DEBUG: Screenshot saved to {shot_path}")
        
        # Print button texts
        buttons = await page.query_selector_all("button")
        for b in buttons:
            txt = await b.inner_text()
            if txt: print(f"DEBUG: Found button: '{txt.strip()}'")
            
        await browser.close()

if __name__ == "__main__":
    # Test with Top Listings
    url = "https://members.erank.com/keyword-tool/top-listings?keyword=hail%20mary&country=EEA&source=etsy"
    asyncio.run(debug_tool(url))
