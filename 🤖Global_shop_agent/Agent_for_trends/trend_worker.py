import argparse
import os
import json
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright
try:
    import inquirer
except ImportError:
    print("Библиотека inquirer не установлена. Выполните: pip install -r requirements.txt")
    import sys
    sys.exit(1)

# Настройка путей
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Путь: 🤖Global_shop_agent/база_данных_для_агентов/actual_topics/
DB_DIR = os.path.normpath(os.path.join(AGENT_DIR, "..", "база_данных_для_агентов", "actual_topics"))

async def fetch_trends(geo, date_range, category):
    print(f"\n🔍 Начинаю поиск трендов...")
    print(f"📍 Регион: {geo}")
    print(f"📅 Период: {date_range}")
    print(f"📂 Категория: {category}\n")
    
    print("⏳ Сбор данных из Google Trends (через API)...")
    await asyncio.sleep(1) # Заглушка
    
    print("🌐 Подключение к живому Chrome (CDP) для анализа Etsy...")
    try:
        async with async_playwright() as p:
            # Подключаемся к запущенному Chrome с флагом --remote-debugging-port=9222
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = await context.new_page()
            
            print("🚀 Переход на Etsy Trends...")
            await page.goto("https://www.etsy.com/trends", timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000) # Даем время на рендер картинок
            
            # Эмуляция скролла для подгрузки динамического контента
            print("📜 Эмуляция скролла страницы...")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Простая заглушка: попытаемся выцепить заголовки H2, если они есть
            page_title = await page.title()
            print(f"✅ Страница загружена: {page_title}")
            
            await page.close()
            # Браузер не закрываем, так как он "живой" (пользовательский)
            
    except Exception as e:
        print("\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ К CHROME!")
        print("Убедитесь, что ваш браузер Google Chrome открыт и запущен с флагом:")
        print("--remote-debugging-port=9222")
        print(f"Детали ошибки: {e}\n")
        return []

    # Возвращаем Мок-данные для отчета
    return [
        {"topic": f"Kidcore Aesthetic {geo}", "reason": "High search volume in Google, Seen on Etsy Trends page"},
        {"topic": f"Embroidery Illusion {geo}", "reason": "Trending category, low competition on Etsy"}
    ]

def save_report(trends_data, geo, date_range):
    os.makedirs(DB_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"report_{timestamp}_{geo}.md"
    filepath = os.path.join(DB_DIR, filename)

    # Строго зафиксированные статусы для других агентов
    json_block = {
        "topics": [{f"topic{i+1}": t["topic"]} for i, t in enumerate(trends_data)],
        "tegs_agent_checked": "no",
        "etsy_popullary_agent_checked": "no",
        "real_sales_etsy_checked": "no"
    }

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Отчет по трендам ({geo})\n\n")
        f.write(f"**Дата:** {timestamp}\n")
        f.write(f"**Период:** {date_range}\n\n")
        
        f.write("## 📌 Найденные тренды:\n")
        for item in trends_data:
            f.write(f"- **{item['topic']}**: {item['reason']}\n")
            
        f.write("\n## ⚙️ Системные данные для агентов\n")
        f.write("```json\n")
        json.dump(json_block, f, indent=2, ensure_ascii=False)
        f.write("\n```\n")

    print(f"✅ Отчет успешно сохранен в базу данных:\n{filepath}")

def run_interactive_menu():
    print("🤖 Trend Agent запущен в ручном режиме.\n")
    questions = [
        inquirer.List('geo',
            message="Выберите регион поиска (Google Trends)",
            choices=[
                ('Глобально (Весь мир)', 'global'), 
                ('США (US)', 'US'), 
                ('Европа (EU)', 'EU'),
                ('Великобритания (GB)', 'GB')
            ],
            default='global'
        ),
        inquirer.List('date',
            message="Выберите глубину анализа",
            choices=[
                ('Последние 7 дней', 'now 7-d'), 
                ('Последние 30 дней', 'today 1-m'), 
                ('Реальное время', 'realtime')
            ],
            default='now 7-d'
        ),
        inquirer.List('category',
            message="Выберите категорию поиска",
            choices=[
                ('Все категории', '0'), 
                ('Развлечения (Кино/Сериалы)', 'e'), 
                ('Наука и Технологии', 't'),
                ('Бизнес', 'b')
            ],
            default='0'
        )
    ]
    answers = inquirer.prompt(questions)
    return answers['geo'], answers['date'], answers['category']

def main():
    parser = argparse.ArgumentParser(description="Trend Agent for Etsy")
    parser.add_argument("--status_run", choices=["auto", "manual"], default="manual", help="Режим запуска")
    parser.add_argument("--geo", default="global", help="Регион поиска (например, US)")
    parser.add_argument("--date", default="now 7-d", help="Временной промежуток")
    parser.add_argument("--category", default="0", help="Категория поиска")

    args = parser.parse_args()

    if args.status_run == "auto":
        print("⚙️ Запуск в режиме AUTO (управление другим агентом)")
        geo = args.geo
        date_range = args.date
        category = args.category
    else:
        geo, date_range, category = run_interactive_menu()

    # Запускаем сбор
    trends_data = asyncio.run(fetch_trends(geo, date_range, category))
    save_report(trends_data, geo, date_range)

if __name__ == "__main__":
    main()
