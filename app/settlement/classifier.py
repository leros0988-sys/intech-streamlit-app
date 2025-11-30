import pandas as pd

# -------------------------------------------------------
# 회사 / 유형 자동 분류
# -------------------------------------------------------

def detect_company(df: pd.DataFrame) -> str:
    """
    엑셀 컬럼만 보고 카카오 / KT / 네이버 / 다수기관 자동 판별
    """

    cols = set(df.columns)

    # 카카오 패턴
    kakao_keys = {
        "앱 ID", "알림 수신 건수", "열람 시 인증 건수", "OTT검증 건수",
        "D10_2", "D11_2", "D10_2T", "D11_2T"
    }

    # KT 패턴
    kt_keys = {
        "발송요청건", "수신건수", "열람건수", "맵핑건수",
        "xMS열람건", "rcs열람건"
    }

    # 네이버 패턴
    naver_keys = {"발송건수", "열람건수"}

    # 다수기관 PDF 구성용 패턴 (너의 대금청구서 파일)
    multi_keys = {"기관명", "Settle ID", "청구금액", "요율"}

    # -------------------------
    # 회사 판별
    # -------------------------
    if len(kakao_keys & cols) >= 2:
        return "kakao"

    if len(kt_keys & cols) >= 2:
        return "kt"

    if len(naver_keys & cols) >= 1:
        return "naver"

    if len(multi_keys & cols) >= 2:
        return "multi"

    # 기본값 (안전)
    return "unknown"


def classify_uploaded_files(data_map: dict):
    """
    {파일명: DF} -> [{filename, df, company}] 리스트 반환
    """

    results = []

    for fname, df in data_map.items():
        company = detect_company(df)
        results.append(
            {
                "filename": fname,
                "company": company,
                "df": df,
            }
        )

    return results
