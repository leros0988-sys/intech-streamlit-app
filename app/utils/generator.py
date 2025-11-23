import pandas as pd
import io

def generate_settlement_excel(df: pd.DataFrame) -> bytes:
    """
    DataFrame → 엑셀 파일 bytes 변환
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)

    buf.seek(0)
    return buf.read()
