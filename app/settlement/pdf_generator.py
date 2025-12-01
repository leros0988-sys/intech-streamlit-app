from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import os
import pandas as pd


# -------------------------------------
# 폰트 등록 (Korean Friendly)
# -------------------------------------
FONT_NAME = "NotoSansKR"
FONT_FILE = "app/static/NotoSansKR-Regular.otf"

if os.path.exists(FONT_FILE):
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))
else:
    FONT_NAME = "Helvetica"


# 좌표 변환
def mm(v):
    return v * 2.83465


# 텍스트 출력 헬퍼
def draw_text(c, text, x, y, size=11):
    c.setFont(FONT_NAME, size)
    c.drawString(x, y, text)


# =====================================================================
# ① 카카오 단일기관 PDF 생성
# =====================================================================
def generate_kakao_pdf(save_path, org_name, settle_id, summary_row, detail_df):
    c = canvas.Canvas(save_path, pagesize=A4)
    width, height = A4

    # Page 1 — 기본요약
    draw_text(c, f"[카카오 대금청구서] {org_name}", mm(20), height - mm(25), size=18)
    draw_text(c, f"Settle ID : {settle_id}", mm(20), height - mm(40), size=12)

    draw_text(c, "발송료:", mm(25), height - mm(65))
    draw_text(c, f"{summary_row['발송료']:,} 원", mm(60), height - mm(65))

    draw_text(c, "인증료:", mm(25), height - mm(80))
    draw_text(c, f"{summary_row['인증료']:,} 원", mm(60), height - mm(80))

    draw_text(c, "부가세:", mm(25), height - mm(95))
    draw_text(c, f"{summary_row['부가세']:,} 원", mm(60), height - mm(95))

    draw_text(c, "총 합계:", mm(25), height - mm(115), size=14)
    draw_text(c, f"{summary_row['총금액']:,} 원", mm(60), height - mm(115), size=14)

    c.showPage()

    # Page 2 — 상세내역
    draw_text(c, f"[상세내역] {org_name}", mm(20), height - mm(25), size=15)

    table_data = [detail_df.columns.tolist()] + detail_df.values.tolist()
    table = Table(table_data, colWidths=[mm(25)] * len(detail_df.columns))

    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )

    table.wrapOn(c, mm(15), height - mm(200))
    table.drawOn(c, mm(15), height - mm(250))

    c.showPage()
    c.save()


# =====================================================================
# ② 다수기관 PDF 생성
# =====================================================================
def generate_multi_pdf(save_path, org_rows_df):
    c = canvas.Canvas(save_path, pagesize=A4)
    width, height = A4

    row = org_rows_df.iloc[0]

    # Page 1 — 표지
    draw_text(c, "[대금청구서(다수기관)]", mm(20), height - mm(25), size=18)
    draw_text(c, f"기관명 : {row.get('기관명', '')}", mm(20), height - mm(45))
    draw_text(c, f"청구명 : {row.get('청구명', '')}", mm(20), height - mm(60))
    draw_text(c, f"부서 : {row.get('부서(서식)', '')}", mm(20), height - mm(75))

    total_amt = int(row.get("합 계", row.get("합계", 0)))
    draw_text(c, "총 합계 :", mm(20), height - mm(95))
    draw_text(c, f"{total_amt:,} 원", mm(60), height - mm(95), size=14)

    c.showPage()

    # Page 2 — 월별 금액표
    draw_text(c, f"[월별 금액표] {row.get('기관명','')}", mm(20), height - mm(25), size=15)

    month_cols = [
        "1월","2월","3월","4월","5월","6월",
        "7월","8월","9월","10월","11월","12월","합 계"
    ]
    month_cols = [x for x in month_cols if x in org_rows_df.columns]

    table_data = [["항목"] + month_cols]
    table_data.append(["금액"] + [f"{int(row[c]):,}" for c in month_cols])

    table = Table(table_data, colWidths=[mm(25)] * len(table_data[0]))
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )

    table.wrapOn(c, mm(20), height - mm(200))
    table.drawOn(c, mm(20), height - mm(250))

    c.showPage()

    # Page 3 — 총괄표
    draw_text(c, f"[총괄표] {row.get('기관명','')}", mm(20), height - mm(25), size=15)

    total_table = [
        ["항목", "금액"],
        ["발송료", f"{int(row.get('정산발송료', 0)):,}"],
        ["인증료", f"{int(row.get('정산인증료', 0)):,}"],
        ["부가세", f"{int(row.get('부가세', 0)):,}"],
        ["총금액", f"{total_amt:,}"],
    ]

    tt = Table(total_table, colWidths=[mm(40), mm(40)])
    tt.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )

    tt.wrapOn(c, mm(20), height - mm(200))
    tt.drawOn(c, mm(20), height - mm(250))

    c.showPage()
    c.save()
