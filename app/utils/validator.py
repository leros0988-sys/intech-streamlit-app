import pandas as pd

REQUIRED_COLUMNS = [
    "일자", "기관명", "SETTLE_ID",
    "발송건수", "열람건수", "인증건수"
]


def validate_uploaded_df(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        return False, f"필수 컬럼 누락: {', '.join(missing)}"
    return True, "OK"
