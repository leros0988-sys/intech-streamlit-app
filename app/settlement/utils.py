import pandas as pd
from io import BytesIO
import re


# -------------------------------------------------------
# 1) 금액 포맷 (천단위 쉼표)
# -------------------------------------------------------

def format_money(x):
    """
    금액을 천단위 쉼표로 포맷
    """
    try:
        return f"{int(x):,}"
    except:
        return x


# -------------------------------------------------------
# 2) 파일명 안전하게 변환 (영문 + 숫자 + _ 만 남김)
# -------------------------------------------------------

def safe_filename(name: str) -> str:
    """
    기관명 등을 안전한 파일명으로 변환
    """
    name = str(name).strip()
    name = re.sub(r"[^0-9A-Za-z가-힣_]+", "_", name)
    return name


# -------------------------------------------------------
# 3) DataFrame → Excel bytes 변환
# -------------------------------------------------------

def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """
    DataFrame을 엑셀(byte stream)로 변환해
    Streamlit download_button에서 직접 쓸 수 있게 반환
    """
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)
    return buffer.read()


# -------------------------------------------------------
# 4) DataFrame 기본 정리: 공백 제거 & NaN 정리
# -------------------------------------------------------

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    기본적인 trimming / 공백 제거 / NaN 처리
    """
    df = df.copy()

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()

    df = df.fillna("")
    return df
