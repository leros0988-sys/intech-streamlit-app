import json
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
SETTINGS_FILE = BASE / "settings.json"


# -----------------------------
# SETTINGS LOAD/SAVE
# -----------------------------
def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(data: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# -----------------------------
# 요율표 / 기관DB 로드
# -----------------------------
def load_rate_table():
    settings = load_settings()
    path = settings.get("rate_table_path", None)

    if not path:
        raise FileNotFoundError("settings.json에 'rate_table_path' 없음")

    excel_path = BASE / Path(path).name
    if not excel_path.exists():
        raise FileNotFoundError(f"요율표 파일 없음: {excel_path}")

    return pd.read_excel(excel_path)


def load_partner_db():
    settings = load_settings()
    path = settings.get("partner_db_path", None)

    if not path:
        raise FileNotFoundError("settings.json에 'partner_db_path' 없음")

    excel_path = BASE / Path(path).name
    if not excel_path.exists():
        raise FileNotFoundError(f"기관DB 파일 없음: {excel_path}")

    return pd.read_excel(excel_path)
