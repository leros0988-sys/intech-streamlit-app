import csv
from datetime import datetime
from pathlib import Path
import pandas as pd

# login_logs.csv 파일 경로
LOG_FILE = Path(__file__).resolve().parent.parent / "login_logs.csv"


def write_log(username: str, event: str):
    """로그인 성공/실패 기록"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = LOG_FILE.exists()

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "username", "event"])
        writer.writerow([now, username, event])


def load_login_logs() -> pd.DataFrame:
    """CSV 읽어서 DataFrame 형태로 반환"""
    if not LOG_FILE.exists():
        # 파일 없으면 빈 DataFrame 반환
        return pd.DataFrame(columns=["timestamp", "username", "event"])

    try:
        return pd.read_csv(LOG_FILE, encoding="utf-8")
    except Exception:
        return pd.DataFrame(columns=["timestamp", "username", "event"])
