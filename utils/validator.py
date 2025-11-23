import pandas as pd

def validate_uploaded_files(kakao_df, kt_df):
    """카카오/KT 업로드 파일 기본 검증"""

    errors = []

    # 1) 빈 파일
    if kakao_df.empty:
        errors.append("카카오 업로드 파일이 비어 있습니다.")
    if kt_df.empty:
        errors.append("KT 업로드 파일이 비어 있습니다.")

    # 2) 필드 확인
    required_cols = ["기관명", "담당자", "발송건수"]

    for col in required_cols:
        if col not in kakao_df.columns:
            errors.append(f"카카오 파일에 '{col}' 컬럼 없음")
        if col not in kt_df.columns:
            errors.append(f"KT 파일에 '{col}' 컬럼 없음")

    return errors

