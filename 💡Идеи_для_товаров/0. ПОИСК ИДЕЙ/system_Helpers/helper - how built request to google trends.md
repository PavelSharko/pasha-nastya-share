
## 1. Популярные запросы прямо сейчас (Trending Now)

### Ежедневные тренды (Daily Search Trends)
Показывает популярные запросы за последние сутки.
- **Базовый URL**: `https://trends.google.com/trends/trendingsearches/daily`
- **Параметр**: `?geo=[КОД_СТРАНЫ]`
- **Пример**: `https://trends.google.com/trends/trendingsearches/daily?geo=US`

### Тренды в реальном времени (Realtime Search Trends)
Показывает то, что ищут прямо в эту минуту.
- **Базовый URL**: `https://trends.google.com/trends/trendingsearches/realtime`
- **Параметры**: `?geo=[КОД_СТРАНЫ]&cat=[БУКВА_КАТЕГОРИИ]`
- **Пример**: `https://trends.google.com/trends/trendingsearches/realtime?geo=US&cat=t`

**Буквенные коды категорий для Realtime:**
- `all` — Все категории
- `b` — Бизнес (Business)
- `e` — Развлечения (Entertainment)
- `m` — Здоровье (Health/Medical)
- `t` — Наука и техника (Sci/Tech)
- `s` — Спорт (Sports)
- `h` — Главные новости (Top Stories)

---

## 2. Анализ запросов (Explore)
Позволяет искать тренды по конкретным словам, времени и регионам.
- **Базовый URL**: `https://trends.google.com/trends/explore`
- **Формула**: `?q=[ЗАПРОС]&date=[ДАТА]&geo=[СТРАНА]&cat=[ID_КАТЕГОРИИ]&gprop=[ТИП_ПОИСКА]`

### Параметры:

#### 1. q= (Поисковый запрос)
- Одно слово: `q=bitcoin`
- Фраза: `q=elon+musk` (пробелы заменяются на `+` или `%20`)
- Сравнение: `q=bitcoin,ethereum,solana` (до 5 слов через запятую)

#### 2. date= (Временной промежуток)
- Последний час: `date=now%201-H`
- Последние 4 часа: `date=now%204-H`
- Последний день: `date=now%201-d`
- Последние 7 дней: `date=now%207-d`
- Последние 30 дней: `date=today%201-m`
- Последние 90 дней: `date=today%203-m`
- Последние 12 месяцев (по умолчанию): `date=today%2012-m`
- Последние 5 лет: `date=today%205-y`
- За все время (с 2004): `date=all`
- Точные даты: `date=YYYY-MM-DD%20YYYY-MM-DD` (например: `date=2023-01-01%202023-12-31`)

#### 3. geo= (География)
- Весь мир: оставить пустым или не указывать (`geo=`)
- США: `geo=US`
- Штат США: `geo=US-CA` (Калифорния), `geo=US-NY` (Нью-Йорк)
- Коды стран Европы (ISO 3166-1 alpha-2): `AT` (Австрия), `BE` (Бельгия), `DE` (Германия), `FR` (Франция) и т.д.

#### 4. cat= (Категория поиска)
- Все категории (по умолчанию): `cat=0`
- Примеры ID: `12` (Бизнес), `18` (Книги), `16` (Новости), `71` (Еда) и др.

#### 5. gprop= (Тип поиска)
- Поиск по картинкам: `gprop=images`
- Поиск по новостям: `gprop=news`
- Поиск по товарам (Google Shopping): `gprop=froogle`
- Поиск по YouTube: `gprop=youtube`
- Обычный веб-поиск: параметр не указывается.
