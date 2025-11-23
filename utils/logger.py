import csv
from datetime import datetime
from pathlib import Path   # ← ← ← ★★★ 여기가 없어서 NameError 난 거임

LOG_FILE = Path("login_logs.csv")


def write_log(username: str, event: str):
    """로그 파일에 기록"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 파일이 없으면 헤더 자동 생성
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
