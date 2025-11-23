import json
import os
import pandas as pd
import streamlit as st

SETTINGS_FILE = "app/utils/settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

def load_rate_table():
    settings = load_settings()
    path = settings.get("rate_table_path")
    if not os.path.exists(path):
        st.error(f"요율표 파일이 없습니다: {path}")
        return None
    return pd.read_excel(path)

def load_partner_db():
    settings = load_settings()
    path = settings.get("partner_db_path")
    if not os.path.exists(path):
        st.error(f"기관 담당자 DB 파일이 없습니다: {path}")
        return None
    return pd.read_excel(path)


