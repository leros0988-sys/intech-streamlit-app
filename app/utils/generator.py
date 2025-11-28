import pandas as pd
import io


def generate_settlement_excel(df: pd.DataFrame):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="정산결과")
    buf.seek(0)
    return buf

