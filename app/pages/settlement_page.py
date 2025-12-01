import io
import tempfile
import zipfile
from typing import Optional
import pandas as pd
import streamlit as st

from app.settlement.pdf_generator import (
    generate_kakao_pdf,
    generate_multi_pdf
)

# ------------------------------------------------------
# 공통 컬럼명 정규화
# ------------------------------------------------------
def normalize_col(col: str):
    if col is None:
        return ""
    return (
        str(col)
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .lower()
    )

def normalize_dataframe_columns(df: pd.DataFrame):
    df.columns = [normalize_col(c) for c in df.columns]
    return df


# ------------------------------------------------------
# 엑셀 시트 선택 로더
# ------------------------------------------------------
def load_excel_sheet(file, label: str) -> Optional[pd.DataFrame]:
    if file is None:
        st.info(f"{label} 파일을 업로드하세요.")
        return None

    try:
        xls = pd.ExcelFile(file)
    except Exception as e:
        st.error(f"{label} 파일 읽기 오류: {e}")
        return None

    sheet = st.selectbox(
        f"{label} 시트 선택",
        xls.sheet_names,
        key=f"{label}_sheet"
    )

    try:
        df = pd.read_excel(xls, sheet)
    except Exception as e:
        st.error(f"{label} 시트 로드 오류: {e}")
        return None

    st.success(f"{label} '{sheet}' 로드 완료 (행 {len(df)})")

    with st.expander(f"{label} 미리보기"):
        st.dataframe(df.head(30), use_container_width=True)

    return df


# ------------------------------------------------------
# Settlement Page
# ------------------------------------------------------
def settlement_page():

    st.markdown("<div class='title-text'>📑 전자고지 정산 · PDF ZIP 생성</div>", unsafe_allow_html=True)
    st.write("---")

    # --------------------------------------------------
    # 1) 파일 업로드
    # --------------------------------------------------
    st.subheader("1️⃣ 엑셀 업로드")

    col1, col2 = st.columns(2)
    with col1:
        kakao_file = st.file_uploader("카카오 정산 엑셀", type=["xlsx"])
    with col2:
        master_file = st.file_uploader("2025 정산 발송료 시트", type=["xlsx"])

    if kakao_file is None or master_file is None:
        st.info("두 파일을 모두 업로드하세요.")
        return

    st.write("---")

    # --------------------------------------------------
    # 2) 시트 선택 및 로드
    # --------------------------------------------------
    st.subheader("2️⃣ 시트 선택")

    kakao_df = load_excel_sheet(kakao_file, "카카오 정산")
    if kakao_df is None:
        return

    master_xls = pd.ExcelFile(master_file)

    rates_sheet = st.selectbox("발송료 시트 선택", master_xls.sheet_names, key="rates")
    rates_df = pd.read_excel(master_xls, rates_sheet)
    st.success(f"발송료 시트 '{rates_sheet}' 로드 완료")

    drafts_sheet = st.selectbox("기안자료 시트 선택", master_xls.sheet_names, key="drafts")
    drafts_df = pd.read_excel(master_xls, drafts_sheet)
    st.success(f"기안자료 시트 '{drafts_sheet}' 로드 완료")

    st.write("---")

    # --------------------------------------------------
    # 3) 컬럼 정규화 (이게 전체 문제 해결)
    # --------------------------------------------------
    st.subheader("3️⃣ 컬럼 정규화 처리 (자동 매칭)")

    kakao_df = normalize_dataframe_columns(kakao_df)
    rates_df = normalize_dataframe_columns(rates_df)
    drafts_df = normalize_dataframe_columns(drafts_df)

    # 강제 컬럼명 맵핑
    col_fix = {
        "settleid": "settleid",
        "카카오settleid": "settleid",
        "카카오settlid": "settleid",
        "id": "settleid",
        "기관명": "기관명",
        "기관": "기관명",
    }

    fixed_cols = {}
    for c in rates_df.columns:
        if c in col_fix:
            fixed_cols[c] = col_fix[c]
    rates_df.rename(columns=fixed_cols, inplace=True)

    # 카카오 DF에서도 동일하게
    fixed_cols = {}
    for c in kakao_df.columns:
        if c in col_fix:
            fixed_cols[c] = col_fix[c]
    kakao_df.rename(columns=fixed_cols, inplace=True)

    st.success("정규화 완료 → Settle ID 자동 매칭 OK")

    with st.expander("정규화 결과 확인"):
        st.write("카카오 DF 컬럼:", list(kakao_df.columns))
        st.write("발송료 DF 컬럼:", list(rates_df.columns))

    st.write("---")

    # --------------------------------------------------
    # 4) 단일기관 ZIP 생성
    # --------------------------------------------------
    st.subheader("4️⃣ 카카오 단일기관 PDF ZIP 생성")

    if "settleid" not in kakao_df.columns or "settleid" not in rates_df.columns:
        st.error("정규화 실패: settleid 컬럼이 존재하지 않습니다.")
        return

    kakao_ids = sorted(set(kakao_df["settleid"].astype(str)))
    master_ids = sorted(set(rates_df["settleid"].astype(str)))

    available_ids = sorted(list(set(kakao_ids) & set(master_ids)))

    if not available_ids:
        st.info("카카오 ↔ 발송료 공통 Settle ID 없음")
    else:
        st.success(f"총 {len(available_ids)}개 Settle ID 매칭됨")

        selected_ids = st.multiselect(
            "PDF 생성할 Settle ID 선택",
            available_ids,
            default=[]
        )

        select_all = st.checkbox("전체 선택")
        if select_all:
            selected_ids = available_ids

        if st.button("📦 단일기관 PDF ZIP 다운로드"):
            if not selected_ids:
                st.warning("선택된 기관이 없습니다.")
            else:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w") as zipf:
                    for sid in selected_ids:
                        row = rates_df[rates_df["settleid"] == sid].iloc[0]
                        org_name = row.get("기관명", f"기관_{sid}")

                        # summary + detail
                        from app.pages.settlement_page import (
                            build_kakao_summary_row,
                            build_kakao_detail_df,
                        )
                        summary_row = build_kakao_summary_row(kakao_df, rates_df, sid)
                        detail_df = build_kakao_detail_df(kakao_df, sid)

                        # temp PDF
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            pdf_path = tmp.name

                        generate_kakao_pdf(pdf_path, org_name, sid, summary_row, detail_df)

                        with open(pdf_path, "rb") as f:
                            zipf.writestr(f"{org_name}_{sid}.pdf", f.read())

                st.download_button(
                    "📥 ZIP 다운로드",
                    data=zip_buf.getvalue(),
                    file_name="kakao_single_pdf.zip"
                )

    st.write("---")

    # --------------------------------------------------
    # 5) 다수기관 ZIP 생성
    # --------------------------------------------------
    st.subheader("5️⃣ 다수기관 PDF ZIP 생성")

    if "기관명" not in rates_df.columns:
        st.error("'기관명' 컬럼이 없어 다수기관 PDF 불가")
        return

    org_list = sorted(rates_df["기관명"].dropna().astype(str).unique().tolist())

    selected_orgs = st.multiselect("기관 선택", org_list, default=[])
    select_all_org = st.checkbox("전체 기관 선택")

    if select_all_org:
        selected_orgs = org_list

    if st.button("📦 다수기관 ZIP 다운로드"):
        if not selected_orgs:
            st.warning("선택된 기관이 없습니다.")
        else:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as zipf:
                for org in selected_orgs:
                    rows = rates_df[rates_df["기관명"] == org].copy()

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        pdf_path = tmp.name

                    generate_multi_pdf(pdf_path, rows)

                    with open(pdf_path, "rb") as f:
                        zipf.writestr(f"{org}_다수기관.pdf", f.read())

            st.download_button(
                "📥 ZIP 다운로드",
                data=zip_buf.getvalue(),
                file_name="multi_org_pdf.zip"
            )
