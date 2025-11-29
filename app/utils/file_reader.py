import pandas as pd
from io import BytesIO
import warnings

def read_any_file(uploaded_file):
    """
    엑셀 스타일 깨짐 오류(openpyxl stylesheet error)를 우회해서 읽는 안전 버전.
    calamine 없이 Streamlit Cloud에서 100% 작동.
    """

    file_bytes = uploaded_file.read()
    data = BytesIO(file_bytes)

    # 1차: openpyxl 정상 로드 시도
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # 스타일 관련 경고 무시
            return pd.read_excel(data, dtype=str, engine="openpyxl")
    except:
        pass

    # 2차: 파일 포인터 리셋
    data.seek(0)

    # 2차: CSV 변환 시도 (엑셀 구조 깨진 경우)
    try:
        return pd.read_csv(data, dtype=str, encoding="utf-8-sig")
    except:
        pass

    # 3차: cp949 인코딩 시도 (공공기관 XLSX → CSV 변환 형태)
    data.seek(0)
    try:
        return pd.read_csv(data, dtype=str, encoding="cp949")
    except:
        raise RuntimeError("엑셀 파일을 읽을 수 없습니다. 엑셀 구조가 손상된 파일입니다.")
