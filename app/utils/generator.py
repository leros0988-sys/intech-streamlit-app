# app/utils/generator.py

import pandas as pd
from io import BytesIO


def generate_settle_report(df: pd.DataFrame) -> bytes:
    """
    정산 결과 DataFrame을 엑셀 바이너리(bytes)로 변환.
    필요하면 streamlit download_button에 data로 넣어서 사용.
    """
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()
