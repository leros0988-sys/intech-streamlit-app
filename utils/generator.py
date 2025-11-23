# utils/generator.py

import pandas as pd

def generate_partner_excel(df, partner_name, send_rate, read_rate):
    """
    협력사(에프원, 엑스아이티) 정산 다운로드용 엑셀 생성
    """

    df = df.copy()
    df["발송료"] = df["발송건수"] * send_rate
    df["인증료"] = df["인증건수"] * read_rate
    df["총금액"] = df["발송료"] + df["인증료"]

    output = {
        "filename": f"{partner_name}_정산.xlsx",
        "data": df
    }
    return output
