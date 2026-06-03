import asyncio
from playwright.async_api import async_playwright

async def run_cdp():
    async with async_playwright() as p:
        try:
            # Пытаемся подключиться к уже запущенному браузеру
            print("LOG: Попытка подключения к Chrome через порт 9222...")
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            
            # Используем первый контекст (который уже открыт у пользователя)
            context = browser.contexts[0]
            page = await context.new_page()
            
            print("LOG: Проверка авторизации на eRank...")
            await page.goto("https://members.erank.com/dashboard", timeout=30000)
            
            if "login" in page.url:
                print("ERROR: Сессия не найдена даже в открытом браузере. Пожалуйста, залогиньтесь.")
            else:
                print("SUCCESS: Авторизация подтверждена!")
                target_url = "https://members.erank.com/keyword-tool?keyword=tshirt%20cat&country=EEA&source=etsy"
                print(f"LOG: Переход на {target_url}")
                await page.goto(target_url, wait_until="networkidle")
                await page.wait_for_timeout(3000)
                
                content = await page.content()
                with open("last_erank_data.html", "w") as f:
                    f.write(content)
                print("SUCCESS: Данные сохранены в last_erank_data.html")
            
            await page.close()
            # Мы не закрываем сам браузер, только наше соединение
        except Exception as e:
            print(f"ERROR: Не удалось подключиться к Chrome. Убедитесь, что он запущен с флагом --remote-debugging-port=9222")
            print(f"DEBUG: {e}")

if __name__ == "__main__":
    asyncio.run(run_cdp())
