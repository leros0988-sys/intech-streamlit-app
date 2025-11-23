import pandas as pd

def summarize_by_settle_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    카카오 기준 SETTLE ID 별로 대금청구서 집계.
    금액 관련 컬럼 자동 탐지하여 합산.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    # 금액 컬럼 자동 탐색
    amount_cols = [c for c in df.columns if c in ["금액", "청구금액", "정산금액", "합계"]]
    if not amount_cols:
        raise ValueError("금액 관련 컬럼을 찾을 수 없습니다.")

    amount_col = amount_cols[0]

    if "카카오 settle id" not in df.columns:
        raise ValueError("카카오 settle id 컬럼이 없습니다.")

    grouped = df.groupby("카카오 settle id")[amount_col].sum().reset_index()
    grouped.rename(columns={amount_col: "총 청구금액"}, inplace=True)

    return grouped


def calculate_settlement(df: pd.DataFrame) -> dict:
    """
    정산 페이지에서 총 발송건수/총 금액 계산.
    (카카오 기반)
    """
    if df is None or df.empty:
        return {
            "총 정산건수": 0,
            "총 금액": 0
        }

    if "카카오 settle id" not in df.columns:
        return {
            "총 정산건수": 0,
            "총 금액": 0
        }

    summary = summarize_by_settle_id(df)

    total_count = len(summary)      # SETTLE ID 기준 건수
    total_amount = summary["총 청구금액"].sum()

    return {
        "총 정산건수": int(total_count),
        "총 금액": int(total_amount)
    }
