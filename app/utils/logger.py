import pandas as pd
from datetime import datetime
import os

LOG_PATH = "app/utils/login_logs.csv"


def write_log(user, msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_row = pd.DataFrame(
        [[now, user, msg]],
        columns=["timestamp", "user", "message"]
    )

    if os.path.exists(LOG_PATH):
        old = pd.read_csv(LOG_PATH)
        df = pd.concat([old, new_row], ignore_index=True)
    else:
        df = new_row

    df.to_csv(LOG_PATH, index=False, encoding="utf-8-sig")


def load_login_logs():
    if not os.path.exists(LOG_PATH):
        return pd.DataFrame(columns=["timestamp", "user", "message"])

    return pd.read_csv(LOG_PATH)
