from pathlib import Path   # ★★★ 반드시 필요 — NameError 해결 ★★★
import csv
from datetime import datetime

# 로그 파일을 utils 폴더 내부에 자동 생성
LOG_FILE = Path(__file__).parent / "login_logs.csv"

def write_log(username: str, event: str):
    """로그 기록"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = LOG_FILE.exists()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # 첫 생성 시 헤더 넣기
        if not file_exists:
            writer.writerow(["timestamp", "username", "event"])

        writer.writerow([now, username, event])
