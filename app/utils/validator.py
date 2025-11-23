import pandas as pd

def validate_uploaded_df(df: pd.DataFrame) -> list[str]:
    warnings = []

    if df is None or df.empty:
        warnings.append("엑셀 데이터가 비어 있습니다.")

    # 카카오 settle id 존재 여부
    if "카카오 settle id" not in df.columns:
        warnings.append("'카카오 settle id' 컬럼을 찾을 수 없습니다.")

    # 금액 관련 컬럼 체크
    money_cols = ["금액", "청구금액", "정산금액", "합계"]
    if not any(col in df.columns for col in money_cols):
        warnings.append("금액 관련 컬럼을 찾을 수 없습니다.")

    return warnings
