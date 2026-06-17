import asyncio
import os
import json
import re
import sys

# Импортируем существующий воркер
import erank_worker

# Конфигурация путей
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DB_DIR = os.path.join(AGENT_DIR, "..", "база_данных_для_агентов")
TAGS_QUEUE_DIR = os.path.join(BASE_DB_DIR, "tags_before_check")
QUEUE_FILE = os.path.join(TAGS_QUEUE_DIR, "tags_queue.md")

def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except: pass
    return []

def save_queue(queue_data):
    os.makedirs(TAGS_QUEUE_DIR, exist_ok=True)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        f.write("# 📋 Очередь тегов для проверки в eRank\n\n")
        f.write("```json\n")
        f.write(json.dumps(queue_data, indent=2, ensure_ascii=False))
        f.write("\n```\n")

async def process_queue(auto_mode=False):
    queue = load_queue()
    if not queue:
        print("LOG: Очередь пуста.")
        return

    # Находим все задачи со статусом "no"
    pending_tasks = [item for item in queue if item.get("cheked_in_erank") == "no"]
    
    if not pending_tasks:
        print("LOG: Нет новых задач для обработки.")
        return

    if not auto_mode:
        print(f"\n📝 В очереди ожидает топиков: {len(pending_tasks)}")
        confirm = input("Запустить автоматическую проверку всех тегов? (y/n): ")
        if confirm.lower() != 'y':
            print("LOG: Запуск отменен пользователем.")
            return

    for task in pending_tasks:
        topic = task["original_topic"]
        tags = task["tags_to_check"]
        country = task.get("country", "global")
        
        erank_country = country if country != "global" else "US"

        print(f"\n🚀 ОБРАБОТКА ТОПИКА: {topic} (Регион: {erank_country})")
        
        for tag in tags:
            print(f"--- Проверка тега: {tag} ---")
            target_url = f"https://members.erank.com/keyword-tool?keyword={tag.replace(' ', '%20')}&country={erank_country}&source=etsy"
            
            try:
                success = await erank_worker.run_extraction(target_url, tag)
                if success:
                    print(f"✅ Тег {tag} обработан.")
                else:
                    print(f"❌ Ошибка при обработке тега {tag}.")
            except Exception as e:
                print(f"ERROR: Исключение при обработке {tag}: {e}")
            
            await asyncio.sleep(15)

        task["cheked_in_erank"] = "yes"
        save_queue(queue)
        print(f"🏁 Топик {topic} завершен.\n")

if __name__ == "__main__":
    # Проверяем флаг авто-запуска
    is_auto = "procces_run: auto" in " ".join(sys.argv)
    asyncio.run(process_queue(auto_mode=is_auto))
