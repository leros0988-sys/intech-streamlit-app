import json
import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parent
SETTINGS = BASE / "settings.json"

with open(SETTINGS, "r", encoding="utf-8") as f:
    cfg = json.load(f)


def load_rate_table():
    path = BASE / Path(cfg["rate_table_path"]).name
    if not path.exists():
        raise FileNotFoundError(f"요율표 없음: {path}")
    return pd.read_excel(path)


def load_partner_db():
    path = BASE / Path(cfg["partner_db_path"]).name
    if not path.exists():
        raise FileNotFoundError(f"기관DB 없음: {path}")
    return pd.read_excel(path)
