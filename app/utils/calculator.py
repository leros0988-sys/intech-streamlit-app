import pandas as pd

def _normalize_rate_db(rate_db: pd.DataFrame) -> pd.DataFrame:
    """
    요율표 컬럼 이름을 정규화.
    기관명 / 부서명 / 문서명 / 중계자 / 발송단가 / 인증단가 로 통일.
    """
    rename_map = {
        "기관명": ["기관명", "이용기관명", "고객명"],
        "부서명": ["부서명", "부서", "서식", "서식명"],
        "문서명": ["문서명", "문서", "서식명"],
        "중계자": ["중계자", "유통사", "채널", "플랫폼"],
        "발송단가": ["발송단가", "(1)발송료", "발송 수수료", "건당발송료"],
        "인증단가": ["인증단가", "(1)인증료", "인증 수수료", "건당인증료"],
    }

    col_map = {}
    for std, variants in rename_map.items():
        for c in rate_db.columns:
            if c.lower().strip() in [v.lower() for v in variants]:
                col_map[c] = std

    rate_db = rate_db.rename(columns=col_map)

    needed = ["기관명", "부서명", "문서명", "중계자", "발송단가", "인증단가"]
    missing = [c for c in needed if c not in rate_db.columns]
    if missing:
        raise ValueError(f"요율표에 필요한 컬럼이 없습니다: {missing}")

    # 문자열 양끝 공백 제거
    for col in ["기관명", "부서명", "문서명", "중계자"]:
        rate_db[col] = rate_db[col].astype(str).str.strip()

    return rate_db[needed].copy()


def _attach_platform_key(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    업로드 통계 DF에 __플랫폼(카카오/KT/네이버)이 이미 있을 때,
    이를 '중계자' 컬럼으로 복사하여 rate_db와 매칭에 사용.
    """
    df = raw_df.copy()

    if "__플랫폼" not in df.columns:
        # 혹시 몰라서 fallback
        df["__플랫폼"] = "미확인"

    platform_to_vendor = {
        "카카오": "카카오",
        "kakao": "카카오",
        "kt": "KT",
        "케이티": "KT",
        "네이버": "네이버",
        "naver": "네이버",
    }

    df["중계자"] = df["__플랫폼"].astype(str).str.strip().map(
        lambda x: platform_to_vendor.get(x.lower(), x)
    )

    # 문자열 정리
    for col in ["기관명", "부서명", "문서명", "중계자"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def calculate_settlement(raw_df: pd.DataFrame, rate_db: pd.DataFrame):
    """
    1) 업로드 통계(raw_df) + 요율표(rate_db)를 조인
    2) 기관명 / 부서명 / 문서명 / 중계자 기준으로 매칭
    3) 발송비, 인증비, 총금액 계산
    4) 매칭 실패 건은 issues_df로 분리
    """
    # 요율표 정규화
    rate_norm = _normalize_rate_db(rate_db)

    # 통계 DF 정리
    df = _attach_platform_key(raw_df)

    needed_cols = ["기관명", "부서명", "문서명", "발송건수", "인증건수", "중계자"]
    missing_cols = [c for c in needed_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"통계자료에 필요한 컬럼이 없습니다: {missing_cols}")

    # 병합
    merged = pd.merge(
        df,
        rate_norm,
        on=["기관명", "부서명", "문서명", "중계자"],
        how="left",
        indicator=True,
    )

    # 매칭 실패 로그
    issues_df = merged[merged["_merge"] == "left_only"].copy()

    # 정상 매칭
    ok_df = merged[merged["_merge"] == "both"].copy()

    # 금액 계산
    ok_df["발송건수"] = pd.to_numeric(ok_df["발송건수"], errors="coerce").fillna(0)
    ok_df["인증건수"] = pd.to_numeric(ok_df["인증건수"], errors="coerce").fillna(0)
    ok_df["발송단가"] = pd.to_numeric(ok_df["발송단가"], errors="coerce").fillna(0)
    ok_df["인증단가"] = pd.to_numeric(ok_df["인증단가"], errors="coerce").fillna(0)

    ok_df["발송비"] = ok_df["발송건수"] * ok_df["발송단가"]
    ok_df["인증비"] = ok_df["인증건수"] * ok_df["인증단가"]
    ok_df["총금액"] = ok_df["발송비"] + ok_df["인증비"]

    ok_df = ok_df.drop(columns=["_merge"])

    return ok_df, issues_df
