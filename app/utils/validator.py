# app/utils/validator.py

from typing import Dict
import pandas as pd
from app.utils.file_reader import read_any_file

def validate_uploaded_files(files) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    파일명 → 시트명 → DF 구조로 반환.
    (upload_page가 요구하는 정확한 형태)
    """

    validated: Dict[str, Dict[str, pd.DataFrame]] = {}

    for f in files:
        name = f.name

        try:
            df = read_any_file(f)

            if df is None or not isinstance(df, pd.DataFrame) or df.empty:
                raise ValueError("유효한 데이터가 아님")

            # ✔ 하나의 파일을 "단일 시트" 형태로 묶어서 반환
            validated[name] = { "Sheet1": df }

        except Exception as e:
            print(f"[validator] '{name}' 읽기 실패: {e}")
            continue

    return validated
