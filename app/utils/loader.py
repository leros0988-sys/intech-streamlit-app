import json
import pandas as pd


# --------------------------------------------
# settings.json 읽기
# --------------------------------------------
def load_settings(path="app/utils/settings.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


# --------------------------------------------
# settings.json 저장하기 (import 에러 방지 목적)
# --------------------------------------------
def save_settings(settings: dict, path="app/utils/settings.json"):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)
    except:
        pass


# --------------------------------------------
# 기관 담당자 DB 불러오기
# --------------------------------------------
def load_partner_db(path="app/utils/기관담당자DB.xlsx"):
    return pd.read_excel(path)
