import asyncio
import os
from playwright.async_api import async_playwright

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")

async def check_vision_stealth():
    async with async_playwright() as p:
        print("LOG: Запуск браузера в ВИДИМОМ режиме для отладки...")
        # Запускаем Chromium с эмуляцией человека
        browser = await p.chromium.launch(
            headless=False, # ВКЛЮЧАЕМ ОКНО, чтобы ты видел что происходит
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(storage_state=AUTH_JSON)
        page = await context.new_page()

        url = "https://members.erank.com/keyword-tool?keyword=thirt%20footbal&country=EEA&source=etsy"
        print(f"LOG: Переход на {url}")
        
        try:
            # Ждем просто загрузки DOM, а не всей сети
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print("LOG: Страница начала грузиться. Ждем 15 секунд...")
            await page.wait_for_timeout(15000)
            
            shot_path = os.path.join(AGENT_DIR, "DEBUG_WHAT_HAPPENED.png")
            await page.screenshot(path=shot_path, full_page=True)
            print(f"LOG: Скриншот сделан: {shot_path}")
            print(f"LOG: Текст заголовка: {await page.title()}")
            
        except Exception as e:
            print(f"ERROR: {e}")
        
        print("Браузер закроется через 5 секунд...")
        await page.wait_for_timeout(5000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(check_vision_stealth())
