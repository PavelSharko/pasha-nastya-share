import os
import json
import re
import sys
from datetime import datetime

# Конфигурация путей
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DB_DIR = os.path.join(AGENT_DIR, "..", "база_данных_для_агентов")
ACTUAL_TOPICS_DIR = os.path.join(BASE_DB_DIR, "actual_topics")
TAGS_QUEUE_DIR = os.path.join(BASE_DB_DIR, "tags_before_check")
QUEUE_FILE = os.path.join(TAGS_QUEUE_DIR, "tags_queue.md")

def get_latest_report():
    if not os.path.exists(ACTUAL_TOPICS_DIR):
        return None
    files = [f for f in os.listdir(ACTUAL_TOPICS_DIR) if f.startswith("report_") and (f.endswith(".md") or f.endswith(".json"))]
    if not files:
        return None
    # Сортируем по имени (так как там дата в формате YYYY-MM-DD)
    files.sort(reverse=True)
    return os.path.join(ACTUAL_TOPICS_DIR, files[0])

def extract_json_from_md(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Ищем блок json
    match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            print(f"ERROR: Не удалось распарсить JSON в {file_path}")
            return None
    
    # Если это чистый JSON файл
    if file_path.endswith(".json"):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print(f"ERROR: Не удалось распарсить JSON файл {file_path}")
            return None
    
    return None

def enrich_topic(topic_str):
    # Извлекаем регион, если он есть в конце (2 буквы заглавными)
    country = "global"
    words = topic_str.split()
    
    # Список известных регионов (можно расширить)
    regions = ["US", "EU", "GB", "CA", "AU", "DE", "FR", "EEA"]
    
    if words and words[-1].upper() in regions:
        country = words[-1].upper()
        topic_name = " ".join(words[:-1])
    else:
        topic_name = topic_str

    # Генерация тегов
    tags = [topic_name]
    sub_words = topic_name.split()
    if len(sub_words) > 1:
        for w in sub_words:
            if len(w) > 2: # Пропускаем короткие предлоги
                tags.append(w)
    
    # Убираем дубликаты и ограничиваем до 3-5
    unique_tags = list(dict.fromkeys(tags))[:5]
    
    return {
        "original_topic": topic_str,
        "tags_to_check": unique_tags,
        "cheked_in_erank": "no",
        "country": country
    }

def update_queue(topics_to_add=None):
    report_path = get_latest_report()
    if not report_path:
        print("LOG: Файлы отчетов не найдены.")
        return False

    data = extract_json_from_md(report_path)
    if not data or "topics" not in data:
        print("ERROR: В отчете не найдены топики.")
        return False

    all_found_topics = []
    for topic_obj in data["topics"]:
        for key, value in topic_obj.items():
            if key.startswith("topic"):
                all_found_topics.append(value)

    # Если мы в ручном режиме, показываем что нашли
    if topics_to_add is None:
        print(f"\n🔎 В последнем отчете ({os.path.basename(report_path)}) найдено:")
        for i, t in enumerate(all_found_topics, 1):
            print(f"{i}. {t}")
        return all_found_topics

    # Добавляем выбранные топики в очередь
    new_entries = [enrich_topic(t) for t in topics_to_add]

    # Загружаем текущую очередь
    current_queue = []
    if os.path.exists(QUEUE_FILE):
        content = open(QUEUE_FILE, "r", encoding="utf-8").read()
        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
        if match:
            try:
                current_queue = json.loads(match.group(1))
            except: pass

    existing_topics = [item["original_topic"] for item in current_queue]
    added_count = 0
    for entry in new_entries:
        if entry["original_topic"] not in existing_topics:
            current_queue.append(entry)
            added_count += 1

    # Сохраняем
    os.makedirs(TAGS_QUEUE_DIR, exist_ok=True)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        f.write("# 📋 Очередь тегов для проверки в eRank\n\n")
        f.write("```json\n")
        f.write(json.dumps(current_queue, indent=2, ensure_ascii=False))
        f.write("\n```\n")

    print(f"SUCCESS: В очередь добавлено {added_count} новых топиков.")
    return True

if __name__ == "__main__":
    # По умолчанию запускаем полный поиск, если вызван напрямую
    update_queue()
