import json
import pandas as pd

SETTINGS_PATH = "app/settings.json"
PARTNER_DB_PATH = "app/utils/기관담당자DB.xlsx"


def load_settings():
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {
            "login_fail_limit": 5
        }


def save_settings(data: dict):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_partner_db():
    try:
        df = pd.read_excel(PARTNER_DB_PATH)
        return df
    except Exception as e:
        raise RuntimeError(f"기관 담당자 DB 로드 오류: {e}")
