import pandas as pd
import io

def read_any_file(uploaded_file):
    """엑셀/CSV 자동 판별해서 DataFrame으로 반환. 실패 시 None."""
    file_bytes = uploaded_file.read()

    # 1) 엑셀 시도
    try:
        df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        return df
    except:
        pass

    # 2) CSV UTF-8 시도
    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8")
        return df
    except:
        pass

    # 3) CSV CP949 시도
    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="cp949")
        return df
    except:
        pass

    return None
