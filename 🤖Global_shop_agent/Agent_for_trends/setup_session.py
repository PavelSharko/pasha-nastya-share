import asyncio
import os
from playwright.async_api import async_playwright

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "etsy_session.json")

async def main():
    async with async_playwright() as p:
        print("🚀 Открываем браузер для авторизации на Etsy...")
        # Запускаем НЕ в headless режиме, чтобы Настя могла пройти капчу
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.etsy.com/signin")
        
        print("=========================================================")
        print("❗ Пожалуйста, войдите в свой аккаунт Etsy в браузере.")
        print("❗ Пройдите все проверки безопасности (Cloudflare/Капча).")
        print("❗ После успешного входа вернитесь в консоль и нажмите ENTER.")
        print("=========================================================")
        
        input("Нажмите ENTER после успешной авторизации...")

        await context.storage_state(path=AUTH_JSON)
        print(f"✅ Сессия успешно сохранена в {AUTH_JSON}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
