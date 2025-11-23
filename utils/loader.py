# utils/loader.py
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def load_rate_table():
    """rate_table.xlsx 로드"""
    path = os.path.join(BASE_DIR, "rate_table.xlsx")

    if not os.path.exists(path):
        raise FileNotFoundError(f"요율표 파일이 없습니다: {path}")

    return pd.read_excel(path)

def load_partner_db():
    """기관담당자DB.xlsx 로드"""
    path = os.path.join(BASE_DIR, "기관담당자DB.xlsx")

    if not os.path.exists(path):
        raise FileNotFoundError(f"기관 DB 파일이 없습니다: {path}")

    return pd.read_excel(path)
