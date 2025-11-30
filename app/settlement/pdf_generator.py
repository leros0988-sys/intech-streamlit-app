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


def mm(v):  # 좌표 변환
    return v * 2.83465


def draw_text(c, text, x, y, size=11):
    c.setFont(FONT_NAME, size)
    c.drawString(x, y, text)


# ================================================================
#   🔥 PDFGenerator 클래스 (함수 그대로 + 감싸기만)
# ================================================================
class PDFGenerator:

    # ---------------------------------------------------------
    # ① 카카오 단일 기관
    # ---------------------------------------------------------
    def generate_kakao_pdf(self, save_path, org_name, settle_id, summary_row, detail_df):
        c = canvas.Canvas(save_path, pagesize=A4)
        width, height = A4

        # Page 1 - 대금청구서
        draw_text(c, f"[대금청구서] {org_name}", mm(20), height - mm(25), size=18)
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

        # Page 2 - 상세내역
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
        return save_path

    # ---------------------------------------------------------
    # ② 다수기관 PDF
    # ---------------------------------------------------------
    def generate_multi_pdf(self, save_path, org_rows_df):
        c = canvas.Canvas(save_path, pagesize=A4)
        width, height = A4

        row = org_rows_df.iloc[0]

        # Page 3 - 표지
        draw_text(c, "[대금청구서(다수기관)]", mm(20), height - mm(25), size=18)

        draw_text(c, f"기관명 : {row['기관명']}", mm(20), height - mm(45))
        draw_text(c, f"청구명 : {row['청구명']}", mm(20), height - mm(60))
        draw_text(c, f"부서    : {row['부서(서식)']}", mm(20), height - mm(75))

        draw_text(c, "총 합계 :", mm(20), height - mm(95))
        draw_text(c, f"{int(row['합 계']):,} 원", mm(60), height - mm(95), size=14)

        c.showPage()

        # Page 4 - 월별 금액
        draw_text(c, f"[월별 금액표] {row['기관명']}", mm(20), height - mm(25), size=15)

        month_cols = [m for m in [
            "1월","2월","3월","4월","5월","6월",
            "7월","8월","9월","10월","11월","12월","합 계"
        ] if m in org_rows_df.columns]

        table_data = [["항목"] + month_cols]
        table_data.append(["금액"] + [f"{int(row[c]):,}" for c in month_cols])

        table = Table(table_data, colWidths=[mm(25)] * len(table_data[0]))
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )
        table.wrapOn(c, mm(20), height - mm(200))
        table.drawOn(c, mm(20), height - mm(250))

        c.showPage()

        # Page 5 - 총괄표
        draw_text(c, f"[총괄표] {row['기관명']}", mm(20), height - mm(25), size=15)

        total_table = [
            ["항목", "금액"],
            ["발송료", f"{int(row['정산발송료']):,}"],
            ["인증료", f"{int(row['정산인증료']):,}"],
            ["부가세", f"{int(row['부가세']):,}"],
            ["총금액", f"{int(row['합 계']):,}"],
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

        return save_path
