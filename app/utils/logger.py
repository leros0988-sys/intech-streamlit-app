# app/utils/logger.py

import os
from datetime import datetime

LOG_FILE = "app/logs/system.log"
os.makedirs("app/logs", exist_ok=True)

def write_log(user: str, action: str):
    """사용자 행동을 로그 텍스트 파일에 기록"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{timestamp}] ({user}) {action}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)


def read_logs() -> list:
    """저장된 로그 전체를 리스트로 반환"""
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]
