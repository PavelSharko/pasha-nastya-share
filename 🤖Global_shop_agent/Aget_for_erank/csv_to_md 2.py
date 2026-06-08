import pandas as pd
import os

# Пути
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = "/Users/pavelsarko/Library/Mobile Documents/iCloud~md~obsidian/Documents/work-notes/RAW"
INPUT_CSV = os.path.join(RAW_DIR, "erank_export_hail_mary.csv")
OUTPUT_MD = os.path.join(RAW_DIR, "erank_report_hail_mary_FINAL.md")

def convert_csv_to_md():
    if not os.path.exists(INPUT_CSV):
        print(f"ERROR: Файл {INPUT_CSV} не найден.")
        return

    try:
        # Читаем CSV (пробуем разные кодировки, если нужно)
        df = pd.read_csv(INPUT_CSV)
        
        # Добавляем колонку с нумерацией
        df.insert(0, '#', range(1, len(df) + 1))
        
        # Чистим названия колонок от лишних пробелов и переносов
        df.columns = [col.replace('\n', ' ').strip() for col in df.columns]
        
        # Генерируем Markdown
        md_table = df.to_markdown(index=False)
        
        with open(OUTPUT_MD, "w", encoding="utf-8") as f:
            f.write(f"# 🏆 Полный отчет eRank: hail mary\n\n")
            f.write(f"Всего найдено тегов: **{len(df)}**\n\n")
            f.write(md_table)
            f.write(f"\n\n--- \n*Отчет сконвертирован из официального экспорта eRank.*")
            
        print(f"SUCCESS: Отчет с нумерацией сохранен в {OUTPUT_MD}")
        print(f"LOG: Колонки: {list(df.columns)}")
        
    except Exception as e:
        print(f"ERROR: Ошибка конвертации: {e}")

if __name__ == "__main__":
    convert_csv_to_md()
