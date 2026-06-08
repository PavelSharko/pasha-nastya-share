import asyncio
import os
from playwright.async_api import async_playwright

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")

async def check_vision():
    async with async_playwright() as p:
        print("LOG: Запуск браузера для диагностики...")
        browser = await p.chromium.launch(headless=True) # Оставим headless, но сделаем скрин
        context = await browser.new_context(storage_state=AUTH_JSON)
        page = await context.new_page()

        url = "https://members.erank.com/keyword-tool?keyword=thirt%20footbal&country=EEA&source=etsy"
        print(f"LOG: Переход на {url}")
        
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(10000)
        
        shot_path = os.path.join(AGENT_DIR, "VISION_CHECK.png")
        await page.screenshot(path=shot_path, full_page=True)
        
        print(f"LOG: Скриншот сохранен: {shot_path}")
        print(f"LOG: Текущий URL: {page.url}")
        
        if "login" in page.url:
            print("DIAGNOSIS: СЕССИЯ ПРОТУХЛА. Нужно перелогиниться.")
        elif "cloudflare" in page.content().lower() or "bot" in page.content().lower():
            print("DIAGNOSIS: ОБНАРУЖЕНА ЗАЩИТА ОТ БОТОВ.")
        else:
            print("DIAGNOSIS: СТРАНИЦА ЗАГРУЖЕНА, НО ДАННЫЕ НЕ ВИДНЫ ПАРСЕРУ.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_vision())
