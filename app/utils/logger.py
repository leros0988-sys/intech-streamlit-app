# app/utils/logger.py

import os
from datetime import datetime

import pandas as pd

LOG_FILE = "app/utils/login_logs.csv"


def write_log(user: str, message: str) -> None:
    """로그인/관리 이벤트 간단 기록"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new = pd.DataFrame([[now, user, message]],
                       columns=["timestamp", "user", "message"])

    if os.path.exists(LOG_FILE):
        old = pd.read_csv(LOG_FILE)
        df = pd.concat([old, new], ignore_index=True)
    else:
        df = new

    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")


def load_login_logs() -> pd.DataFrame:
    """로그 CSV 로드 (없으면 빈 DF)"""
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame(columns=["timestamp", "user", "message"])
    return pd.read_csv(LOG_FILE)

