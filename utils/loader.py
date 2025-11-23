import json
import os
import pandas as pd

SETTINGS_FILE = "settings.json"


def load_settings():
    """settings.json 로드 (없으면 기본값 생성)"""
    if not os.path.exists(SETTINGS_FILE):
        default_settings = {
            "main_image_path": "app/images/imagesusagi_kuma.png",
            "youtube_url": "https://youtu.be/0f2x_3zlz4I",
            "dashboard_text": "전자고지 발송, 관리, 정산 기능을 보다 쉽게 사용할 수 있도록 제작되었습니다.",
            "rate_table_path": "rate_table.xlsx",
            "partner_db_path": "partner_db.xlsx",
            "auto_logout_minutes": 30,
            "login_fail_limit": 5,
        }
        save_settings(default_settings)
        return default_settings

    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_settings(data: dict):
    """settings.json 저장"""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_rate_table(path: str | None = None):
    """요율표 엑셀 로드"""
    settings = load_settings()
    file_path = path or settings.get("rate_table_path", "rate_table.xlsx")

    if not os.path.exists(file_path):
        return None

    return pd.read_excel(file_path)


def load_partner_db(path: str | None = None):
    """기관 담당자 DB 로드"""
    settings = load_settings()
    file_path = path or settings.get("partner_db_path", "partner_db.xlsx")

    if not os.path.exists(file_path):
        return None

    return pd.read_excel(file_path)

