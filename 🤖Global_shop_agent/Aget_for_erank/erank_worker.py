import asyncio
import os
import json
import sys
from datetime import datetime
import urllib.parse
from playwright.async_api import async_playwright

# Конфигурация путей
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")
# Путь к базе данных агента (относительный)
DB_DIR = os.path.join(AGENT_DIR, "DB_agent")

def get_region_from_url(url):
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        return params.get('country', ['unknown'])[0]
    except:
        return "unknown"

async def run_extraction(target_url, keyword_label):
    async with async_playwright() as p:
        if not os.path.exists(AUTH_JSON):
            print(f"ERROR: Файл авторизации {AUTH_JSON} не найден. Запустите manual_login.py")
            return False

        print(f"LOG: Запуск браузера (Headless)...")
        browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context(storage_state=AUTH_JSON)
        page = await context.new_page()

        print(f"LOG: Переход на страницу запроса: {target_url}")
        try:
            await page.goto(target_url, timeout=60000, wait_until="networkidle")
            
            print("LOG: Ожидание загрузки таблицы данных...")
            try:
                # Ждем появления таблицы. Обычно у них есть таблицы с ID или классами.
                # Мы подождем текст, который точно есть в заголовке таблицы
                await page.wait_for_selector("text=Avg. Searches", timeout=30000)
                # Даем время на полную прогрузку JS-таблицы
                await page.wait_for_timeout(10000) 
            except:
                print("WARNING: Таблица не прогрузилась вовремя.")

            if "login" in page.url:
                print("ERROR: Сессия истекла.")
                await browser.close()
                return False

            # ГЛУБОКАЯ ЭКСТРАКЦИЯ ТАБЛИЦЫ
            print("LOG: Извлечение данных из таблицы...")
            table_data = await page.evaluate("""() => {
                const rows = Array.from(document.querySelectorAll('table tr'));
                if (rows.length === 0) return [];
                
                // Находим заголовок, чтобы понять индексы колонок
                const headerRow = rows.find(r => r.innerText.includes('Keywords') && r.innerText.includes('Searches'));
                if (!headerRow) return [];
                
                const headers = Array.from(headerRow.querySelectorAll('th, td')).map(h => h.innerText.trim());
                
                const results = [];
                rows.forEach(row => {
                    const cells = Array.from(row.querySelectorAll('td'));
                    if (cells.length >= headers.length) {
                        const rowData = {};
                        cells.forEach((cell, idx) => {
                            const header = headers[idx] || `col_${idx}`;
                            // Если в ячейке есть график (тренд), мы его пропускаем или помечаем
                            if (cell.querySelector('canvas') || cell.querySelector('svg')) {
                                rowData[header] = "[Trend]";
                            } else {
                                rowData[header] = cell.innerText.trim();
                            }
                        });
                        // Добавляем только если есть ключевое слово
                        if (rowData['Keywords'] || rowData['Keyword']) {
                            results.push(rowData);
                        }
                    }
                });
                return results;
            }""")

            if not table_data:
                print("ERROR: Данные в таблице не найдены. Возможно, изменилась верстка.")
                # Сделаем скриншот для отладки, если данных нет
                await page.screenshot(path=os.path.join(AGENT_DIR, "error_debug.png"))
                await browser.close()
                return False

            print(f"LOG: Извлечено строк: {len(table_data)}")

            # Сохранение в DB_agent
            os.makedirs(DB_DIR, exist_ok=True)
            
            region = get_region_from_url(target_url)
            date_str = datetime.now().strftime("%Y-%m-%d")
            safe_keyword = keyword_label.replace(" ", "_")
            
            # Формат имени: имя_тега_дата_регион
            filename_base = f"{safe_keyword}_{date_str}_{region}"
            
            output_json = os.path.join(DB_DIR, f"{filename_base}.json")
            output_md = os.path.join(DB_DIR, f"{filename_base}.md")

            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(table_data, f, indent=4, ensure_ascii=False)

            with open(output_md, "w", encoding="utf-8") as f:
                f.write(f"# 📊 Глубокий отчет eRank: {keyword_label}\n\n")
                f.write(f"**Дата:** {date_str}  \n")
                f.write(f"**Регион:** {region}  \n\n")
                
                # Формируем заголовки таблицы Markdown
                if table_data:
                    headers = list(table_data[0].keys())
                    f.write("| " + " | ".join(headers) + " |\n")
                    f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
                    
                    for row in table_data:
                        f.write("| " + " | ".join([str(row.get(h, "")) for h in headers]) + " |\n")

                f.write(f"\n\n--- \n*Данные собраны глубоким парсером таблицы.*")

            print(f"SUCCESS: Полный отчет сохранен в {output_md}")
            
            await browser.close()
            return True
            
        except Exception as e:
            print(f"ERROR: Ошибка: {str(e)}")
            await browser.close()
            return False

if __name__ == "__main__":
    test_keyword = "tshirt cat"
    test_url = f"https://members.erank.com/keyword-tool?keyword={test_keyword.replace(' ', '%20')}&country=EEA&source=etsy"
    
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(run_extraction(test_url, test_keyword))
    if not success: sys.exit(1)
