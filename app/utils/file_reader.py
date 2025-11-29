# app/utils/file_reader.py

import pandas as pd
from io import BytesIO
import warnings


def read_any_file(uploaded_file):
    """
    어떤 형식(xlsx, xls, csv)이 와도 반드시 DataFrame 반환.
    - openpyxl 스타일 오류 무시
    - csv utf-8 → cp949 fallback
    """

    file_bytes = uploaded_file.read()
    data = BytesIO(file_bytes)

    # 1) Excel 시도
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(data, dtype=str, engine="openpyxl")
        return df
    except Exception as e:
        print(f"[read_any_file] openpyxl 실패: {e}")

    data.seek(0)

    # 2) CSV utf-8
    try:
        df = pd.read_csv(data, dtype=str, encoding="utf-8-sig")
        return df
    except Exception as e:
        print(f"[read_any_file] CSV utf-8 실패: {e}")

    data.seek(0)

    # 3) CSV cp949
    try:
        df = pd.read_csv(data, dtype=str, encoding="cp949")
        return df
    except Exception as e:
        print(f"[read_any_file] CSV cp949 실패: {e}")

    raise RuntimeError("❌ 파일을 읽을 수 없습니다.")
