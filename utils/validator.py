import pandas as pd


def validate_uploaded_df(df: pd.DataFrame) -> list[str]:
    """
    업로드된 정산 엑셀에 대해 간단 검증.
    문제가 있으면 경고 메시지 리스트 반환.
    """
    warnings: list[str] = []

    if df is None or df.empty:
        warnings.append("엑셀 데이터가 비어 있습니다.")

    # 카카오 settle id 컬럼이 없는 경우
    if "카카오 settle id" not in df.columns:
        warnings.append("'카카오 settle id' 컬럼을 찾을 수 없습니다. (카카오 기준 정산서 집계 불가)")

    # 기본 금액 컬럼 체크
    if not any(col in df.columns for col in ["금액", "청구금액", "정산금액", "합계"]):
        warnings.append("금액 관련 컬럼(금액/청구금액/정산금액/합계)을 찾을 수 없습니다.")

    return warnings
