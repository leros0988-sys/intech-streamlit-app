from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent / "system.log"


def write_log(user, action):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {user}: {action}\n")
