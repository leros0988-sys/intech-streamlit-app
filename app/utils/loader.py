# app/utils/loader.py

import json
from pathlib import Path
import pandas as pd


# ----------------------------------------
# 🔵 Base Path 설정
# ----------------------------------------
# Streamlit Cloud / 로컬 모두에서 문제 없이 동작하도록
BASE_DIR = Path(__file__).resolve().parent.parent  # app/
UTILS_DIR = BASE_DIR / "utils"

SETTINGS_FILE = UTILS_DIR / "settings.json"
PARTNER_DB_FILE = UTILS_DIR / "partner_db.xlsx"


# ----------------------------------------
# 🔵 settings.json 로드
# ----------------------------------------
def load_settings() -> dict:
    """settings.json 읽기 (없으면 기본값 반환)"""

    default_settings = {
        "welcome_text": "환영합니다! 아이앤텍 전자고지 정산 대시보드입니다.",
        "login_fail_limit": 5,
        "main_image": "app/images/imagesusagi_kuma.png",
        "youtube_url": "",
    }

    if not SETTINGS_FILE.exists():
        return default_settings

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return {**default_settings, **data}  # 기본값 + 사용자 설정 덮어쓰기
    except Exception:
        return default_settings


# ----------------------------------------
# 🔵 settings.json 저장
# ----------------------------------------
def save_settings(data: dict) -> None:
    """settings.json 저장"""
    SETTINGS_FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


# ----------------------------------------
# 🔵 기관 담당자 DB 로드
# ----------------------------------------
def load_partner_db() -> pd.DataFrame:
    """
    partner_db.xlsx 로드.
    파일 없으면 빈 데이터프레임 반환.
    """
    if not PARTNER_DB_FILE.exists():
        return pd.DataFrame(columns=["기관명", "담당자", "연락처"])

    try:
        return pd.read_excel(PARTNER_DB_FILE)
    except Exception as e:
        raise RuntimeError(f"기관 담당자 DB 로드 오류: {e}")
