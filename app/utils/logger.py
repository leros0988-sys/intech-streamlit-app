import csv
from datetime import datetime
from pathlib import Path

# utils 폴더 바로 아래에 login_logs.csv 생성
LOG_FILE = Path(__file__).resolve().parent / "login_logs.csv"


def write_log(username: str, event: str):
    """로그 기록 (성공/실패)"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = LOG_FILE.exists()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "username", "event"])
        writer.writerow([now, username, event])


def load_login_logs():
    """로그 파일 읽기"""
    if not LOG_FILE.exists():
        return []

    rows = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # 헤더 스킵
        for row in reader:
            rows.append(row)
    return rows
