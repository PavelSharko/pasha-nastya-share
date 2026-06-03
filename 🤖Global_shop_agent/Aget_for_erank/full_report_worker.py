import asyncio
import os
import json
import pandas as pd
from playwright.async_api import async_playwright

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_JSON = os.path.join(AGENT_DIR, "auth.json")
RAW_DIR = "/Users/pavelsarko/Library/Mobile Documents/iCloud~md~obsidian/Documents/work-notes/RAW"

TOOLS_WITH_CSV = {
    "Keyword_Tool": "https://members.erank.com/keyword-tool",
    "Near_Matches": "https://members.erank.com/keyword-tool/near-matches",
    "Top_Listings": "https://members.erank.com/keyword-tool/top-listings",
    "Marketplaces": "https://members.erank.com/keyword-tool/marketplaces"
}

SERP_URL = "https://members.erank.com/keyword-tool/serp-analysis"

async def download_csv_robust(page, tool_url, keyword, country, tool_name):
    safe_kw = keyword.replace(" ", "%20")
    full_url = f"{tool_url}?keyword={safe_kw}&country={country}&source=etsy"
    try:
        await page.goto(full_url, timeout=90000, wait_until="networkidle")
        await page.wait_for_timeout(5000)
        export_btn = await page.query_selector("button:has-text('Export'), [aria-label*='Export'], .export-button, button:has-text('Download')")
        if export_btn:
            async with page.expect_download(timeout=30000) as download_info:
                await export_btn.click()
                try: await page.click("text=CSV", timeout=2000)
                except: pass
            download = await download_info.value
            temp_path = os.path.join(AGENT_DIR, f"temp_{tool_name.lower()}.csv")
            await download.save_as(temp_path)
            return temp_path
        return None
    except Exception as e:
        print(f"ERROR CSV [{tool_name}]: {e}")
        return None

async def scrape_serp_analysis(page, keyword, country):
    safe_kw = keyword.replace(" ", "%20")
    full_url = f"{SERP_URL}?keyword={safe_kw}&country={country}&source=etsy"
    print(f"LOG: Глубокий парсинг SERP Analysis...")
    
    try:
        await page.goto(full_url, timeout=90000, wait_until="networkidle")
        await page.wait_for_timeout(10000)

        serp_data = await page.evaluate("""() => {
            const results = { summary: {} };
            
            // 1. Улучшенный поиск метрик
            const labels = ["Listings Analyzed", "Average Price", "Average Hearts", "Total Views", "Avg. Views", "Avg. Daily Views", "Avg. Weekly Views"];
            labels.forEach(label => {
                const el = Array.from(document.querySelectorAll('*')).find(e => e.innerText === label);
                if (el) {
                    // Ищем ближайшее числовое значение в соседних элементах или родителе
                    const parent = el.parentElement;
                    const valEl = parent.querySelector('h2, [class*="value"], [class*="Typography"]');
                    results.summary[label] = valEl ? valEl.innerText.trim() : "Н/Д";
                } else {
                    results.summary[label] = "NOT_FOUND";
                }
            });

            // 2. Теги (более надежно через ссылки)
            results.popular_tags = Array.from(document.querySelectorAll('a[href*="keyword-tool?keyword="]'))
                .slice(0, 30)
                .map(a => ({ tag: a.innerText.trim() }))
                .filter(t => t.tag.length > 1);

            // 3. Категории
            const tables = Array.from(document.querySelectorAll('table'));
            const catTable = tables.find(t => t.innerText.includes('Category'));
            results.categories = catTable ? Array.from(catTable.querySelectorAll('tr')).slice(1, 10).map(tr => {
                const tds = tr.querySelectorAll('td');
                return tds.length >= 2 ? { cat: tds[0].innerText.trim(), pct: tds[1].innerText.trim() } : null;
            }).filter(i => i) : [];

            return results;
        }""")
        
        serp_data['etsy_best_seller_link'] = f"https://www.etsy.com/search?q={safe_kw}&is_best_seller=true"
        return serp_data
    except Exception as e:
        print(f"ERROR SERP: {e}")
        return None

async def run_full_dossier(keyword, country):
    async with async_playwright() as p:
        if not os.path.exists(AUTH_JSON): return

        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=AUTH_JSON)
        page = await context.new_page()

        collected_csv = {}
        for name, url in TOOLS_WITH_CSV.items():
            path = await download_csv_robust(page, url, keyword, country, name)
            if path: collected_csv[name] = path

        serp_data = await scrape_serp_analysis(page, keyword, country)
        await browser.close()

        final_md = os.path.join(RAW_DIR, f"ERANK_DOSSIER_{keyword.replace(' ','_')}.md")
        with open(final_md, "w", encoding="utf-8") as f:
            f.write(f"# 🛡️ Ультимативное досье eRank: {keyword}\n")
            f.write(f"Регион: {country} | Дата: 2026-06-03\n\n")

            if serp_data:
                f.write(f"## 💎 Анализ SERP\n")
                f.write(f"🔗 **Etsy Best Sellers:** [СМОТРЕТЬ НА ETSY]({serp_data['etsy_best_seller_link']})\n\n")
                f.write("### 📊 Сводные метрики\n")
                for k, v in serp_data['summary'].items():
                    f.write(f"- **{k}:** {v}\n")
                f.write("\n### 🏷️ Топ тегов\n")
                f.write(", ".join([f"`{t['tag']}`" for t in serp_data['popular_tags']]) + "\n\n")

            for name, path in collected_csv.items():
                f.write(f"## 📊 {name.replace('_',' ')}\n")
                try:
                    df = pd.read_csv(path)
                    df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
                    df.insert(0, '#', range(1, len(df) + 1))
                    f.write(df.head(50).to_markdown(index=False))
                    f.write("\n\n")
                    os.remove(path)
                except: pass
        
        print(f"🎉 ДОСЬЕ ГОТОВО: {final_md}")
        return serp_data

if __name__ == "__main__":
    import sys
    kw = sys.argv[1] if len(sys.argv) > 1 else "hail mary"
    ct = sys.argv[2] if len(sys.argv) > 2 else "EEA"
    asyncio.run(run_full_dossier(kw, ct))
