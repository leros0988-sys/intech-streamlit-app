import pandas as pd

def load_rate_table():
    return pd.read_excel("rate_table.xlsx")

def load_partner_db():
    return pd.read_excel("기관담당자DB.xlsx")

