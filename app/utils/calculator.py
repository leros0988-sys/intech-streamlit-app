# app/utils/calculator.py

import pandas as pd

def summarize_settle(df: pd.DataFrame) -> pd.DataFrame:
    """
    정산 업로드된 모든 엑셀을 병합한 raw_df를 받아
    기관명 / SETTLE ID / 발송건수 / 인증건수 / 금액 등을 요약해주는 함수
    """

    # 필수 컬럼 체크
    required = ["기관명", "SETTLE_ID", "발송건수", "인증건수", "금액"]
    for col in required:
        if col not in df.columns:
            df[col] = 0   # 없으면 0으로 생성 (에러 방지)

    # SETTLE ID 기준 집계
    grouped = (
        df.groupby(["기관명", "SETTLE_ID"], dropna=False)[
            ["발송건수", "인증건수", "금액"]
        ]
        .sum()
        .reset_index()
    )

    return grouped
