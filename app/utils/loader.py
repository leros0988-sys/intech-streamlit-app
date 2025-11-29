import json
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

SETTINGS_FILE = BASE / "utils" / "settings.json"
PARTNER_FILE = BASE / "utils" / "partner_db.xlsx"
RATE_FILE = BASE / "utils" / "rate_table.xlsx"


def load_settings():
    if not SETTINGS_FILE.exists():
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(data: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_partner_db():
    if PARTNER_FILE.exists():
        return pd.read_excel(PARTNER_FILE)
    return pd.DataFrame()


def load_rate_table():
    if RATE_FILE.exists():
        return pd.read_excel(RATE_FILE)
    return pd.DataFrame()
