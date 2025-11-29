import pandas as pd

def summarize_by_settle_id(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame()

    grouped = df.groupby(["SETTLE_ID", "기관명"], as_index=False).agg({
        "발송건수": "sum",
        "열람건수": "sum",
        "인증건수": "sum"
    })

    grouped["정산금액"] = grouped["인증건수"] * 20
    return grouped


# ------------------------------
# 개별 통계 (옵션)
# ------------------------------
def summarize_kakao(df):
    if df.empty:
        return df
    return df.groupby("일자", as_index=False).sum()


def summarize_kt(df):
    if df.empty:
        return df
    return df.groupby("일자", as_index=False).sum()


def summarize_naver(df):
    if df.empty:
        return df
    return df.groupby("일자", as_index=False).sum()


