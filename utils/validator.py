import pandas as pd


def validate_uploaded_files(df: pd.DataFrame) -> list[str]:
    """
    업로드된 정산 엑셀 파일의 기본 구조 검증.
    문제가 있을 경우 경고 메시지 리스트를 반환한다.
    """
    warnings: list[str] = []

    if df is None or df.empty:
        warnings.append("엑셀 데이터가 비어 있습니다.")
        return warnings

    # 카카오 settle id 컬럼 필수
    if "카카오 settle id" not in df.columns:
        warnings.append("'카카오 settle id' 컬럼을 찾을 수 없습니다. (카카오 기준 정산서 집계 불가)")

    # 금액 관련 필수 컬럼 체크
    if not any(col in df.columns for col in ["금액", "청구금액", "정산금액", "합계"]):
        warnings.append("금액 관련 컬럼(금액/청구금액/정산금액/합계)을 찾을 수 없습니다.")

    return warnings
