import pandas as pd

def validate_uploaded_files(files):
    result = {}

    for f in files:
        name = f.name

        try:
            df = pd.read_excel(f)
        except Exception as e:
            raise ValueError(f"{name} 읽기 실패: {e}")

        if df.empty:
            raise ValueError(f"{name}: 데이터 없음")

        df.columns = df.columns.str.strip()
        df["플랫폼"] = detect_platform(df)

        result[name] = df

    return result


def detect_platform(df):
    cols = df.columns

    kakao_keys = ["앱 ID", "열람 시 인증", "OTT", "서명"]
    if any(k in cols for k in kakao_keys):
        return "카카오"

    kt_keys = ["발송요청건", "맵핑", "xMS", "RCS"]
    if any(k in cols for k in kt_keys):
        return "KT"

    naver_keys = ["수신건수", "열람건수", "수신 수수료"]
    if any(k in cols for k in naver_keys):
        return "네이버"

    return "미확인"
