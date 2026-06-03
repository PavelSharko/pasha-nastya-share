# Инструкция построения веб-запросов для eRank 🤖

Этот документ содержит правила формирования URL для автоматизированного сбора данных из eRank (Keyword Tool).

## Базовая структура ссылки (Dashboard)
Основная страница после логина:
`https://members.erank.com/dashboard`

## Конструктор запросов (Keyword Tool)

Для получения данных по конкретному ключевому слову и стране используйте следующий шаблон:
`https://members.erank.com/keyword-tool?keyword=[КЛЮЧЕВОЕ_СЛОВО]&country=[КОД_СТРАНЫ]&source=etsy`

### Таблица кодов стран (Country Codes)

| Страна / Регион | Код в URL (`country`) |
| :--- | :--- |
| **США** | `USA` |
| **Европа (EEA)** | `EEA` |
| **Великобритания** | `GBR` |
| **Австралия** | `AUS` |
| **Канада** | `CAN` |
| **Германия** | `DEU` |
| **Франция** | `FRA` |
| **Индия** | `IND` |
| **Глобальный поиск** | `GLO` |

### Примеры запросов:

1. **Запрос `tshirt cat` для США:**
   `https://members.erank.com/keyword-tool?keyword=tshirt%20cat&country=USA&source=etsy`

2. **Запрос `tshirt cat` для Европы (EEA):**
   `https://members.erank.com/keyword-tool?keyword=tshirt%20cat&country=EEA&source=etsy`

3. **Запрос `tshirt cat` для Великобритании:**
   `https://members.erank.com/keyword-tool?keyword=tshirt%20cat&country=GBR&source=etsy`

---
**Важно:** Ключевые слова в URL должны быть закодированы (пробел = `%20`).
