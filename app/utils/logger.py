import csv
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "login_logs.csv"

def write_log(username: str, event: str):
    """
    로그인 성공/실패 기록
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = LOG_FILE.exists()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "username", "event"])
        writer.writerow([now, username, event])
