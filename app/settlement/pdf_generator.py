import pandas as pd
from fpdf import FPDF
import zipfile
from io import BytesIO
import streamlit as st


# -------------------------------------------------------
# 공통 함수: 천단위 콤마
# -------------------------------------------------------
def fmt(x):
    try:
        return f"{int(x):,}"
    except:
        return x


# -------------------------------------------------------
# PDF 기본 템플릿
# -------------------------------------------------------
class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "아이앤텍 전자고지 대금청구서", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 9)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


# -------------------------------------------------------
# 1) 단일기관 PDF 생성
# -------------------------------------------------------
def generate_single_pdf(org_name, settle_id, amount):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 12)

    pdf.ln(10)
    pdf.cell(0, 8, f"기관명 : {org_name}", ln=True)
    pdf.cell(0, 8, f"Settle ID : {settle_id}", ln=True)
    pdf.cell(0, 8, f"정산 금액 : {fmt(amount)} 원", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.read()


# -------------------------------------------------------
# 2) 다수기관 PDF 생성
# -------------------------------------------------------
def generate_multi_pdf(df):
    """
    df는 (기관명, Settle ID, 청구금액) 등의 컬럼이 포함된 정산용 DataFrame
    """
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 11)

    pdf.ln(5)
    pdf.cell(0, 6, "다수기관 대금청구서", ln=True)
    pdf.ln(3)

    cols = ["기관명", "Settle ID", "청구금액"]
    exists = [c for c in cols if c in df.columns]

    for _, row in df.iterrows():
        line = " | ".join([f"{c}: {fmt(row[c])}" for c in exists])
        pdf.multi_cell(0, 6, line)
        pdf.ln(1)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.read()


# -------------------------------------------------------
# 3) 전체 ZIP 묶기
# -------------------------------------------------------
def make_zip(pdf_dict):
    """
    pdf_dict = {filename: pdf_bytes}
    """
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        for fname, pdf_bytes in pdf_dict.items():
            z.writestr(fname, pdf_bytes)

    zip_buffer.seek(0)
    return zip_buffer.read()


# -------------------------------------------------------
# 4) PDF 생성 총괄 함수
# -------------------------------------------------------
def generate_pdfs_from_df(df):
    """
    df : 정산용 다수기관 DF (기관명, SettleID, 청구금액 포함)
    PDF 파일들을 dict 형태로 반환 → ZIP 다운로드 가능
    """

    if not {"기관명", "SettleID"}.issubset(df.columns):
        raise RuntimeError("기관명 또는 SettleID 컬럼이 없습니다.")

    pdf_dict = {}

    for _, row in df.iterrows():
        org = str(row["기관명"])
        sid = str(row["SettleID"])
        amt = row["청구금액"] if "청구금액" in df.columns else row.get("총금액", 0)

        pdf_bytes = generate_single_pdf(org, sid, amt)

        fname = f"{org}_{sid}.pdf"
        pdf_dict[fname] = pdf_bytes

    return pdf_dict
