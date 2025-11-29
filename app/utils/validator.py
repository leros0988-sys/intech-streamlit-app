# app/utils/validator.py

from typing import Dict
import pandas as pd
from app.utils.file_reader import read_any_file

def validate_uploaded_files(files) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    결과 형태: {
        "파일명.xlsx": {
            "Sheet1": df,
            "Sheet2": df2,
        }
    }
    """

    validated = {}

    for f in files:
        name = f.name

        try:
            sheet_dict = read_any_file(f)

            # dict 형태가 아니면 실패 처리
            if not isinstance(sheet_dict, dict):
                raise ValueError("dict(sheet_name → DF) 형태가 아님")

            # 모든 시트 검증
            clean_dict = {}
            for sheet, df in sheet_dict.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    clean_dict[sheet] = df

            if not clean_dict:
                raise ValueError("유효한 시트가 없음")

            validated[name] = clean_dict

        except Exception as e:
            print(f"[validator] {name} 실패: {e}")
            continue

    return validated
