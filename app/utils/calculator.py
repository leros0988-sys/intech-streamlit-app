import pandas as pd


def summarize_kakao(df: pd.DataFrame) -> pd.DataFrame:
    """
    카카오 정산 간단 집계:
    - 카카오 settle id 별 건수 및 금액 합계
    """
    if "카카오 settle id" not in df.columns:
        return pd.DataFrame()

    # 금액 컬럼 탐색
    amount_col = None
    for cand in ["금액", "청구금액", "정산금액", "합계"]:
        if cand in df.columns:
            amount_col = cand
            break

    group_cols = ["카카오 settle id"]
    agg_dict = {"카카오 settle id": "count"}
    if amount_col:
        agg_dict[amount_col] = "sum"

    grouped = df.groupby("카카오 settle id", dropna=True).agg(agg_dict).rename(
        columns={"카카오 settle id": "건수"}
    )

    grouped = grouped.reset_index()
    if amount_col:
        grouped = grouped.rename(columns={amount_col: "금액합계"})

    return grouped


def filter_by_channel(df: pd.DataFrame, keyword: str) -> pd.DataFrame:
    """
    '중계자/채널/발송채널' 컬럼에서 keyword를 포함하는 행만 필터링.
    keyword: '카카오', 'KT', '네이버' 등
    """
    channel_col = None
    for cand in ["중계자", "채널", "발송채널", "중계사"]:
        if cand in df.columns:
            channel_col = cand
            break

    if channel_col is None:
        return pd.DataFrame()

    return df[df[channel_col].astype(str).str.contains(keyword, na=False)]

