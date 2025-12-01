import io
import tempfile
import zipfile
from typing import Optional

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
from app.settlement.pdf_generator import generate_kakao_pdf, generate_multi_pdf


# ============================================
# 엑셀 시트 선택 후 DataFrame 로드
# ============================================
def load_excel_sheet(uploaded_file, label: str) -> Optional[pd.DataFrame]:
    if uploaded_file is None:
        st.info(f"{label} 엑셀 파일을 업로드해주세요.")
        return None

    try:
        xls = pd.ExcelFile(uploaded_file)
    except Exception as e:
        st.error(f"{label} 엑셀을 읽는 중 오류가 발생했습니다: {e}")
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


# ============================================
# 발송료 시트 컬럼 정규화
# ============================================
def normalize_col(c):
    return str(c).replace(" ", "").replace("_", "").replace("-", "").strip().lower()


# ============================================
# 카카오 단가 찾기
# ============================================
def pick_kakao_rates(rates_df: pd.DataFrame, settle_id: str):
    row = rates_df[rates_df.get("카카오 settle id", "").astype(str) == str(settle_id)]
    if row.empty:
        return 0, 0

    r = row.iloc[0]

    send_cols = ["(1)발송료", "(2)발송료", "(3)발송료"]
    auth_cols = ["(1)인증료", "(2)인증료", "(3)인증료"]

    def first_nonzero(row_, cols):
        for c in cols:
            if c in row_ and pd.notna(row_[c]):
                try:
                    v = float(row_[c])
                    if v != 0:
                        return v
                except:
                    pass
        return 0.0

    return first_nonzero(r, send_cols), first_nonzero(r, auth_cols)


# ============================================
# 카카오 요약 dict 생성
# ============================================
def build_kakao_summary_row(kakao_df: pd.DataFrame, rates_df: pd.DataFrame, settle_id: str):
    sub = kakao_df[kakao_df.get("Settle ID", "").astype(str) == str(settle_id)]
    if sub.empty:
        return {"발송료": 0, "인증료": 0, "부가세": 0, "총금액": 0}

    send_rate, auth_rate = pick_kakao_rates(rates_df, settle_id)

    send_cols = ["발송 건수", "발송건수", "총 발송 건수"]
    auth_cols = ["열람 시 인증 건수", "인증건수", "인증 건수"]

    def sum_first_exist(df, cols):
        for c in cols:
            if c in df.columns:
                return float(df[c].fillna(0).sum())
        return 0.0

    send_cnt = sum_first_exist(sub, send_cols)
    auth_cnt = sum_first_exist(sub, auth_cols)

    send_amt = int(round(send_cnt * send_rate))
    auth_amt = int(round(auth_cnt * auth_rate))
    base = send_amt + auth_amt

    vat = int(round(base * 0.1))
    total = base + vat

    return {
        "발송료": send_amt,
        "인증료": auth_amt,
        "부가세": vat,
        "총금액": total,
    }


# ============================================
# 카카오 상세 DF 생성
# ============================================
def build_kakao_detail_df(kakao_df: pd.DataFrame, settle_id: str):
    sub = kakao_df[kakao_df.get("Settle ID", "").astype(str) == str(settle_id)].copy()
    if sub.empty:
        return pd.DataFrame()

    want = [
        "일자",
        "발송 건수",
        "발송건수",
        "알림 수신 건수",
        "열람 건수",
        "열람 시 인증 건수",
    ]

    cols = [c for c in want if c in sub.columns]
    return sub[cols] if cols else sub

# ============================================
# Settlement Page
# ============================================
def settlement_page():

    st.markdown("<div class='title-text'>📑 전자고지 정산 · 대금청구서 생성</div>", unsafe_allow_html=True)
    st.write("")
    st.write("업로드 → 요약 → 누락확인 → PDF 생성까지 한 번에 수행합니다.")
    st.write("---")

    # 1) 파일 업로드
    st.subheader("1️⃣ 정산 엑셀 업로드")
    col1, col2 = st.columns(2)

    with col1:
        kakao_file = st.file_uploader("카카오 월별 정산 엑셀 업로드", type=["xlsx", "xls"], key="kakao_upload")
    with col2:
        master_file = st.file_uploader("아이앤텍 2025 정산 시트 업로드", type=["xlsx", "xls"], key="master_upload")

    if kakao_file is None or master_file is None:
        st.info("두 파일 모두 업로드하면 다음 단계 진행됩니다.")
        return

    st.write("---")

    # 2) 시트 로드
    st.subheader("2️⃣ 시트 선택")

    kakao_df = load_excel_sheet(kakao_file, "카카오 정산 엑셀")
    if kakao_df is None:
        return

    master_xls = pd.ExcelFile(master_file)

    # 발송료 시트 선택
    rates_sheet = st.selectbox("2025 발송료 시트 선택", master_xls.sheet_names, key="rates_sheet")
    rates_df = pd.read_excel(master_xls, sheet_name=rates_sheet)

    # === 정규화 ===
    raw_cols = list(rates_df.columns)
    norm_cols = [normalize_col(c) for c in raw_cols]
    rates_df.columns = norm_cols

    col_map = {
        "기관명": "기관명",
        "기관": "기관명",
        "카카오settleid": "카카오 settle id",
        "settleid": "카카오 settle id",
        "정산발송료": "정산발송료",
        "발송료": "정산발송료",
        "정산인증료": "정산인증료",
        "인증료": "정산인증료",
        "부가세": "부가세",
        "합계": "합계",
        "합계금액": "합계",
    }

    fixed_map = {}
    for orig, new in col_map.items():
        key = normalize_col(orig)
        if key in rates_df.columns:
            fixed_map[key] = new

    rates_df.rename(columns=fixed_map, inplace=True)

    st.success(f"발송료 시트 로드 완료 (행 {len(rates_df)})")
    with st.expander("발송료 시트 미리보기"):
        st.dataframe(rates_df.head(30), use_container_width=True)

    # 기안자료 시트 선택
    drafts_sheet = st.selectbox("기안자료 시트 선택", master_xls.sheet_names, key="drafts_sheet")
    drafts_df = pd.read_excel(master_xls, sheet_name=drafts_sheet)
    st.success(f"기안자료 '{drafts_sheet}' 로드 (행 {len(drafts_df)})")

    with st.expander("기안자료 미리보기"):
        st.dataframe(drafts_df.head(30), use_container_width=True)

    st.write("---")

    # 3) 요약 분석
    st.subheader("3️⃣ 정산 요약 · 누락기관 분석")

    processor = SettlementProcessor(rates_df=rates_df, drafts_df=drafts_df, kakao_df=kakao_df)
    summary = SettlementSummary(kakao_df=kakao_df, rates_df=rates_df, drafts_df=drafts_df)
    missing_det = MissingFinder(kakao_df=kakao_df, master_settle_df=rates_df)

    summary_dict = summary.build_summary_dict()

    # 요약 카드 표시
    colA, colB, colC = st.columns(3)
    totals = summary_dict["총매출"]
    colA.metric("카카오 총액", f"{totals['카카오 총액']:,} 원")
    colB.metric("다수기관 총액", f"{totals['다수기관 총액']:,} 원")
    colC.metric("전체 총액", f"{totals['전체 총액']:,} 원")

    st.write("---")

    # 누락기관
    st.markdown("### ⚠ 누락된 Settle ID 보기")

    missing_ids = missing_det.get_missing_settle_ids()
    if not missing_ids:
        st.success("누락된 Settle ID가 없습니다.")
    else:
        missing_df = missing_det.to_dataframe()
        st.dataframe(missing_df, use_container_width=True)

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as w:
            missing_df.to_excel(w, index=False)
        st.download_button(
            "누락기관 Excel 다운로드",
            data=buf.getvalue(),
            file_name="missing_settle_id.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.write("---")

    # ==========================================================
    # 4) 카카오 단일기관 PDF ZIP 생성 (멀티 선택)
    # ==========================================================
    st.subheader("4️⃣ 카카오 단일기관 PDF ZIP 생성")

    kakao_ids = {str(x).strip() for x in kakao_df.get("Settle ID", []) if str(x).strip()}
    master_ids = {str(x).strip() for x in rates_df.get("카카오 settle id", []) if str(x).strip()}
    available_ids = sorted(list(kakao_ids & master_ids))

    if not available_ids:
        st.info("카카오 통계 + 발송료 시트 공통 Settle ID 없음.")
    else:
        selected_ids = st.multiselect(
            "PDF 생성할 Settle ID 선택 (여러 개 선택 가능)",
            available_ids,
            default=available_ids,  # 전체선택 기본
            key="multi_kakao_sid",
        )

        if st.button("📦 ZIP 묶어서 다운로드 (단일기관 PDF 전체)", key="btn_kakao_zip"):
            mem_zip = io.BytesIO()
            with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as zf:

                for sid in selected_ids:
                    org_row = rates_df[rates_df["카카오 settle id"].astype(str) == str(sid)]
                    org_name = org_row.iloc[0]["기관명"] if ("기관명" in org_row.columns and not org_row.empty) else f"SID_{sid}"

                    summary_row = build_kakao_summary_row(kakao_df, rates_df, sid)
                    detail_df = build_kakao_detail_df(kakao_df, sid)

                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp_path = tmp.name

                    generate_kakao_pdf(tmp_path, org_name, sid, summary_row, detail_df)

                    with open(tmp_path, "rb") as f:
                        zf.writestr(f"{org_name}_카카오_{sid}.pdf", f.read())

            st.download_button(
                "📥 단일기관 ZIP 다운로드",
                data=mem_zip.getvalue(),
                file_name="카카오단일기관_pdf.zip",
                mime="application/zip",
            )

    st.write("---")

    # ==========================================================
    # 5) 다수기관 PDF ZIP 생성 (멀티 선택)
    # ==========================================================
    st.subheader("5️⃣ 다수기관 PDF ZIP 생성")

    if "기관명" not in rates_df.columns:
        st.error("발송료 시트에 '기관명' 컬럼이 없습니다. (다수기관 불가)")
        return

    org_list = sorted(rates_df["기관명"].dropna().astype(str).unique().tolist())

    selected_orgs = st.multiselect(
        "PDF 생성할 기관 선택 (여러 개 선택 가능)",
        org_list,
        default=org_list,  # 기본 전체선택
        key="multi_org_select",
    )

    if st.button("📦 ZIP 묶어서 다운로드 (다수기관 PDF)", key="btn_multi_zip"):

        mem_zip = io.BytesIO()
        with zipfile.ZipFile(mem_zip, "w", zipfile.ZIP_DEFLATED) as zf:

            for org_name in selected_orgs:
                org_rows_df = rates_df[rates_df["기관명"].astype(str) == org_name].copy()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp_path = tmp.name

                generate_multi_pdf(tmp_path, org_rows_df)

                with open(tmp_path, "rb") as f:
                    zf.writestr(f"{org_name}_다수기관.pdf", f.read())

        st.download_button(
            "📥 다수기관 ZIP 다운로드",
            data=mem_zip.getvalue(),
            file_name="다수기관_pdf.zip",
            mime="application/zip",
        )
