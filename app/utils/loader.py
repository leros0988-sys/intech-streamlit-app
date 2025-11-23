import json
import os
import pandas as pd

SETTINGS_PATH = os.path.join("app", "utils", "settings.json")


def load_settings() -> dict:
    if not os.path.exists(SETTINGS_PATH):
        return {
            "main_image": "app/images/default_usagi_kuma.png",
            "youtube_url": "https://youtu.be/0f2x_3zlz4I",
            "max_login_fail": 5,
            "auto_logout_minutes": 30,
            "rate_table_path": "app/utils/rate_table.xlsx",
            "partner_db_path": "app/utils/partner_db.xlsx",
        }
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(settings: dict):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def load_rate_table() -> pd.DataFrame:
    settings = load_settings()
    path = settings.get("rate_table_path", "app/utils/rate_table.xlsx")
    return pd.read_excel(path)


def load_partner_db() -> pd.DataFrame:
    settings = load_settings()
    path = settings.get("partner_db_path", "app/utils/partner_db.xlsx")
    return pd.read_excel(path)
