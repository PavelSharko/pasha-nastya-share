import asyncio
import os
import json
from playwright.async_api import async_playwright

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")
RAW_DIR = "/Users/pavelsarko/Library/Mobile Documents/iCloud~md~obsidian/Documents/work-notes/RAW"

async def extract_visible_table(page):
    """Вытаскивает данные из текущей таблицы на странице"""
    return await page.evaluate("""() => {
        const rows = Array.from(document.querySelectorAll('table tr'));
        const headerRow = rows.find(r => r.innerText.includes('Keywords') && r.innerText.includes('Searches'));
        if (!headerRow) return [];
        const headers = Array.from(headerRow.querySelectorAll('th, td')).map(h => h.innerText.trim());
        
        return rows.filter(r => r.querySelectorAll('td').length >= headers.length)
                   .map(row => {
                       const cells = Array.from(row.querySelectorAll('td'));
                       const d = {};
                       cells.forEach((c, i) => {
                           const h = headers[i] || `col_${i}`;
                           d[h] = c.innerText.trim();
                       });
                       return d;
                   }).filter(d => d['Keywords'] || d['Keyword']);
    }""")

async def run_hail_mary_scraper(max_pages=5):
    async with async_playwright() as p:
        print("LOG: Запуск скрапера...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=AUTH_JSON)
        page = await context.new_page()

        target_url = "https://members.erank.com/keyword-tool?keyword=hail%20mary&country=EEA&source=etsy"
        await page.goto(target_url, wait_until="networkidle")
        
        all_data = {}

        for p_num in range(1, max_pages + 1):
            print(f"LOG: Сбор страницы {p_num}...")
            
            # Ждем таблицу
            await page.wait_for_selector("table tr td", timeout=30000)
            await page.wait_for_timeout(5000) # Даем время на рендер цифр

            # Парсим
            rows = await extract_visible_table(page)
            for r in rows:
                key = r.get('Keywords') or r.get('Keyword')
                if key and key not in all_data:
                    all_data[key] = r
            
            print(f"LOG: Собрано уникальных тегов: {len(all_data)}")

            if p_num < max_pages:
                print(f"LOG: Переход на страницу {p_num + 1}...")
                try:
                    # Используем Jump to (ввод номера страницы)
                    # Обычно это input в конце страницы или в пагинации
                    jump_input = await page.query_selector("input[aria-label*='page'], .MuiInputBase-input")
                    if jump_input:
                        await jump_input.click(click_count=3) # Выделяем старый номер
                        await jump_input.fill(str(p_num + 1))
                        await jump_input.press("Enter")
                        await page.wait_for_timeout(7000) # Ждем загрузки
                    else:
                        # Если инпута нет, жмем на кнопку с цифрой
                        next_page_btn = await page.query_selector(f"button:has-text('{p_num + 1}')")
                        if next_page_btn:
                            await next_page_btn.click()
                            await page.wait_for_timeout(7000)
                        else:
                            print("LOG: Навигация не найдена. Завершаю на текущей странице.")
                            break
                except Exception as e:
                    print(f"WARNING: Не удалось переключить страницу: {e}")
                    break

        # Сохраняем результат
        os.makedirs(RAW_DIR, exist_ok=True)
        output_path = os.path.join(RAW_DIR, "erank_multi_page_hail_mary.md")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# 📊 ГИГА-отчет eRank: hail mary (Страницы 1-{max_pages})\n\n")
            f.write(f"Всего уникальных тегов: **{len(all_data)}**\n\n")
            
            if all_data:
                sample = list(all_data.values())[0]
                headers = ["#"] + list(sample.keys())
                f.write("| " + " | ".join(headers) + " |\n")
                f.write("| " + " | ".join(["---"] * len(headers)) + " |\n")
                
                for idx, row in enumerate(all_data.values(), 1):
                    f.write("| " + " | ".join([str(idx)] + [str(row.get(h, "")) for h in headers[1:]]) + " |\n")

        print(f"SUCCESS: Собрано {len(all_data)} тегов. Файл: {output_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_hail_mary_scraper(5))
