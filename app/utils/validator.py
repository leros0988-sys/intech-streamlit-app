# app/utils/validator.py

from typing import Dict
import pandas as pd
from app.utils.file_reader import read_any_file


def validate_uploaded_files(files) -> Dict[str, Dict[str, pd.DataFrame]]:
    """
    파일 여러 개 업로드 → 시트 → df 구조를 통일
    return = { "파일명": { "Sheet1": df } }
    """

    result = {}

    for f in files:
        name = f.name

        try:
            df = read_any_file(f)

            if isinstance(df, pd.DataFrame) and not df.empty:
                result[name] = {"Sheet1": df}
            else:
                print(f"[validator] {name} 무효 (empty or wrong type)")

        except Exception as e:
            print(f"[validator] {name} 오류: {e}")
            continue

    return result
