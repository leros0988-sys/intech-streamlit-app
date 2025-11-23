import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SETTINGS_FILE = BASE_DIR / "settings.json"
RATE_TABLE_FILE = BASE_DIR / "rate_table.xlsx"
PARTNER_DB_FILE = BASE_DIR / "partner_db.xlsx"


def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        default = {
            "main_image": "default_usagi_kuma.png",
            "youtube_url": "https://youtu.be/0f2x_3zlz4I",
            "auto_logout_minutes": 30,
            "max_login_fail": 5,
        }
        save_settings(default)
        return default

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(data: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_rate_table() -> pd.DataFrame:
    return pd.read_excel(RATE_TABLE_FILE)


def load_partner_db() -> pd.DataFrame:
    return pd.read_excel(PARTNER_DB_FILE)
