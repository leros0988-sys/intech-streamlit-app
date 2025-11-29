# app/utils/validator.py

from typing import Dict
import pandas as pd
from app.utils.file_reader import read_any_file


def validate_uploaded_files(files) -> Dict[str, pd.DataFrame]:
    """
    업로드된 파일들을 안전하게 읽어 DataFrame만 반환하는 검증기.
    - 파일 하나라도 실패하면 해당 파일은 제외
    - None, 빈 DF 절대 허용하지 않음
    - 항상 dict[str, DataFrame] 형태로만 반환
    """

    validated = {}

    for f in files:
        name = f.name

        try:
            df = read_any_file(f)

            # 완전 무결성 검증
            if df is None:
                raise ValueError("None 반환됨")

            if not isinstance(df, pd.DataFrame):
                raise ValueError("DataFrame이 아님")

            if df.empty:
                raise ValueError("빈 파일")

            validated[name] = df

        except Exception as e:
            print(f"[validator] '{name}' 읽기 실패: {e}")
            # 실패한 파일은 절대 validated에 넣지 않는다.
            continue

    return validated
