import pandas as pd

# -------------------------------------------------------
# 1) 총 매출, 회사별 매출 계산
# -------------------------------------------------------

def calculate_revenue(all_processed_df: pd.DataFrame):
    """
    정산된 전체 DF 기준으로 총매출 & 회사별 매출 계산
    """

    df = all_processed_df.copy()

    # 총합
    total_revenue = df["총금액_표준"].sum()

    # 회사별
    company_sum = (
        df.groupby("정산회사")["총금액_표준"]
        .sum()
        .reset_index()
        .rename(columns={"총금액_표준": "매출"})
    )

    # 딕셔너리 형태로 반환
    revenue_dict = {
        "total_revenue": total_revenue,
        "company_revenue": {
            row["정산회사"]: row["매출"] for _, row in company_sum.iterrows()
        }
    }

    return revenue_dict


# -------------------------------------------------------
# 2) 기관별 매출 TOP3
# -------------------------------------------------------

def top3_revenue(all_processed_df: pd.DataFrame):
    """
    기관별 매출 기준 TOP3 계산
    """

    df = all_processed_df.copy()

    # 기관명 없으면 제외
    if "기관명" not in df.columns:
        return pd.DataFrame(columns=["기관명", "매출"])

    grouped = (
        df.groupby("기관명")["총금액_표준"]
        .sum()
        .reset_index()
        .rename(columns={"총금액_표준": "매출"})
        .sort_values("매출", ascending=False)
    )

    # TOP3 추출
    return grouped.head(3)


# -------------------------------------------------------
# 3) 지역 기반 추정 (선택적)
# -------------------------------------------------------

def guess_region(org_name: str):
    """
    기관명 기반 지역 추정: ○○시청, ○○군청, ○○도청 등
    """

    if "시청" in org_name:
        return org_name.replace("시청", "") + "시"
    if "군청" in org_name:
        return org_name.replace("군청", "") + "군"
    if "구청" in org_name:
        return org_name.replace("구청", "") + "구"
    if "도청" in org_name:
        return org_name.replace("도청", "") + "도"

    return "기타"


def revenue_by_region(all_processed_df: pd.DataFrame):
    """
    (옵션) 기안자료용 지역별 매출 집계
    """

    if "기관명" not in all_processed_df.columns:
        return pd.DataFrame(columns=["지역", "매출"])

    df = all_processed_df.copy()
    df["지역"] = df["기관명"].astype(str).apply(guess_region)

    return (
        df.groupby("지역")["총금액_표준"]
        .sum()
        .reset_index()
        .sort_values("총금액_표준", ascending=False)
        .rename(columns={"총금액_표준": "매출"})
    )


# -------------------------------------------------------
# 4) 기안자료 생성 (DataFrame 형태)
# -------------------------------------------------------

def create_draft_table(all_processed_df: pd.DataFrame):
    """
    기안자료용 요약 테이블 생성
    """

    total_rev = all_processed_df["총금액_표준"].sum()

    # 회사별 매출
    company_sum = (
        all_processed_df.groupby("정산회사")["총금액_표준"]
        .sum()
        .reset_index()
        .rename(columns={"총금액_표준": "매출"})
    )

    # 지역별 매출
    region_sum = revenue_by_region(all_processed_df)

    # 기관별 매출 상위 3
    top_df = top3_revenue(all_processed_df)

    return {
        "total_revenue": total_rev,
        "company_sum": company_sum,
        "region_sum": region_sum,
        "top3": top_df,
    }
