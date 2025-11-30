import pandas as pd


# -------------------------------------------------------
# 1) 업로드된 "정산용 대금청구서" 파일에서 기관 목록 추출
# -------------------------------------------------------

def extract_settle_ids_from_multi(df: pd.DataFrame):
    """
    대금청구서(다수기관) 파일에서 기관명 / Settle ID 목록 추출
    """
    cols = df.columns

    org_col = None
    sid_col = None

    # 기관명 찾기
    for c in ["기관명", "기관", "organization"]:
        if c in cols:
            org_col = c
            break

    # Settle ID 찾기
    for c in ["Settle ID", "SETTLE_ID", "settle_id"]:
        if c in cols:
            sid_col = c
            break

    if org_col is None or sid_col is None:
        raise RuntimeError("대금청구서 파일에서 기관명 또는 Settle ID가 없습니다.")

    base_df = df[[org_col, sid_col]].copy()
    base_df.columns = ["기관명", "SettleID"]

    base_df["기관명"] = base_df["기관명"].astype(str).str.strip()
    base_df["SettleID"] = base_df["SettleID"].astype(str).str.strip()

    base_df = base_df[base_df["기관명"] != ""]
    base_df = base_df[base_df["SettleID"] != ""]

    return base_df


# -------------------------------------------------------
# 2) 카카오 통계 파일에서 기관명 / Settle ID 가져오기
# -------------------------------------------------------

def extract_settle_ids_from_kakao(df: pd.DataFrame):
    """
    카카오 통계 파일에서 기관명 / Settle ID 목록 생성
    """

    cols = df.columns
    org_col = None
    sid_col = None

    for c in ["기관명", "사업자명", "기관"]:
        if c in cols:
            org_col = c
            break

    for c in ["SETTLE_ID", "Settle ID", "settle_id"]:
        if c in cols:
            sid_col = c
            break

    if org_col is None:
        raise RuntimeError("카카오 통계 파일에서 기관명을 찾을 수 없습니다.")

    # Settle ID 없는 경우도 있으므로 예외 처리
    if sid_col is None:
        out = df[[org_col]].copy()
        out.columns = ["기관명"]
        out["SettleID"] = ""
        return out

    out = df[[org_col, sid_col]].copy()
    out.columns = ["기관명", "SettleID"]

    out["기관명"] = out["기관명"].astype(str).strip()
    out["SettleID"] = out["SettleID"].astype(str).strip()

    return out


# -------------------------------------------------------
# 3) 누락 기관 계산
# -------------------------------------------------------

def find_missing_settle_ids(base_df, kakao_df):
    """
    대금청구서 기반 기관 목록 vs 카카오 통계 기관 목록 비교
    """

    base_names = set(base_df["기관명"])
    kakao_names = set(kakao_df["기관명"])

    missing = base_names - kakao_names  # 누락된 기관

    miss_df = base_df[base_df["기관명"].isin(missing)].copy()

    return miss_df
