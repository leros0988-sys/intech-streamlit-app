import pandas as pd

def read_excel_safely(file):
    try:
        return pd.read_excel(file)
    except:
        return pd.DataFrame()
