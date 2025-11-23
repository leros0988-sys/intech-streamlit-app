import pandas as pd

def calculate_partner_fee(kakao_df, kt_df, rate_db):
    """협력사 정산 계산"""

    # 두 업체 데이터 합치기
    df = pd.concat([kakao_df, kt_df], ignore_index=True)

    # 요율 테이블과 매칭
    df = df.merge(rate_db, how="left", on="기관명")

    # 금액 계산
    df["총금액"] = df["발송건수"] * df["요율"]

    return df

