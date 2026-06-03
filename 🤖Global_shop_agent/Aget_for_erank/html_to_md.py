import os
from bs4 import BeautifulSoup

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(AGENT_DIR, "last_erank_data.html")
REPORT_FILE = os.path.join(AGENT_DIR, "Keyword_Report_tshirt_cat.md")

def parse_erank_html():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: Файл {INPUT_FILE} не найден.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    report_md = "# 📊 Отчет eRank по тегу: tshirt cat\n\n"
    report_md += f"**Регион:** EEA (Европа) | **Источник:** Etsy\n\n"
    
    # Ищем таблицу статистики (обычно это первая большая таблица с данными)
    # Или ищем блоки по тексту меток
    data_map = {
        "Avg. Searches": "Н/Д",
        "Avg. Clicks": "Н/Д",
        "Avg. CTR": "Н/Д",
        "Etsy Competition": "Н/Д"
    }

    # Попробуем найти все элементы с классом, содержащим 'value' или 'stat'
    # eRank часто использует структуру: <div class="label">Avg. Searches</div><div class="value">1,234</div>
    
    for label in data_map.keys():
        label_node = soup.find(string=lambda t: label in t if t else False)
        if label_node:
            parent = label_node.find_parent()
            # Обычно значение идет СЛЕДУЮЩИМ элементом или внутри того же родителя
            full_text = parent.get_text(separator="|").split("|")
            for part in full_text:
                part = part.strip()
                if part and part != label and any(c.isdigit() for c in part):
                    data_map[label] = part
                    break
            
            # Если не нашли, ищем в соседнем блоке
            if data_map[label] == "Н/Д":
                sibling = parent.find_next_sibling()
                if sibling:
                    data_map[label] = sibling.get_text().strip()

    report_md += "## Основные показатели\n"
    report_md += f"| Метрика | Значение |\n| :--- | :--- |\n"
    for k, v in data_map.items():
        report_md += f"| {k} | **{v}** |\n"

    report_md += "\n---\n*Отчет создан автоматически агентом eRank Worker.*"

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"SUCCESS: Отчет обновлен в {REPORT_FILE}")

if __name__ == "__main__":
    parse_erank_html()
