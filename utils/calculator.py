import pandas as pd

def match_rate(data_df: pd.DataFrame, rate_df: pd.DataFrame):
    """
    data_df : 업로드된 정산 통계 DataFrame
    rate_df : 요율표(rate_table.xlsx)

    기준 컬럼 예시:
      data_df  : 기관명, 부서명, 문서명, 건수
      rate_df  : 기관명, 부서, 문서, 단가
    """

    merged = pd.merge(
        data_df,
        rate_df,
        left_on=["기관명", "부서명", "문서명"],
        right_on=["기관명", "부서", "문서"],
        how="left",
        suffixes=("", "_rate")
    )

    # 요율(단가) 못 찾은 행들
    issues = merged[merged["단가"].isna()].copy()

    # 정상 매칭된 행들
    ok = merged[~merged.index.isin(issues.index)].copy()

    return ok, issues


def calculate_settlement(data_df: pd.DataFrame, rate_df: pd.DataFrame):
    """
    결과:
      settled_df : 정상 계산이 끝난 행
      issues_df  : 요율 매칭 안 된 행 (특이사항 로그용)
    """

    ok, issues = match_rate(data_df, rate_df)

    if ok.empty:
        raise ValueError("요율표와 매칭되는 데이터가 없습니다. 기관명/부서명/문서명을 다시 확인해주세요.")

    ok["총금액"] = ok["건수"] * ok["단가"]

    return ok, issues
