import pandas as pd


def validate_uploaded_files(files):
    """
    여러 엑셀 파일 업로드 시 자동 감지 + 검증
    """
    results = {}

    for f in files:
        name = f.name

        try:
            df = pd.read_excel(f)
        except Exception as e:
            raise ValueError(f"{name} 읽기 실패: {e}")

        if df.empty:
            raise ValueError(f"{name}: 데이터 없음")

        df.columns = df.columns.str.strip()
        df["__플랫폼"] = detect_platform(df)
        results[name] = df

    return results


def detect_platform(df):
    cols = df.columns

    if any(k in cols for k in ["앱 ID", "OTT", "열람 시 인증", "서명"]):
        return "카카오"

    if any(k in cols for k in ["발송요청건", "맵핑건수", "xMS", "RCS"]):
        return "KT"

    if any(k in cols for k in ["수신건수", "열람건수", "수신 수수료"]):
        return "네이버"

    return "미확인"


def validate_uploaded_df(df):
    """
    upload_page.py에서 사용하던 옛 함수 호환용
    """
    if df is None or df.empty:
        raise ValueError("업로드된 엑셀이 비어있습니다.")
    df.columns = df.columns.str.strip()
    return df

