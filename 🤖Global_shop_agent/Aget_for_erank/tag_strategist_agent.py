import os
import json
import re
import pandas as pd
from datetime import datetime

# Конфигурация путей
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(AGENT_DIR, "DB_agent")
BASE_DB_DIR = os.path.join(AGENT_DIR, "..", "база_данных_для_агентов")
TAGS_QUEUE_FILE = os.path.join(BASE_DB_DIR, "tags_before_check", "tags_queue.md")
RESULT_DB_DIR = os.path.join(BASE_DB_DIR, "tags_after_check")
RESULT_JSON_FILE = os.path.join(RESULT_DB_DIR, "processed_tags.json")

# Инструкция (скомпилированная из HELP_STRATEGY и Промт для тегов)
STRATEGY_RULES = """
# Инструкция по анализу тегов

## 1. Цветовая логика (Searches, Clicks, CTR, Competition)
- Идеально: Все 4 поля "Зеленые" (Высокие показатели, низкая конкуренция).
- Хорошо: 2-3 поля зеленые, остальные желтые/оранжевые.
- Допустимо: Минимум 2 оранжевых (если нет лучших вариантов).
- Мусор: Красная конкуренция при низких поисках/кликах.

## 2. Стратегии
- Массовый спрос: Приоритет Searches. Даже если CTR чуть ниже, объем важен.
- Узкая ниша: Приоритет Clicks и CTR. Низкий объем допустим при высокой вовлеченности и низкой конкуренции.

## 3. Критерии отбора
- Максимум 15 тегов на один запрос.
- Приоритет Long-tail фразам (длинные уточняющие запросы).
- Обязательно убирать "шумные" теги (высокая конкуренция, нет кликов).
"""

def clean_numeric(value):
    """Очистка строковых значений eRank в числа для сравнения"""
    if isinstance(value, (int, float)):
        return value
    if not value or not isinstance(value, str):
        return 0
    # Убираем запятые, знаки <, % и т.д.
    clean_val = re.sub(r'[^\d.]', '', value.replace(',', ''))
    try:
        return float(clean_val) if clean_val else 0
    except:
        return 0

def analyze_tags(json_data, strategy="mass"):
    """
    Применяет логику фильтрации к списку тегов из JSON.
    Возвращает список отфильтрованных тегов.
    """
    if not json_data:
        return []
    
    # Превращаем в DataFrame для удобства анализа
    df = pd.DataFrame(json_data)
    
    # Ключевые колонки (могут называться по-разному в зависимости от парсера)
    col_map = {
        'Keywords': ['Keywords', 'Keyword'],
        'Searches': ['Avg. Searches', 'Searches'],
        'Clicks': ['Avg. Clicks', 'Clicks'],
        'CTR': ['Avg. CTR', 'CTR'],
        'Competition': ['Etsy Competition', 'Competition']
    }
    
    # Определяем реальные имена колонок в данных
    real_cols = {}
    for standard, variations in col_map.items():
        for v in variations:
            if v in df.columns:
                real_cols[standard] = v
                break
    
    if 'Keywords' not in real_cols:
        return []

    # Подготовка данных для анализа (приведение к числам)
    analysis_list = []
    for _, row in df.iterrows():
        kw = row.get(real_cols['Keywords'], "")
        searches = clean_numeric(row.get(real_cols.get('Searches', ''), 0))
        clicks = clean_numeric(row.get(real_cols.get('Clicks', ''), 0))
        ctr = clean_numeric(row.get(real_cols.get('CTR', ''), "0%"))
        # Конкуренция - тут инвертированная логика (чем меньше, тем лучше)
        comp = clean_numeric(row.get(real_cols.get('Competition', ''), "High"))
        
        # Базовая фильтрация "мусора"
        if searches < 10 and clicks < 5:
            continue
            
        analysis_list.append({
            "keyword": kw,
            "searches": searches,
            "clicks": clicks,
            "ctr": ctr,
            "competition": comp,
            "score": (clicks * 2) + (searches * 0.5) if strategy == "mass" else (ctr * 10) + (clicks * 5)
        })

    # Сортировка по весу (score) и выбор топ-15
    sorted_tags = sorted(analysis_list, key=lambda x: x['score'], reverse=True)
    return [t['keyword'] for t in sorted_tags[:15]]

def load_queue_status():
    if not os.path.exists(TAGS_QUEUE_FILE):
        return []
    with open(TAGS_QUEUE_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except: pass
    return []

def run_strategist():
    queue = load_queue_status()
    if not queue:
        print("LOG: Очередь пуста.")
        return

    # Загружаем текущую базу обработанных тегов
    os.makedirs(RESULT_DB_DIR, exist_ok=True)
    if os.path.exists(RESULT_JSON_FILE):
        with open(RESULT_JSON_FILE, "r", encoding="utf-8") as f:
            try:
                processed_db = json.load(f)
            except:
                processed_db = {"topics": {}}
    else:
        processed_db = {"topics": {}}

    updated_count = 0
    
    for task in queue:
        # Берем только те, что уже проверены в eRank (yes)
        if task.get("cheked_in_erank") != "yes":
            continue
            
        topic_name = task["original_topic"]
        enriched_words = task["tags_to_check"]
        
        if topic_name not in processed_db["topics"]:
            processed_db["topics"][topic_name] = {}

        print(f"LOG: Анализ топика: {topic_name}")
        
        for word in enriched_words:
            safe_word = word.replace(" ", "_")
            # Ищем самый свежий JSON файл для этого слова в DB_agent
            matching_files = [f for f in os.listdir(DB_DIR) if f.startswith(safe_word) and f.endswith(".json")]
            if not matching_files:
                continue
                
            matching_files.sort(reverse=True) # По дате (имена содержат дату)
            latest_json_path = os.path.join(DB_DIR, matching_files[0])
            
            with open(latest_json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            
            # Анализируем (по умолчанию массовый спрос, можно менять)
            top_tags = analyze_tags(raw_data, strategy="mass")
            
            processed_db["topics"][topic_name][word] = top_tags
            updated_count += 1

    # Сохраняем финальную базу
    with open(RESULT_JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(processed_db, f, indent=2, ensure_ascii=False)

    print(f"SUCCESS: База после проверки обновлена. Обработано под-тегов: {updated_count}")
    print(f"Файл: {RESULT_JSON_FILE}")

if __name__ == "__main__":
    run_strategist()
