import streamlit as st
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from app.utils.loader import load_manager_db


# --------------------------------------
# 기관명 표준화 (필수)
# --------------------------------------
def _normalize_org(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    possible_cols = ["기관", "기관명", "이용기관명", "사업자명", "App ID", "app id"]

    actual_col = None
    for c in possible_cols:
        if c in df.columns:
            actual_col = c
            break

    if actual_col:
        df["기관"] = df[actual_col].fillna("").astype(str).str.strip()
    else:
        df["기관"] = "미확인기관"

    return df


# --------------------------------------
# SETTLE_ID + 기관별 요약
# --------------------------------------
def _summarize_settle(df: pd.DataFrame) -> pd.DataFrame:
    df = _normalize_org(df)

    # SETTLE ID 탐색
    possible_ids = [c for c in df.columns if "SETTLE" in c.upper()]
    settle_col = possible_ids[0] if possible_ids else None

    group_cols = ["기관"]
    if settle_col:
        group_cols.append(settle_col)

    numeric_cols = [
        c for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c])
    ]

    if not numeric_cols:
        numeric_cols = []

    summary = df.groupby(group_cols)[numeric_cols].sum().reset_index()
    return summary


# --------------------------------------
# PDF 생성
# --------------------------------------
def _generate_pdf(gian_text: str) -> bytes:
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    text = p.beginText(40, 800)
    text.setFont("Helvetica", 11)

    for line in gian_text.split("\n"):
        text.textLine(line)

    p.drawText(text)
    p.save()
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------
# 메인 페이지
# --------------------------------------
def gian_page():
    st.markdown("## 📝 기안 생성 페이지")

    # 데이터 체크
    df = st.session_state.get("raw_combined_df")
    if df is None or df.empty:
        st.warning("⚠ 먼저 정산 데이터 업로드가 필요합니다.")
        return

    # load manager DB
    try:
        manager_db = load_manager_db()
    except:
        st.error("❌ manager_db.xlsx 파일을 불러올 수 없습니다.")
        return

    st.markdown("### 📁 담당자 DB")
    st.dataframe(manager_db, use_container_width=True)

    df = _normalize_org(df)
    orgs = sorted(df["기관"].unique().tolist())

    selected_org = st.selectbox("기안 생성할 기관 선택", orgs)

    org_df = df[df["기관"] == selected_org]

    summary = _summarize_settle(org_df)

    st.markdown("### 📊 기관 요약 데이터")
    st.dataframe(summary, use_container_width=True)

    # 담당자 조회
    manager_row = manager_db[manager_db["기관"] == selected_org]

    if manager_row.empty:
        담당자명 = "미등록"
        직급 = "-"
        연락처 = "-"
    else:
        row = manager_row.iloc[0]
        담당자명 = row.get("담당자명", "미등록")
        직급 = row.get("직급", "-")
        연락처 = row.get("연락처", "-")

    # -----------------------------
    # 발송/인증 건수 합계
    # -----------------------------
    total_send = 0
    total_cert = 0

    for col in summary.columns:
        col_low = col.lower()

        if "발송" in col_low or "수신" in col_low:
            total_send += summary[col].sum()

        if "열람" in col_low or "조회" in col_low or "인증" in col_low:
            total_cert += summary[col].sum()

    # -----------------------------
    # 기안문
    # -----------------------------
    gian_text = f"""
[전자고지 정산 기안문]

1. 기관명: {selected_org}

2. 담당자 정보
   - 담당자: {담당자명}
   - 직급: {직급}
   - 연락처: {연락처}

3. 정산 건수
   - 총 발송 건수: {total_send:,}건
   - 총 인증/열람 건수: {total_cert:,}건

4. 첨부 서류
   - 일자별 통계자료
   - 채널별 상세내역
   - 발송/인증 요약표

5. 검토 의견
   상기 기관의 전자고지 발송 및 열람 건수에 대한 정산을 위해
   기안을 상신하오니 검토 후 승인 부탁드립니다.

작성자: 정윤서
아이앤텍 전자문서사업부
"""

    st.markdown("### 📝 자동 생성된 기안문")
    st.text_area("기안문", gian_text, height=350)

    # Excel 다운로드
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        summary.to_excel(writer, index=False, sheet_name="정산요약")
    excel_buffer.seek(0)

    st.download_button(
        "📥 기안용 Excel 다운로드",
        data=excel_buffer,
        file_name=f"{selected_org}_정산요약.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # PDF 다운로드
    pdf_bytes = _generate_pdf(gian_text)
    st.download_button(
        "📄 기안문 PDF 다운로드",
        data=pdf_bytes,
        file_name=f"{selected_org}_기안문.pdf",
        mime="application/pdf"
    )
