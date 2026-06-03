import asyncio
import os
from playwright.async_api import async_playwright

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")
RAW_DIR = "/Users/pavelsarko/Library/Mobile Documents/iCloud~md~obsidian/Documents/work-notes/RAW"

async def run_export_extraction(target_url, keyword_label):
    async with async_playwright() as p:
        print(f"LOG: Запуск Экспорт-Агента для: {keyword_label}")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=AUTH_JSON)
        page = await context.new_page()

        try:
            await page.goto(target_url, timeout=60000, wait_until="networkidle")
            await page.wait_for_selector("text=Avg. Searches", timeout=30000)
            
            print("LOG: Поиск кнопки экспорта...")
            # На eRank кнопка экспорта часто скрыта в меню или за иконкой 'Download'
            # Попробуем найти кнопку со словом 'Export' или 'CSV'
            
            # Ждем появления кнопки экспорта
            export_button = await page.query_selector("button:has-text('Export'), [aria-label*='Export'], .export-button")
            
            if not export_button:
                # Если кнопка не найдена сразу, сделаем скриншот, чтобы понять где она
                await page.screenshot(path=os.path.join(AGENT_DIR, "export_debug.png"))
                print("ERROR: Кнопка 'Export' не найдена. Проверьте export_debug.png")
                await browser.close()
                return False

            # Ожидаем событие скачивания
            async with page.expect_download() as download_info:
                print("LOG: Клик по кнопке экспорта...")
                await export_button.click()
                
                # Если выпадает меню, кликаем по CSV
                try:
                    csv_option = await page.query_selector("text=CSV")
                    if csv_option:
                        await csv_option.click()
                except: pass

            download = await download_info.value
            
            # Сохраняем файл в RAW
            safe_kw = keyword_label.replace(" ", "_")
            download_path = os.path.join(RAW_DIR, f"erank_export_{safe_kw}.csv")
            await download.save_as(download_path)
            
            print(f"SUCCESS: Файл успешно скачан и сохранен: {download_path}")
            await browser.close()
            return True

        except Exception as e:
            print(f"ERROR: {e}")
            await browser.close()
            return False

if __name__ == "__main__":
    kw = "hail mary"
    url = f"https://members.erank.com/keyword-tool?keyword={kw.replace(' ', '%20')}&country=EEA&source=etsy"
    asyncio.run(run_export_extraction(url, kw))
