import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일 기준
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
LOG_FILE = os.path.join(LOG_DIR, "system.log")

os.makedirs(LOG_DIR, exist_ok=True)

def write_log(user: str, action: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] ({user}) {action}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def read_logs() -> list:
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]
