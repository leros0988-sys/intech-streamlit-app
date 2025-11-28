import pandas as pd
import io

def validate_uploaded_files(files):
    """
    업로드된 모든 엑셀 파일을 읽고,
    카카오 / KT / 네이버 파일을 자동 감지하여 df로 반환.
    파일명은 전혀 상관없음.
    """

    result = {}

    for f in files:
        name = f.name

        try:
            df = pd.read_excel(f)
        except Exception as e:
            raise ValueError(f"{name} 읽기 실패: {e}")

        # 빈 파일 거르기
        if df.empty:
            raise ValueError(f"{name}: 데이터가 비어 있습니다.")

        # 공백 컬럼명 제거
        df.columns = df.columns.str.strip()

        # 플랫폼 자동 감지
        platform = detect_platform(df)

        df["__플랫폼"] = platform

        result[name] = df

    return result


def detect_platform(df: pd.DataFrame) -> str:
    """
    통계자료가 어떤 플랫폼(KAKAO / KT / NAVER)인지 자동 감지
    """

    cols = df.columns

    # ----- 카카오 -----
    kakao_keys = ["앱 ID", "열람 시 인증 건수", "OTT", "조회 후 서명"]
    if any(key in cols for key in kakao_keys):
        return "카카오"

    # ----- KT -----
    kt_keys = ["발송요청건", "맵핑건수", "xMS", "RCS"]
    if any(key in cols for key in kt_keys):
        return "KT"

    # ----- 네이버 -----
    naver_keys = ["수신건수", "열람건수", "수신 수수료"]
    if any(key in cols for key in naver_keys):
        return "네이버"

    # ----- 감지 실패 -----
    return "미확인"
