# app/utils/file_reader.py

import pandas as pd
from io import BytesIO
import warnings

def read_any_file(uploaded_file):
    """
    업로드된 파일을 반드시 다음 형태로 반환한다:
    {
        "시트명1": df1,
        "시트명2": df2,
        ...
    }
    실패하면 예외 발생
    """

    file_bytes = uploaded_file.read()
    data = BytesIO(file_bytes)

    # ------------------------------------------------------
    # 1) Excel — 다중 시트 로드 (openpyxl)
    # ------------------------------------------------------
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            xls = pd.ExcelFile(data, engine="openpyxl")

        sheet_dict = {}
        for sheet_name in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=sheet_name, dtype=str)
                sheet_dict[sheet_name] = df
            except:
                continue

        if sheet_dict:
            return sheet_dict

    except Exception as e:
        print(f"[file_reader] Excel 다중 시트 실패: {e}")

    # ------------------------------------------------------
    # 2) CSV (utf-8)
    # ------------------------------------------------------
    data.seek(0)
    try:
        df = pd.read_csv(data, dtype=str, encoding="utf-8-sig")
        return {"CSV": df}
    except:
        pass

    # ------------------------------------------------------
    # 3) CSV (cp949)
    # ------------------------------------------------------
    data.seek(0)
    try:
        df = pd.read_csv(data, dtype=str, encoding="cp949")
        return {"CSV": df}
    except:
        pass

    # ------------------------------------------------------
    # 최종 실패
    # ------------------------------------------------------
    raise RuntimeError("❌ 파일 파싱 실패: 엑셀/CSV 어떤 구조도 읽을 수 없습니다.")

