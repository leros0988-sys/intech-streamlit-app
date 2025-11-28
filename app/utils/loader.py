import json
import pandas as pd
from pathlib import Path

# utils 폴더 경로
BASE_DIR = Path(__file__).resolve().parent

# settings.json 경로
SETTINGS_FILE = BASE_DIR / "settings.json"


# -----------------------------
# settings.json 읽기
# -----------------------------
def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# settings.json 저장
# -----------------------------
def save_settings(setting_dict: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(setting_dict, f, ensure_ascii=False, indent=4)


# -----------------------------
# 정산용 Excel DB 로드
# -----------------------------
def load_rate_table():
    settings = load_settings()
    path = settings.get("rate_table_path", None)

    if not path:
        raise FileNotFoundError("settings.json: rate_table_path 가 설정되지 않음")

    excel_path = BASE_DIR / Path(path).name
    if not excel_path.exists():
        raise FileNotFoundError(f"요율표 파일을 찾을 수 없습니다: {excel_path}")

    return pd.read_excel(excel_path)


def load_partner_db():
    settings = load_settings()
    path = settings.get("partner_db_path", None)

    if not path:
        raise FileNotFoundError("settings.json: partner_db_path 가 설정되지 않음")

    excel_path = BASE_DIR / Path(path).name
    if not excel_path.exists():
        raise FileNotFoundError(f"기관 담당자 DB 파일 없음: {excel_path}")

    return pd.read_excel(excel_path)
