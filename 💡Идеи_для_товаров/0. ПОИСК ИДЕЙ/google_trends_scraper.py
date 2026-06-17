import os
import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime
import time

# Настройки
COUNTRIES = {
    'US': 'United States',
    'ES': 'Spain',
    'DE': 'Germany',
    'FR': 'France'
}

# Маппинг категорий Google Trends для Trending Searches (Realtime)
# Примечание: В pytrends категории для realtime трендов задаются строками
CATEGORY_MAP = {
    'Fashion & Beauty': 'f',
    'Games': 'g',
    'Shopping': 's',
    'Entertainment': 'e',
    'Hobbies & Leisure': 'h'
}

BASE_DIR = r'работа этси/etsy_and_shared/💡Идеи_для_товаров/0. ПОИСК ИДЕЙ'

def get_next_folder_index():
    index = 1
    while os.path.exists(os.path.join(BASE_DIR, f'search_ideas_from_googletrends_{index}')):
        index += 1
    return index

def save_to_csv(df, folder, name):
    if df is not None and not df.empty:
        path = os.path.join(folder, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"    Сохранено: {name}.csv")
    else:
        print(f"    Пропуск (нет данных): {name}")

def fetch_and_save_all():
    index = get_next_folder_index()
    output_dir = os.path.join(BASE_DIR, f'search_ideas_from_googletrends_{index}')
    os.makedirs(output_dir, exist_ok=True)
    print(f"🚀 Начинаю сбор данных в папку: {output_dir}")

    pytrends = TrendReq(hl='en-US', tz=360)

    for geo, country_name in COUNTRIES.items():
        print(f"\n🌍 Обработка: {country_name} ({geo})")
        
        # 1 & 2. Image Search (Last 7 days)
        try:
            pytrends.build_payload(kw_list=[''], timeframe='now 7-d', geo=geo, gprop='images')
            related = pytrends.related_queries()
            # Для пустого списка ключевых слов pytrends может вести себя специфично,
            # обычно Google Trends требует хотя бы одно слово для 'Explore'.
            # Но мы попробуем популярные ниши Etsy для затравки, если пустой запрос не сработает.
            # На самом деле, "Trending Searches" лучше подходит для общего поиска.
        except Exception as e:
            print(f"  Ошибка в Explore Image: {e}")

        # 3 & 4. Shopping Search (Last 7 days)
        # Аналогично Explore.

        # 5-9. Trending Searches (Realtime - Last 48h)
        # В pytrends есть trending_searches(pn='united_states') - это ежедневные
        # И realtime_trending_searches(geo='US', cat='all') - это за 48ч
        
        for cat_name, cat_code in CATEGORY_MAP.items():
            try:
                print(f"  Сбор категории: {cat_name}")
                df = pytrends.realtime_trending_searches(geo=geo, cat=cat_code)
                save_to_csv(df, output_dir, f"{geo}_trending_{cat_name.replace(' ', '_')}")
                time.sleep(2) # Пауза чтобы не забанили
            except Exception as e:
                print(f"  Ошибка в {cat_name}: {e}")

    print(f"\n✅ Сбор завершен. Все файлы в {output_dir}")

if __name__ == "__main__":
    fetch_and_save_all()
