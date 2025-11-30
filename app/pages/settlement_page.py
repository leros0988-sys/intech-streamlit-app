import io
import tempfile
from typing import Optional, List

import pandas as pd
import streamlit as st

from app.settlement.uploader import (
    load_master_workbook,
    load_kakao_stats
)

from app.settlement.classifier import classify_uploaded_files
from app.settlement.processor import SettlementProcessor
from app.settlement.missing import MissingFinder
from app.settlement.summary import SettlementSummary
from app.settlement.pdf_generator import PDFGenerator


# ------------------------------------------------------
# 유틸: 엑셀 파일에서 시트 선택 후 DataFrame 로드
# ------------------------------------------------------
def load_excel_sheet(uploaded_file, label: str) -> Optional[pd.DataFrame]:
    if uploaded_file is None:
        st.info(f"{label} 엑셀 파일을 업로드해주세요.")
        return None

    try:
        xls = pd.ExcelFile(uploaded_file)
    except Exception as e:
        st.error(f"{label} 엑셀을 읽는 중 오류: {e}")
        return None

    sheet_name = st.selectbox(
        f"{label}에서 사용할 시트를 선택하세요",
        xls.sheet_names,
        key=f"{label}_sheet_select",
    )

    try:
        df = pd.read_excel(xls, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"{label} 시트 로드 중 오류: {e}")
        return None

    st.success(f"{label} - '{sheet_name}' 시트 로드 완료 (행 {len(df)})")

    with st.expander(f"{label} 미리보기 (상위 30행)"):
        st.dataframe(df.head(30), use_container_width=True)

    return df


# ------------------------------------------------------
# 본체: 정산 페이지
# ------------------------------------------------------
def settlement_page():

    st.markdown(
        "<div class='title-text'>📑 전자고지 정산 · 대금청구서 생성</div>",
        unsafe_allow_html=True,
    )

    st.write("---")

    # 1) 파일 업로드
    st.subheader("1️⃣ 정산 엑셀 업로드")

    col1, col2 = st.columns(2)
    with col1:
        kakao_file = st.file_uploader("카카오 월별 정산 엑셀 업로드", type=["xlsx", "xls"])
    with col2:
        master_file = st.file_uploader("아이앤텍 2025 정산 시트 업로드", type=["xlsx", "xls"])

    if kakao_file is None or master_file is None:
        st.info("두 파일을 모두 업로드하면 다음 단계가 열립니다.")
        return

    st.write("---")

    # 2) 시트 선택 및 로드
    st.subheader("2️⃣ 시트 선택")

    kakao_df = load_excel_sheet(kakao_file, "카카오 정산 엑셀")
    if kakao_df is None:
        return

    master_xls = pd.ExcelFile(master_file)

    # -------------------------
    # 발송료 시트 선택
    # -------------------------
    rates_sheet = st.selectbox(
        "2025 발송료 시트 선택",
        master_xls.sheet_names,
    )
    rates_df = pd.read_excel(master_xls, sheet_name=rates_sheet)
    st.success(f"발송료 시트 '{rates_sheet}' 로드 (행 {len(rates_df)})")

    # === 발송료 시트 컬럼 표준화 ===
    def normalize_col(c):
        return str(c).replace(" ", "").replace("_", "").strip().lower()

    rates_df.columns = [normalize_col(c) for c in rates_df.columns]

    col_map = {
        "기관명": "기관명",
        "기관": "기관명",
        "카카오settleid": "카카오 settle id",
        "settleid": "카카오 settle id",
        "카카오id": "카카오 settle id",
        "id": "카카오 settle id",
        "발송료": "정산발송료",
        "정산발송료": "정산발송료",
        "인증료": "정산인증료",
        "정산인증료": "정산인증료",
        "부가세": "부가세",
        "합계": "합 계",
        "합계금액": "합 계",
    }
    rates_df.rename(columns=col_map, inplace=True)

    with st.expander("2025 발송료 미리보기 (상위 30행)"):
        st.dataframe(rates_df.head(30), use_container_width=True)

    # -------------------------
    # 기안자료 시트 선택
    # -------------------------
    drafts_sheet = st.selectbox(
        "기안자료 시트 선택",
        master_xls.sheet_names,
    )
    drafts_df = pd.read_excel(master_xls, sheet_name=drafts_sheet)
    st.success(f"기안자료 시트 '{drafts_sheet}' 로드 (행 {len(drafts_df)})")

    with st.expander("기안자료 미리보기 (상위 30행)"):
        st.dataframe(drafts_df.head(30), use_container_width=True)

    st.write("---")

    # --------------------------------------------------
    # 3) 정산 엔진 초기화
    # --------------------------------------------------
    st.subheader("3️⃣ 정산 요약 · 누락기관 분석")

    processor = SettlementProcessor(rates_df=rates_df, drafts_df=drafts_df, kakao_df=kakao_df)
    summary = SettlementSummary(kakao_df=kakao_df, rates_df=rates_df, drafts_df=drafts_df)
    missing_det = MissingFinder(kakao_df=kakao_df, master_settle_df=rates_df)

    # 요약 결과
    summary_dict = summary.build_summary_dict()

    col_a, col_b, col_c = st.columns(3)
    totals = summary_dict["총매출"]
    col_a.metric("카카오 총액", f"{totals['카카오 총액']:,} 원")
    col_b.metric("다수기관 총액", f"{totals['다수기관 총액']:,} 원")
    col_c.metric("전체 총액", f"{totals['전체 총액']:,} 원")

    # 누락기관
    st.markdown("### ⚠ 누락기관 (카카오에는 있는데 발송료 시트에 없음)")
    missing_ids = missing_det.get_missing_settle_ids()

    if not missing_ids:
        st.success("누락된 Settle ID 없음")
    else:
        missing_df = missing_det.to_dataframe()
        st.dataframe(missing_df, use_container_width=True)

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            missing_df.to_excel(writer, index=False)
        st.download_button(
            "누락기관 목록 다운로드",
            data=buf.getvalue(),
            file_name="누락기관.xlsx",
        )

    st.write("---")

    # --------------------------------------------------
    # 4) 단일기관 PDF 생성
    # --------------------------------------------------
    st.subheader("4️⃣ 카카오 단일기관 대금청구서 PDF 생성")

    kakao_ids = {str(x).strip() for x in kakao_df.get("Settle ID", []) if str(x).strip()}
    master_ids = {str(x).strip() for x in rates_df.get("카카오 settle id", []) if str(x).strip()}
    available_ids = sorted(list(kakao_ids & master_ids))

    if not available_ids:
        st.info("PDF 생성 가능한 Settle ID 없음")
    else:
        selected_sid = st.selectbox("PDF 생성할 Settle ID 선택", available_ids)

        # 기관명 찾기
        row = rates_df[rates_df["카카오 settle id"] == selected_sid]
        org_name = row.iloc[0]["기관명"] if not row.empty else f"Settle ID {selected_sid}"

        if st.button("📄 단일기관 PDF 생성"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                path = tmp.name

            from app.settlement.pdf_generator import generate_kakao_pdf

            summary_row = processor.build_single_summary(selected_sid)
            detail_df = processor.build_single_detail(selected_sid)

            generate_kakao_pdf(path, org_name, selected_sid, summary_row, detail_df)

            with open(path, "rb") as f:
                st.download_button(
                    "PDF 다운로드",
                    data=f.read(),
                    file_name=f"{org_name}_카카오정산.pdf",
                )

    st.write("---")

    # --------------------------------------------------
    # 5) 다수기관 PDF 생성
    # --------------------------------------------------
    st.subheader("5️⃣ 다수기관 PDF 생성")

    if "기관명" not in rates_df.columns:
        st.info("발송료 시트에 기관명 컬럼 없음 → 생성 불가")
        return

    org_list = sorted(rates_df["기관명"].dropna().astype(str).unique().tolist())
    selected_org = st.selectbox("기관 선택", org_list)

    if st.button("📄 다수기관 PDF 생성"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            path = tmp.name

        from app.settlement.pdf_generator import generate_multi_pdf

        rows = rates_df[rates_df["기관명"] == selected_org]
        generate_multi_pdf(path, rows)

        with open(path, "rb") as f:
            st.download_button(
                "PDF 다운로드",
                data=f.read(),
                file_name=f"{selected_org}_다수기관정산.pdf",
            )
