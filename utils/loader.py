import pandas as pd

def load_rate_table():
    try:
        return pd.read_excel("rate_table.xlsx")
    except Exception as e:
        raise ValueError(f"요율표(rate_table.xlsx) 불러오기 실패: {e}")

def load_partner_db():
    try:
        return pd.read_excel("기관 담당자 정보 DB.xlsx")
    except Exception as e:
        raise ValueError(f"기관 담당자 DB 불러오기 실패: {e}")


