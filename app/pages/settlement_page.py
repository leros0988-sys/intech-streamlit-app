import io
import tempfile
from typing import Optional

import pandas as pd
import streamlit as st

from app.settlement.processor import SettlementProcessor
from app.settlement.missing import MissingFinder
from app.settlement.summary import SettlementSummary
from app.settlement.pdf_generator import generate_kakao_pdf, generate_multi_pdf


# ------------------------------------------------------
# 엑셀 시트 로더
# ------------------------------------------------------
def load_excel_sheet(uploaded_file, label: str) -> Optional[pd.DataFrame]:
    if uploaded_file is None:
        st.info(f"{label} 엑셀 파일을 업로드해주세요.")
        return None

    try:
        xls = pd.ExcelFile(uploaded_file)
    except Exception as e:
        st.error(f"{label} 엑셀을 열 수 없습니다: {e}")
        return None

    sheet_name = st.selectbox(
        f"{label}에서 사용할 시트 선택",
        xls.sheet_names,
        key=f"{label}_sheet",
    )

    try:
        df = pd.read_excel(xls, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"{label} 시트 로드 실패: {e}")
        return None

    st.success(f"{label} 시트 '{sheet_name}' 로드 완료 (행 {len(df)})")
    with st.expander(f"{label} 미리보기 (상위 30행)"):
        st.dataframe(df.head(30), use_container_width=True)

    return df


# ------------------------------------------------------
# 카카오 통계 요약용 함수
# ------------------------------------------------------
def pick_kakao_rates(rates_df: pd.DataFrame, settle_id: str):
    row = rates_df[rates_df.get("카카오 settle id", "").astype(str) == str(settle_id)]
    if row.empty:
        return 0, 0

    r = row.iloc[0]

    send_cols = ["(1)발송료", "(2)발송료", "(3)발송료"]
    auth_cols = ["(1)인증료", "(2)인증료", "(3)인증료"]

    def first_nonzero(rr, cols):
        for c in cols:
            if c in rr and pd.notna(rr[c]):
                try:
                    v = float(rr[c])
                    if v != 0:
                        return v
                except:
                    pass
        return 0

    send = first_nonzero(r, send_cols)
    auth = first_nonzero(r, auth_cols)
    return send, auth


def build_kakao_summary_row(kakao_df, rates_df, settle_id):
    sub = kakao_df[kakao_df["Settle ID"].astype(str) == str(settle_id)]
    if sub.empty:
        return {"발송료": 0, "인증료": 0, "부가세": 0, "총금액": 0}

    send_rate, auth_rate = pick_kakao_rates(rates_df, settle_id)

    send_cols = ["발송 건수", "발송건수", "총 발송 건수"]
    auth_cols = ["열람 시 인증 건수", "인증건수", "인증 건수"]

    def sum_first(df, cols):
        for c in cols:
            if c in df.columns:
                return float(df[c].fillna(0).sum())
        return 0

    send_cnt = sum_first(sub, send_cols)
    auth_cnt = sum_first(sub, auth_cols)

    send_amt = int(send_cnt * send_rate)
    auth_amt = int(auth_cnt * auth_rate)

    base = send_amt + auth_amt
    vat = int(base * 0.1)
    total = base + vat

    return {"발송료": send_amt, "인증료": auth_amt, "부가세": vat, "총금액": total}


def build_kakao_detail_df(kakao_df, settle_id):
    sub = kakao_df[kakao_df["Settle ID"].astype(str) == str(settle_id)].copy()
    if sub.empty:
        return pd.DataFrame()

    cols = [c for c in [
        "일자",
        "발송 건수",
        "발송건수",
        "알림 수신 건수",
        "열람 건수",
        "열람 시 인증 건수",
    ] if c in sub.columns]

    return sub[cols] if cols else sub


# ------------------------------------------------------
# 본체: settlement_page()
# ------------------------------------------------------
def settlement_page():

    # 제목
    st.markdown(
        "<div class='title-text'>📑 전자고지 정산 · 대금청구서 생성</div>",
        unsafe_allow_html=True,
    )
    st.write("---")

    # 1) 파일 업로드
    st.subheader("1️⃣ 정산 파일 업로드")

    col1, col2 = st.columns(2)
    with col1:
        kakao_file = st.file_uploader("카카오 정산 엑셀 업로드", type=["xlsx", "xls"])
    with col2:
        master_file = st.file_uploader("2025 발송료 시트 업로드", type=["xlsx", "xls"])

    if kakao_file is None or master_file is None:
        st.info("두 파일 모두 업로드하면 다음 단계가 열립니다.")
        return

    st.write("---")

    # 2) 시트 로드
    st.subheader("2️⃣ 시트 선택")

    kakao_df = load_excel_sheet(kakao_file, "카카오 정산엑셀")
    if kakao_df is None:
        return

    master_xls = pd.ExcelFile(master_file)

    rates_sheet = st.selectbox("발송료 시트 선택", master_xls.sheet_names)
    rates_df = pd.read_excel(master_xls, sheet_name=rates_sheet)
    st.success(f"발송료 시트 '{rates_sheet}' 로드 완료 (행 {len(rates_df)})")

    # === 🔥 표준화 함수 정의 (핵심) ===
    def normalize_col(c):
        return str(c).replace(" ", "").replace("_", "").strip().lower()

    # ① 컬럼 이름 표준화
    rates_df.columns = [normalize_col(c) for c in rates_df.columns]

    # ② 매핑
    col_map = {
        "기관명": "기관명",
        "기관": "기관명",
        "카카오settleid": "카카오 settle id",
        "settleid": "카카오 settle id",
        "발송료": "정산발송료",
        "정산발송료": "정산발송료",
        "인증료": "정산인증료",
        "정산인증료": "정산인증료",
        "부가세": "부가세",
        "합계": "합계",
        "합계금액": "합계",
    }

    # 표준화된 컬럼명 기반 매핑
    inv_map = {normalize_col(k): v for k, v in col_map.items()}
    rates_df.rename(columns=inv_map, inplace=True)

    with st.expander("발송료 시트 미리보기"):
        st.dataframe(rates_df.head(30), use_container_width=True)

    st.write("---")

    # 3) 정산 엔진 초기화
    st.subheader("3️⃣ 요약 · 누락기관 분석")

    processor = SettlementProcessor(rates_df=rates_df, drafts_df=None, kakao_df=kakao_df)
    summary = SettlementSummary(kakao_df=kakao_df, rates_df=rates_df, drafts_df=None)
    missing = MissingFinder(kakao_df=kakao_df, master_settle_df=rates_df)

    summary_dict = summary.build_summary_dict()

    col_a, col_b, col_c = st.columns(3)
    totals = summary_dict["총매출"]
    col_a.metric("카카오 총액", f"{totals['카카오 총액']:,} 원")
    col_b.metric("다수기관 총액", f"{totals['다수기관 총액']:,} 원")
    col_c.metric("전체 총액", f"{totals['전체 총액']:,} 원")

    st.markdown("### 누락된 Settle ID 목록")
    missing_ids = missing.get_missing_settle_ids()
    if not missing_ids:
        st.success("누락된 Settle ID 없음")
    else:
        df_m = missing.to_dataframe()
        st.dataframe(df_m, use_container_width=True)

    st.write("---")

    # 4) 단일기관 PDF 생성
    st.subheader("4️⃣ 카카오 단일기관 PDF 생성")

    kakao_ids = {str(x).strip() for x in kakao_df.get("Settle ID", []) if str(x).strip()}
    master_ids = {str(x).strip() for x in rates_df.get("카카오 settle id", []) if str(x).strip()}
    available_ids = sorted(list(kakao_ids & master_ids))

    if not available_ids:
        st.info("PDF 생성 가능한 Settle ID 없음")
    else:
        sid = st.selectbox("Settle ID 선택", available_ids)

        row = rates_df[rates_df["카카오 settle id"] == sid]
        org_name = row.iloc[0]["기관명"] if not row.empty and "기관명" in row.columns else f"기관_{sid}"

        if st.button("📄 단일기관 PDF 생성"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                path = tmp.name

            summary_row = build_kakao_summary_row(kakao_df, rates_df, sid)
            detail_df = build_kakao_detail_df(kakao_df, sid)

            generate_kakao_pdf(path, org_name, sid, summary_row, detail_df)

            with open(path, "rb") as f:
                st.download_button(
                    "PDF 다운로드",
                    data=f.read(),
                    file_name=f"{org_name}_카카오정산.pdf"
                )

    st.write("---")

    # 5) 다수기관 PDF 생성
    st.subheader("5️⃣ 다수기관 PDF 생성")

    if "기관명" not in rates_df.columns:
        st.info("발송료 시트에 '기관명'이 없어 생성할 수 없습니다.")
        return

    org_list = sorted(rates_df["기관명"].dropna().astype(str).unique().tolist())
    selected_org = st.selectbox("기관 선택", org_list)

    if st.button("📄 다수기관 PDF 생성"):
        rows = rates_df[rates_df["기관명"] == selected_org]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            path = tmp.name

        generate_multi_pdf(path, rows)

        with open(path, "rb") as f:
            st.download_button(
                "PDF 다운로드",
                data=f.read(),
                file_name=f"{selected_org}_다수기관정산.pdf"
            )
