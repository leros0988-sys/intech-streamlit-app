# app/utils/file_reader.py

import pandas as pd


def read_any_file(file) -> pd.DataFrame:
    """
    업로드된 파일(엑셀/CSV)을 DataFrame으로 읽는다.
    accept_multiple_files용 공통 함수.
    """
    name = getattr(file, "name", "") or ""

    lower = name.lower()
    try:
        if lower.endswith(".csv"):
            return pd.read_csv(file)
        elif lower.endswith(".xls") or lower.endswith(".xlsx"):
            return pd.read_excel(file)
        else:
            # 확장자 못 알아도 엑셀로 시도
            return pd.read_excel(file)
    except Exception as e:
        raise RuntimeError(f"{name} 파일 읽기 실패: {e}")
