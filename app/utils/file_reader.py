import pandas as pd
from io import BytesIO
import warnings

def read_any_file(uploaded_file):
    """
    엑셀/CSV 어떤 파일이 와도 반드시 DataFrame으로 반환하는 안정 버전.
    - openpyxl 스타일 오류 무시
    - CSV fallback (utf-8 → cp949)
    - Silent Fail 제거: 무조건 DataFrame 반환 or 명확한 에러
    """

    file_bytes = uploaded_file.read()
    data = BytesIO(file_bytes)

    # ---------------------------------------------------
    # 1) Excel 시도 (openpyxl)
    # ---------------------------------------------------
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(data, dtype=str, engine="openpyxl")
        return df
    except Exception as e:
        # Debug용 로그
        print(f"[read_any_file] openpyxl 실패: {e}")

    # 포인터 리셋
    data.seek(0)

    # ---------------------------------------------------
    # 2) CSV(UTF-8) 시도
    # ---------------------------------------------------
    try:
        df = pd.read_csv(data, dtype=str, encoding="utf-8-sig")
        return df
    except Exception as e:
        print(f"[read_any_file] CSV utf-8 실패: {e}")

    data.seek(0)

    # ---------------------------------------------------
    # 3) CSV(cp949) 시도
    # ---------------------------------------------------
    try:
        df = pd.read_csv(data, dtype=str, encoding="cp949")
        return df
    except Exception as e:
        print(f"[read_any_file] CSV cp949 실패: {e}")

    # ---------------------------------------------------
    # 4) 마지막 보루 — 명확하게 에러 반환
    # ---------------------------------------------------
    raise RuntimeError("❌ 파일을 읽을 수 없습니다. Excel/CSV 구조가 모두 손상된 파일입니다.")
