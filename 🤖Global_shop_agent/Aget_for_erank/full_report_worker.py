import asyncio
import os
import pandas as pd
from datetime import datetime
from playwright.async_api import async_playwright

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")
# Путь к базе данных агента (относительный)
DB_DIR = os.path.join(AGENT_DIR, "DB_agent")

# Инструменты eRank
TOOLS = {
    "Keyword_Tool": "https://members.erank.com/keyword-tool",
    "Near_Matches": "https://members.erank.com/keyword-tool/near-matches",
    "SERP_Analysis": "https://members.erank.com/keyword-tool/serp-analysis",
    "Top_Listings": "https://members.erank.com/keyword-tool/top-listings",
    "Marketplaces": "https://members.erank.com/keyword-tool/marketplaces"
}

async def download_csv_pro(page, tool_url, keyword, country, tool_name):
    safe_kw = keyword.replace(" ", "%20")
    full_url = f"{tool_url}?keyword={safe_kw}&country={country}&source=etsy"
    
    print(f"LOG: [{tool_name}] Обработка...")
    try:
        await page.goto(full_url, wait_until="domcontentloaded", timeout=60000)
        
        # Специальная обработка для SERP (она не имеет CSV)
        if tool_name == "SERP_Analysis":
            print(f"LOG: [{tool_name}] Живой парсинг...")
            await page.wait_for_timeout(10000)
            data = await page.evaluate("document.body.innerText")
            return ("TEXT", data[:2000]) # Возвращаем кусок текста для отчета

        # Для остальных ищем кнопку Export
        await page.wait_for_selector("table, button:has-text('Export')", timeout=40000)
        await page.wait_for_timeout(5000)

        export_btn = await page.query_selector("button:has-text('Export'), [aria-label*='Export'], .export-button")
        
        if export_btn:
            async with page.expect_download(timeout=30000) as download_info:
                await export_btn.scroll_into_view_if_needed()
                await export_btn.click()
                try: await page.click("text=CSV", timeout=2000); await page.wait_for_timeout(1000)
                except: pass
            
            download = await download_info.value
            temp_path = os.path.join(AGENT_DIR, f"temp_{tool_name.lower()}.csv")
            await download.save_as(temp_path)
            print(f"SUCCESS: [{tool_name}] Скачан.")
            return ("CSV", temp_path)
        
        print(f"WARNING: [{tool_name}] Кнопка не найдена.")
        return None
            
    except Exception as e:
        print(f"ERROR [{tool_name}]: {e}")
        return None

async def run_pro_dossier(keyword, country):
    async with async_playwright() as p:
        if not os.path.exists(AUTH_JSON):
            print(f"ERROR: Файл авторизации {AUTH_JSON} не найден.")
            return

        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=AUTH_JSON, viewport={'width':1920, 'height':1080})
        page = await context.new_page()

        results = {}
        for name, url in TOOLS.items():
            res = await download_csv_pro(page, url, keyword, country, name)
            if res: results[name] = res

        await browser.close()
        
        # Сохранение в DB_agent
        os.makedirs(DB_DIR, exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_kw = keyword.replace(" ", "_")
        
        # Формат имени: имя_тега_дата_регион
        filename_base = f"{safe_kw}_{date_str}_{country}_dossier"
        final_md = os.path.join(DB_DIR, f"{filename_base}.md")
        
        etsy_link = f"https://www.etsy.com/search?q={keyword.replace(' ', '+')}&is_best_seller=true"
        
        with open(final_md, "w", encoding="utf-8") as f:
            f.write(f"# 🛡️ Ультимативное досье eRank: {keyword}\n\n")
            f.write(f"**Дата:** {date_str}  \n")
            f.write(f"**Регион:** {country}  \n\n")
            f.write(f"🔗 **Etsy Best Sellers:** [{etsy_link}]({etsy_link})\n\n")

            for name, (res_type, content) in results.items():
                f.write(f"## 🛠️ {name}\n\n")
                if res_type == "CSV":
                    try:
                        df = pd.read_csv(content)
                        df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
                        df.insert(0, '#', range(1, len(df) + 1))
                        f.write(df.to_markdown(index=False))
                        os.remove(content)
                    except Exception as e:
                        f.write(f"Ошибка парсинга таблицы: {e}\n")
                else:
                    f.write(f"```text\n{content}\n```\n")
                f.write("\n\n")
        
        print(f"🎉 ДОСЬЕ ГОТОВО: {final_md}")

if __name__ == "__main__":
    import sys
    kw = sys.argv[1] if len(sys.argv) > 1 else "tshirt cat"
    ct = sys.argv[2] if len(sys.argv) > 2 else "US"
    asyncio.run(run_pro_dossier(kw, ct))
