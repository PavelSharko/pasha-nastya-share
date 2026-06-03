import asyncio
from playwright.async_api import async_playwright
import os

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")

async def login_and_save():
    async with async_playwright() as p:
        print("LOG: Запуск браузера для ручного логина...")
        # Запускаем ВИДИМЫЙ браузер
        context = await p.chromium.launch_persistent_context(
            os.path.join(AGENT_DIR, "agent_profile"),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0]
        
        print("LOG: Переход на eRank...")
        await page.goto("https://members.erank.com/dashboard")
        
        print("\n!!! ВНИМАНИЕ !!!")
        print("Пожалуйста, залогинься в открывшемся окне браузера.")
        print("Как только увидишь свой дашборд, возвращайся сюда.")
        
        # Ждем, пока URL перестанет содержать 'login'
        while "login" in page.url or "auth" in page.url:
            await asyncio.sleep(2)
        
        print("SUCCESS: Авторизация обнаружена!")
        # Сохраняем куки в файл для будущего использования (хотя persistent_context и так сохраняет)
        storage = await context.storage_state()
        with open(AUTH_JSON, "w") as f:
            import json
            json.dump(storage, f)
            
        print(f"LOG: Сессия сохранена в {AUTH_JSON}")
        await context.close()

if __name__ == "__main__":
    asyncio.run(login_and_save())
