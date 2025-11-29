import pandas as pd
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent
LOG_FILE = BASE / "utils" / "login_logs.csv"


def write_log(user, action="login"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = pd.DataFrame([{"time": now, "user": user, "action": action}])

    if LOG_FILE.exists():
        old = pd.read_csv(LOG_FILE)
        df = pd.concat([old, record], ignore_index=True)
    else:
        df = record

    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")


def load_login_logs():
    if LOG_FILE.exists():
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame()
