import os
import sqlite3
import shutil

paths = [
    "~/Library/Application Support/Google/Chrome/Default/Cookies",
    "~/Library/Application Support/Google/Chrome/Default/Network/Cookies",
    "~/Library/Application Support/Google/Chrome/Default/Default/Cookies"
]

for p in paths:
    full_path = os.path.expanduser(p)
    if os.path.exists(full_path):
        temp_cookie = "/tmp/check_cookies"
        try:
            shutil.copy2(full_path, temp_cookie)
            conn = sqlite3.connect(temp_cookie)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM cookies WHERE host_key LIKE '%erank.com%'")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"PATH: {p} | COUNT: {count}")
        except Exception as e:
            print(f"PATH: {p} | ERROR: {e}")
    else:
        print(f"PATH: {p} | NOT EXISTS")
