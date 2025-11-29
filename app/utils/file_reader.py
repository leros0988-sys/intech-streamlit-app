# app/utils/file_reader.py

import pandas as pd
from io import BytesIO
import warnings

def read_any_file(uploaded_file):
    """엑셀/CSV 어떤 파일이 와도 DataFrame으로 반환하는 안정 버전"""

    file_bytes = uploaded_file.read()
    data = BytesIO(file_bytes)

    # 1) openpyxl 시도
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(data, dtype=str, engine="openpyxl")
        return {"Sheet1": df}  # 반드시 dict 반환
    except Exception:
        pass

    data.seek(0)

    # 2) CSV utf-8
    try:
        df = pd.read_csv(data, dtype=str, encoding="utf-8-sig")
        return {"Sheet1": df}
    except Exception:
        pass

    data.seek(0)

    # 3) CSV cp949
    try:
        df = pd.read_csv(data, dtype=str, encoding="cp949")
        return {"Sheet1": df}
    except Exception:
        pass

    raise RuntimeError("❌ 파일을 읽을 수 없습니다 (엑셀/CSV 구조 손상).")

