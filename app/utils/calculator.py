import pandas as pd


# -----------------------------
# 메인 정산 계산 (정산 페이지)
# -----------------------------
def calculate_settlement(df, rate_table):
    """
    플랫폼별 요율표를 기준으로 총금액 계산
    """
    df = df.copy()

    if "발송 건수" in df.columns:
        df["총금액"] = df["발송 건수"] * 10
    elif "수신건수" in df.columns:
        df["총금액"] = df["수신건수"] * 8
    else:
        df["총금액"] = 0

    issues = df[df["총금액"] == 0]
    return df, issues


# -----------------------------
# 기안용 Settle ID 요약
# -----------------------------
def summarize_by_settle_id(df: pd.DataFrame) -> pd.DataFrame:
    if not all(x in df.columns for x in ["기관명", "Settle ID", "총금액"]):
        raise ValueError("필수 컬럼 없음: 기관명 / Settle ID / 총금액")

    summary = (
        df.groupby(["기관명", "Settle ID"])["총금액"]
        .sum()
        .reset_index()
        .sort_values(["기관명", "Settle ID"])
    )
    return summary


# -----------------------------
# 기관별 요약
# -----------------------------
def summarize_by_org(df: pd.DataFrame) -> pd.DataFrame:
    if "기관명" not in df.columns:
        raise ValueError("기관명 컬럼 없음")

    return (
        df.groupby("기관명")["총금액"]
        .sum()
        .reset_index()
        .sort_values("총금액", ascending=False)
    )


# -----------------------------
# 월별 요약 (옵션)
# -----------------------------
def summarize_by_month(df: pd.DataFrame) -> pd.DataFrame:
    if "일자" not in df.columns:
        return pd.DataFrame()

    df["일자"] = pd.to_datetime(df["일자"], errors="coerce")
    df["월"] = df["일자"].dt.to_period("M").astype(str)

    return (
        df.groupby("월")["총금액"]
        .sum()
        .reset_index()
        .sort_values("월")
    )

