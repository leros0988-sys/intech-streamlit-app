import pandas as pd

def calculate_settlement(data_df, rate_df):
    """
    data_df : 업로드된 엑셀 (발송 건별 DataFrame)
    rate_df : 요율표 DataFrame
    """

    output = data_df.copy()

    # key 매칭: '기관명' + '부서명' + '문서명'
    merged = pd.merge(
        output,
        rate_df,
        left_on=["기관명", "부서명", "문서명"],
        right_on=["기관명", "부서", "문서"],
        how="left"
    )

    if merged.isnull().any().any():
        raise ValueError("단가표 매칭 실패: 요율 정보가 부족한 행이 있습니다.")

    # 금액 계산
    merged["총금액"] = merged["건수"] * merged["단가"]

    return merged

