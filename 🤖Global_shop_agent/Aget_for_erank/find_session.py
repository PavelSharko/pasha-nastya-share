import os
import sqlite3
import shutil

# Список путей к профилям
base_path = os.path.expanduser("~/Library/Application Support/Google/Chrome")
profiles = ["Default", "Profile 1", "Profile 4", "Profile 7"]

def check_cookies_in_profile(profile_name):
    cookie_path = os.path.join(base_path, profile_name, "Network", "Cookies")
    if not os.path.exists(cookie_path):
        # В старых версиях Chrome путь был другим
        cookie_path = os.path.join(base_path, profile_name, "Cookies")
        if not os.path.exists(cookie_path):
            return False
    
    # Копируем файл куки во временный, чтобы не было ошибки "database is locked"
    temp_cookie = f"/tmp/cookies_{profile_name.replace(' ', '_')}"
    try:
        shutil.copy2(cookie_path, temp_cookie)
        conn = sqlite3.connect(temp_cookie)
        cursor = conn.cursor()
        
        # Ищем куки erank.com
        cursor.execute("SELECT name FROM cookies WHERE host_key LIKE '%erank.com%'")
        results = cursor.fetchall()
        conn.close()
        os.remove(temp_cookie)
        
        if results:
            print(f"FOUND: В профиле '{profile_name}' найдено {len(results)} куки для erank.com")
            return True
        return False
    except Exception as e:
        print(f"DEBUG: Ошибка при чтении {profile_name}: {e}")
        return False

print("Начинаю поиск активной сессии eRank в профилях Chrome...")
found_any = False
for p in profiles:
    if check_cookies_in_profile(p):
        found_any = True

if not found_any:
    print("NOT_FOUND: Ни в одном профиле Chrome не найдены куки erank.com.")
