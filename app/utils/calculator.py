# app/utils/calculator.py

import pandas as pd


def calculate_settlement(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    현재 버전: 업로드된 통합 데이터 그대로 반환.
    나중에 필요하면 여기서 금액 계산/가공 로직을 추가하면 됨.
    """
    if raw_df is None or raw_df.empty:
        raise RuntimeError("정산 대상 데이터가 없습니다.")
    return raw_df.copy()


def summarize_by_settle_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    기안용 요약:
      - 기관명, SETTLE_ID 기준으로
      - 발송건수 / 인증건수 / 총금액(또는 금액) 합계
    컬럼이 없다면 있는 것만 사용.
    """

    if df is None or df.empty:
        raise RuntimeError("요약할 데이터가 없습니다.")

    cols = df.columns
    group_cols = []
    if "기관명" in cols:
        group_cols.append("기관명")
    if "SETTLE_ID" in cols:
        group_cols.append("SETTLE_ID")

    if not group_cols:
        raise RuntimeError("기관명 / SETTLE_ID 컬럼이 없어 요약할 수 없습니다.")

    agg_dict = {}
    for c in ["발송건수", "인증건수", "총금액", "금액"]:
        if c in cols:
            agg_dict[c] = "sum"

    if not agg_dict:
        # 최소한 행 개수라도 세자
        agg_dict = {"발송건수": ("발송건수" if "발송건수" in cols else group_cols[0])}

    grouped = df.groupby(group_cols, as_index=False).agg(agg_dict)

    # '금액'만 있고 '총금액'이 없으면 이름 통일
    if "금액" in grouped.columns and "총금액" not in grouped.columns:
        grouped = grouped.rename(columns={"금액": "총금액"})

    return grouped
