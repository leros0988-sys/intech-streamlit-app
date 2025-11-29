# app/utils/loader.py

import json
from pathlib import Path
import pandas as pd

BASE = Path("app")
SETTINGS_FILE = BASE / "utils" / "settings.json"
PARTNER_DB_FILE = BASE / "utils" / "partner_db.xlsx"


def load_settings() -> dict:
    """settings.json 읽기 (없으면 기본값 반환)"""
    if not SETTINGS_FILE.exists():
        return {
            "welcome_text": "환영합니다!",
            "login_fail_limit": 5,
        }
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        # 깨진 경우 기본값
        return {
            "welcome_text": "환영합니다!",
            "login_fail_limit": 5,
        }


def save_settings(data: dict) -> None:
    """settings.json 저장"""
    SETTINGS_FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )


def load_partner_db() -> pd.DataFrame:
    """기관 담당자 DB 엑셀 로드"""
    try:
        return pd.read_excel(PARTNER_DB_FILE)
    except Exception as e:
        raise RuntimeError(f"기관 담당자 DB 로드 오류: {e}")
