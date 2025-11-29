import pandas as pd
import json
import os

def load_settings(path="app/utils/settings.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_partner_db():
    path = "app/utils/기관담당자DB.xlsx"
    return pd.read_excel(path)
