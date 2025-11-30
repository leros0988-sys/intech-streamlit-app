import pandas as pd
import streamlit as st
from io import BytesIO

# -------------------------------------------------------
# 여러 엑셀 파일 업로드 후 DataFrame으로 읽어오기
# -------------------------------------------------------

def read_excel_file(uploaded_file):
    """단일 엑셀/CSV 파일을 읽어 DF 반환"""
    name = uploaded_file.name.lower()

    try:
        if name.endswith(".csv"):
            return pd.read_csv(uploaded_file)

        # 엑셀 통합
        return pd.read_excel(uploaded_file, engine="openpyxl")

    except Exception as e:
        raise RuntimeError(f"{uploaded_file.name} 읽기 중 오류: {e}")


def upload_multiple_files():
    """
    파일 여러개 업로드 → {파일명: DF} 딕셔너리로 반환
    """
    uploaded = st.file_uploader(
        "📂 정산 관련 엑셀 파일 업로드 (여러 개 가능)",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
    )

    if not uploaded:
        return None

    data_map = {}
    errors = []

    for f in uploaded:
        try:
            df = read_excel_file(f)
            if df is not None and len(df) > 0:
                data_map[f.name] = df
        except Exception as e:
            errors.append(str(e))

    if errors:
        st.error("파일 읽기 오류 발생:\n" + "\n".join(errors))

    if not data_map:
        st.warning("유효한 데이터가 있는 파일이 없습니다.")

    return data_map
