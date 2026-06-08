import json
import os

# Пути
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON = "/Users/pavelsarko/Library/Mobile Documents/iCloud~md~obsidian/Documents/work-notes/RAW/erank_raw_intercepted_hail_mary.json"
OUTPUT_MD = "/Users/pavelsarko/Library/Mobile Documents/iCloud~md~obsidian/Documents/work-notes/RAW/erank_final_report_hail_mary.md"

def format_val(v):
    if isinstance(v, dict):
        return v.get("value", "Н/Д")
    return str(v)

def process_json():
    if not os.path.exists(INPUT_JSON):
        print(f"ERROR: Файл {INPUT_JSON} не найден.")
        return

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        full_intercepted_data = json.load(f)

    # Собираем ВСЕ ключевые слова из ВСЕХ перехваченных запросов
    all_keywords = {} # Используем словарь для удаления дубликатов по названию тега

    for item in full_intercepted_data:
        url = item.get("url", "")
        data = item.get("data")
        
        kw_list = []
        # ПРИОРИТЕТ: near-matches (здесь обычно сотни тегов)
        if "near-matches" in url:
            if isinstance(data, dict): kw_list = data.get("results", [])
            elif isinstance(data, list): kw_list = data
            print(f"LOG: Найден блок Near Matches, строк: {len(kw_list)}")
        
        # ВТОРОЙ ПРИОРИТЕТ: related-searches
        elif "related-searches" in url:
            if isinstance(data, dict): kw_list = data.get("results", [])
            elif isinstance(data, list): kw_list = data
            print(f"LOG: Найден блок Related Searches, строк: {len(kw_list)}")

        for kw in kw_list:
            name = kw.get("keyword") or kw.get("term") or kw.get("plain_text")
            if name and name not in all_keywords:
                all_keywords[name] = kw

    if not all_keywords:
        print("ERROR: Список ключевых слов пуст.")
        return

    print(f"LOG: Всего уникальных ключевых слов найдено: {len(all_keywords)}")

    # Сортируем по популярности (Avg. Searches), если возможно
    sorted_keywords = sorted(
        all_keywords.values(), 
        key=lambda x: int(format_val(x.get("avg_searches")).replace(",","").replace("< 20","10") if format_val(x.get("avg_searches")).replace(",","").isdigit() or "< 20" in format_val(x.get("avg_searches")) else 0), 
        reverse=True
    )

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(f"# 🏆 Ультимативный отчет eRank (ПОЛНЫЙ): hail mary\n\n")
        f.write(f"Найдено тегов: **{len(sorted_keywords)}**\n\n")
        f.write("| # | Keyword | Searches | Clicks | CTR | Competition | Tag Occur. |\n")
        f.write("| --- | :--- | :--- | :--- | :--- | :--- | :--- |\n")
        
        for idx, item in enumerate(sorted_keywords, 1):
            term = item.get("keyword") or item.get("term") or item.get("plain_text") or "Unknown"
            searches = format_val(item.get("avg_searches", "0"))
            clicks = format_val(item.get("avg_clicks", "0"))
            ctr = format_val(item.get("ctr", "0"))
            if ctr and "%" not in ctr: ctr += "%"
            comp = format_val(item.get("competition", "0"))
            tag_occ = item.get("tag_occurrences", "0")
            
            f.write(f"| {idx} | **{term}** | {searches} | {clicks} | {ctr} | {comp} | {tag_occ} |\n")

    print(f"SUCCESS: Финальный отчет сохранен в {OUTPUT_MD}")

if __name__ == "__main__":
    process_json()
