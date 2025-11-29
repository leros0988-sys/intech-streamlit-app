# app/utils/validator.py

import pandas as pd
from .file_reader import read_any_file


def validate_uploaded_files(uploaded_files):
    """
    여러 개 업로드된 파일을 읽어서 {파일명: DataFrame} 딕셔너리로 반환.
    """
    validated: dict[str, pd.DataFrame] = {}

    for f in uploaded_files:
        df = read_any_file(f)
        if df is None or df.empty:
            continue
        validated[f.name] = df

    if not validated:
        raise RuntimeError("업로드된 파일에서 유효한 데이터를 찾지 못했습니다.")

    return validated


def validate_uploaded_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    예전에 쓰던 인터페이스 호환용(단일 DF 검증).
    지금은 특별한 검증은 하지 않고 그대로 반환.
    """
    if df is None or df.empty:
        raise RuntimeError("업로드된 데이터가 비어 있습니다.")
    return df
