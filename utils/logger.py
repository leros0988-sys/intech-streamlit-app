print("🔥 logger.py loaded")
import csv
from datetime import datetime
from pathlib import Path   # ★★★ 여기 추가해야 NameError가 사라짐 ★★★

LOG_FILE = Path("login_logs.csv")


def write_log(username: str, event: str):
    """로그 기록"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = LOG_FILE.exists()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["timestamp", "username", "event"])

        writer.writerow([now, username, event])


def read_logs():
    """로그 전체 읽기"""
    if not LOG_FILE.exists():
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)
