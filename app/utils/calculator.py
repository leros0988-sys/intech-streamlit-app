import pandas as pd

def summarize_by_settle_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    카카오 settle id 기준으로 집계
    """
    if "카카오 settle id" not in df.columns:
        return pd.DataFrame()

    summary = df.groupby("카카오 settle id").size().reset_index(name="건수")
    return summary


def calculate_settlement(df: pd.DataFrame) -> pd.DataFrame:
    """
    기본 정산 계산 로직 (총 건수 + 총 금액)
    """
    money_cols = ["정산금액", "청구금액", "합계", "금액"]

    money_col = None
    for col in money_cols:
        if col in df.columns:
            money_col = col
            break

    if money_col is None:
        df["금액(자동)"] = 0
        money_col = "금액(자동)"

    total_amount = df[money_col].sum()
    total_count = len(df)

    summary = pd.DataFrame({
        "총 건수": [total_count],
        "총 금액": [total_amount]
    })
    return summary
