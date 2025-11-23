# utils/calculator.py
import pandas as pd

def calculate_partner_fee(df: pd.DataFrame) -> pd.DataFrame:
    """
    엑셀 원본(df)을 받아 정산 금액을 계산한 뒤
    정산 결과 DataFrame을 반환하는 함수.
    """

    # 예시 컬럼명 — 네 실제 엑셀 구조에 맞게 변경 가능
    # date, 기관명, 발송건수, 카카오비용, KT비용 …

    if "발송건수" not in df.columns:
        raise ValueError("엑셀 파일에 '발송건수' 컬럼이 없습니다.")

    # ===== 정산 로직 (예시) =====
    df["카카오비용"] = df["발송건수"] * 50
    df["KT비용"] = df["발송건수"] * 70
    df["합계"] = df["카카오비용"] + df["KT비용"]

    return df
