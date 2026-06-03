import asyncio
import os
import json
import sys
from playwright.async_api import async_playwright

# Конфигурация путей
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")
RAW_DIR = "/Users/pavelsarko/Library/Mobile Documents/iCloud~md~obsidian/Documents/work-notes/RAW"

def save_results(all_results, captured_json_data, keyword_label):
    os.makedirs(RAW_DIR, exist_ok=True)
    safe_kw = keyword_label.replace(" ", "_")
    
    if captured_json_data:
        json_path = os.path.join(RAW_DIR, f"erank_raw_intercepted_{safe_kw}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(captured_json_data, f, indent=2, ensure_ascii=False)
        print(f"LOG: JSON сохранен: {json_path}")

    output_md = os.path.join(RAW_DIR, f"erank_multi_page_{safe_kw}.md")
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(f"# 📊 Глубокий отчет (Multi-Page): {keyword_label}\n\n")
        if all_results:
            # Берем заголовки из первого элемента
            headers = ["#"] + [k for k in all_results[0].keys() if k != "Source_Page"] + ["Page"]
            f.write("| " + " | ".join(headers) + " |\n")
            f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
            for i, row in enumerate(all_results, 1):
                page_num = row.get("Source_Page", "?")
                row_vals = [str(i)]
                for h in headers[1:-1]:
                    row_vals.append(str(row.get(h, "")))
                row_vals.append(str(page_num))
                f.write("| " + " | ".join(row_vals) + " |\n")
    print(f"SUCCESS: Отчет сохранен: {output_md}")

async def run_pro_extraction(target_url, keyword_label, max_pages=5):
    async with async_playwright() as p:
        if not os.path.exists(AUTH_JSON):
            print(f"ERROR: Файл авторизации не найден.")
            return

        print(f"LOG: Запуск ПРО-агента (Headless)...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=AUTH_JSON)
        page = await context.new_page()

        captured_json_data = []
        all_results = []

        async def handle_response(response):
            if "keyword" in response.url and "json" in response.headers.get("content-type", ""):
                try:
                    data = await response.json()
                    captured_json_data.append({"url": response.url, "data": data})
                except: pass

        page.on("response", handle_response)

        try:
            print(f"LOG: Переход на {target_url}")
            await page.goto(target_url, timeout=60000, wait_until="networkidle")
            
            # Попробуем установить 100 строк
            try:
                dropdown = await page.wait_for_selector(".MuiSelect-select, [aria-label*='Rows per page']", timeout=10000)
                if dropdown:
                    await dropdown.click()
                    await page.click("text=100")
                    await page.wait_for_timeout(5000)
            except: pass

            for current_page in range(1, max_pages + 1):
                print(f"LOG: Обработка страницы {current_page}...")
                await page.wait_for_selector("table tr td", timeout=20000)
                await page.wait_for_timeout(3000)

                page_data = await page.evaluate("""() => {
                    const rows = Array.from(document.querySelectorAll('table tr'));
                    const headerRow = rows.find(r => r.innerText.includes('Keywords') && r.innerText.includes('Searches'));
                    if (!headerRow) return [];
                    const headers = Array.from(headerRow.querySelectorAll('th, td')).map(h => h.innerText.trim());
                    return rows.filter(r => r.querySelectorAll('td').length >= headers.length)
                               .map(row => {
                                   const cells = Array.from(row.querySelectorAll('td'));
                                   const d = {};
                                   cells.forEach((c, i) => { d[headers[i] || `col_${i}`] = c.innerText.trim(); });
                                   return d;
                               }).filter(d => d['Keywords'] || d['Keyword']);
                }""")
                
                for item in page_data:
                    item['Source_Page'] = current_page
                    all_results.append(item)
                
                print(f"LOG: Найдено {len(page_data)} строк.")

                if current_page < max_pages:
                    print(f"LOG: Переход на страницу {current_page + 1}...")
                    # Пытаемся нажать кнопку "Next" (стрелка вправо)
                    next_btn = await page.query_selector('button[aria-label*="Go to next page"], button:has-text(">"), .pagination-next')
                    if next_btn:
                        await next_btn.click()
                        await page.wait_for_timeout(5000)
                    else:
                        print("LOG: Кнопка навигации не найдена.")
                        break
            
            save_results(all_results, captured_json_data, keyword_label)

        except Exception as e:
            print(f"ERROR: {e}")
            save_results(all_results, captured_json_data, keyword_label)
        finally:
            await browser.close()

if __name__ == "__main__":
    kw = "hail mary"
    url = f"https://members.erank.com/keyword-tool?keyword={kw.replace(' ', '%20')}&country=EEA&source=etsy"
    asyncio.run(run_pro_extraction(url, kw, max_pages=5))
