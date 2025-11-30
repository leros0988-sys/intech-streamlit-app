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
    """
    업로드된 엑셀에서 시트 선택 → DataFrame 로드
    """
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

    st.success(f"{label} - '{sheet_name}' 시트가 로드되었습니다. (행 {len(df)})")
    with st.expander(f"{label} 미리보기 (상위 30행)"):
        st.dataframe(df.head(30), use_container_width=True)

    return df


# ------------------------------------------------------
# 유틸: 카카오 단가 계산용 헬퍼
# ------------------------------------------------------
def pick_kakao_rates(rates_df: pd.DataFrame, settle_id: str):
    """
    2025 발송료 시트에서 해당 Settle ID 행을 찾고
    (1)~(3) 발송료/인증료 중 '카카오'에 해당하는 단가 추출.
    - 단가 없으면 0 처리.
    """
    row = rates_df[rates_df.get("카카오 settle id", "").astype(str) == str(settle_id)]
    if row.empty:
        return 0, 0  # 발송단가, 인증단가

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
                except Exception:
                    continue
        return 0.0

    send_rate = first_nonzero(r, send_cols)
    auth_rate = first_nonzero(r, auth_cols)
    return send_rate, auth_rate


def build_kakao_summary_row(
    kakao_df: pd.DataFrame,
    rates_df: pd.DataFrame,
    settle_id: str,
) -> dict:
    """
    카카오 월별 통계 + 발송료 단가 기반으로
    - 발송료
    - 인증료
    - 부가세
    - 총금액
    을 계산해서 dict로 반환.
    """
    sub = kakao_df[kakao_df.get("Settle ID", "").astype(str) == str(settle_id)]
    if sub.empty:
        return {"발송료": 0, "인증료": 0, "부가세": 0, "총금액": 0}

    send_rate, auth_rate = pick_kakao_rates(rates_df, settle_id)

    # 카카오 통계에서 발송/인증 건수 컬럼 후보
    send_cols = ["발송 건수", "발송건수", "총 발송 건수"]
    auth_cols = ["열람 시 인증 건수", "인증건수", "인증 건수"]

    def sum_first_existing(df, cols):
        for c in cols:
            if c in df.columns:
                return float(df[c].fillna(0).sum())
        return 0.0

    send_cnt = sum_first_existing(sub, send_cols)
    auth_cnt = sum_first_existing(sub, auth_cols)

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


def build_kakao_detail_df(kakao_df: pd.DataFrame, settle_id: str) -> pd.DataFrame:
    """
    카카오 상세내역 테이블용 DataFrame
    - 일자 / 발송 / 알림수신 / 열람 / 인증 등 주요 컬럼만 추출
    """
    sub = kakao_df[kakao_df.get("Settle ID", "").astype(str) == str(settle_id)].copy()
    if sub.empty:
        return pd.DataFrame()

    candidates = [
        "일자",
        "발송 건수",
        "발송건수",
        "알림 수신 건수",
        "열람 건수",
        "열람 시 인증 건수",
    ]
    cols = [c for c in candidates if c in sub.columns]

    if not cols:
        return sub

    return sub[cols]


# ------------------------------------------------------
# 본체: 정산 페이지
# ------------------------------------------------------
def settlement_page():
    st.markdown(
        "<div class='title-text'>📑 전자고지 정산 · 대금청구서 생성</div>",
        unsafe_allow_html=True,
    )
    st.write("")

    st.markdown(
        """
        이 페이지에서는 다음을 한 번에 처리합니다.
        - 카카오 월별 정산 엑셀 + 2025 정산 시트 업로드
        - 정산 요약(총매출, 발행건수, VAT, 지역, TOP3, PDF 집계)
        - 누락기관(Settle ID) 자동 추출
        - 카카오 단일기관 / 다수기관 PDF 생성
        """,
    )

    st.write("---")

    # --------------------------------------------------
    # 1) 파일 업로드
    # --------------------------------------------------
    st.subheader("1️⃣ 정산 엑셀 업로드")

    col1, col2 = st.columns(2)

    with col1:
        kakao_file = st.file_uploader(
            "카카오 월별 정산 엑셀 업로드", type=["xlsx", "xls"], key="kakao_upload"
        )

    with col2:
        master_file = st.file_uploader(
            "아이앤텍 2025 정산 시트 업로드", type=["xlsx", "xls"], key="master_upload"
        )

    if kakao_file is None or master_file is None:
        st.info("두 파일을 모두 업로드하면 다음 단계가 열립니다.")
        return

    st.write("---")

    # --------------------------------------------------
    # 2) 시트 선택 및 로드
    # --------------------------------------------------
    st.subheader("2️⃣ 시트 선택")

    kakao_df = load_excel_sheet(kakao_file, "카카오 정산 엑셀")
    if kakao_df is None:
        return

    master_xls = pd.ExcelFile(master_file)

    # 발송료 시트 선택
    rates_sheet = st.selectbox(
        "2025 발송료 시트 선택",
        master_xls.sheet_names,
        key="rates_sheet",
    )
    rates_df = pd.read_excel(master_xls, sheet_name=rates_sheet)
    st.success(f"발송료 시트 '{rates_sheet}' 로드 (행 {len(rates_df)})")

    # === 발송료 시트 컬럼 표준화 ===
    rates_df.columns = [normalize_col(c) for c in rates_df.columns]

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

    rates_df.rename(columns=col_map, inplace=True)

    with st.expander("2025 발송료 미리보기 (상위 30행)"):
        st.dataframe(rates_df.head(30), use_container_width=True)

    # 기안자료 시트 선택 (필요 시)
    drafts_sheet = st.selectbox(
        "기안자료 시트 선택",
        master_xls.sheet_names,
        key="drafts_sheet",
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

    # 3-1) 요약
    summary_dict = summary.build_summary_dict()

    col_a, col_b, col_c = st.columns(3)
    totals = summary_dict["총매출"]
    with col_a:
        st.metric("카카오 총액", f"{totals['카카오 총액']:,} 원")
    with col_b:
        st.metric("다수기관 총액", f"{totals['다수기관 총액']:,} 원")
    with col_c:
        st.metric("전체 총액", f"{totals['전체 총액']:,} 원")

    bills = summary_dict["발행건수"]
    col_d, col_e, col_f = st.columns(3)
    with col_d:
        st.metric("카카오 발행 건수", f"{bills['카카오 발행 건수']:,} 건")
    with col_e:
        st.metric("다수기관 발행 건수", f"{bills['다수기관 발행 건수']:,} 건")
    with col_f:
        st.metric("전체 발행 건수", f"{bills['전체 발행 건수']:,} 건")

    vat = summary_dict["VAT요약"]
    with st.expander("부가세 요약"):
        st.write(f"- VAT 포함 총액: **{vat['VAT 포함 총액']:,} 원**")
        st.write(f"- VAT 미포함 총액: **{vat['VAT 미포함 총액']:,} 원**")
        st.write(f"- VAT 포함 기관 수: {len(vat['VAT 포함 기관'])}곳")
        st.write(f"- VAT 미포함 기관 수: {len(vat['VAT 미포함 기관'])}곳")

    region_df = summary_dict["지역별"]
    with st.expander("지역별 총액 요약"):
        if not region_df.empty:
            st.dataframe(region_df, use_container_width=True)
        else:
            st.write("지역 정보를 계산할 수 없습니다.")

    top3 = summary_dict["TOP3"]
    with st.expander("기관별 매출 TOP 3"):
        if top3:
            for name, amt in top3:
                st.write(f"- **{name}** : {amt:,} 원")
        else:
            st.write("TOP3 정보를 계산할 수 없습니다.")

    pdf_counts = summary_dict["PDF집계"]
    col_g, col_h, col_i = st.columns(3)
    with col_g:
        st.metric("카카오 PDF 대상", pdf_counts["카카오 PDF 대상"])
    with col_h:
        st.metric("다수기관 PDF 대상", pdf_counts["다수기관 PDF 대상"])
    with col_i:
        st.metric("전체 PDF 수", pdf_counts["전체 PDF"])

    # 3-2) 누락기관
    st.markdown("### ⚠ 누락기관 (카카오에는 있으나 발송료 시트에는 없는 Settle ID)")

    missing_ids = missing_det.get_missing_settle_ids()
    if not missing_ids:
        st.success("누락된 Settle ID가 없습니다. (카카오 통계 ↔ 발송료 시트 모두 매칭 완료)")
    else:
        missing_df = missing_det.to_dataframe()
        st.dataframe(missing_df, use_container_width=True)

        # 엑셀 다운로드
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            missing_df.to_excel(writer, index=False, sheet_name="missing_settle_id")
        st.download_button(
            "누락기관 목록 엑셀 다운로드",
            data=buf.getvalue(),
            file_name="누락기관_settle_id.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.write("---")

    # --------------------------------------------------
    # 4) 카카오 단일기관 PDF 생성
    # --------------------------------------------------
    st.subheader("4️⃣ 카카오 단일기관 대금청구서 PDF 생성")

    # 카카오 통계 + 발송료 모두에 존재하는 Settle ID만 대상
    kakao_ids = {
        str(x).strip()
        for x in kakao_df.get("Settle ID", [])
        if str(x).strip()
    }
    master_ids = {
        str(x).strip()
        for x in rates_df.get("카카오 settle id", [])
        if str(x).strip()
    }
    available_ids = sorted(list(kakao_ids & master_ids))

    if not available_ids:
        st.info("카카오 통계와 발송료 시트가 공통으로 가지는 Settle ID가 없습니다.")
    else:
        selected_sid = st.selectbox(
            "PDF를 생성할 카카오 Settle ID 선택", available_ids, key="kakao_pdf_sid"
        )

        # 기관명 가져오기 (발송료 시트에서)
        org_row = rates_df[rates_df["카카오 settle id"].astype(str) == str(selected_sid)]
        if not org_row.empty and "기관명" in org_row.columns:
            org_name = str(org_row.iloc[0]["기관명"])
        else:
            org_name = f"Settle ID {selected_sid}"

        if st.button("📄 카카오 단일기관 PDF 생성", key="btn_kakao_pdf"):
            # 요약/상세 데이터 준비
            summary_row = build_kakao_summary_row(kakao_df, rates_df, selected_sid)
            detail_df = build_kakao_detail_df(kakao_df, selected_sid)

            # 임시 파일에 PDF 생성 후, bytes 로 읽어서 다운로드 버튼 제공
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp_path = tmp.name

            generate_kakao_pdf(
                save_path=tmp_path,
                org_name=org_name,
                settle_id=selected_sid,
                summary_row=summary_row,
                detail_df=detail_df,
            )

            with open(tmp_path, "rb") as f:
                pdf_bytes = f.read()

            st.download_button(
                label="📥 카카오 대금청구서 PDF 다운로드",
                data=pdf_bytes,
                file_name=f"{org_name}_카카오대금청구서_{selected_sid}.pdf",
                mime="application/pdf",
            )

    st.write("---")

    # --------------------------------------------------
    # 5) 다수기관 PDF 생성
    # --------------------------------------------------
    st.subheader("5️⃣ 다수기관 대금청구서 PDF 생성")

    if "기관명" not in rates_df.columns:
        st.info("발송료 시트에 '기관명' 컬럼이 없어 다수기관 PDF를 생성할 수 없습니다.")
        return

    org_list = sorted(rates_df["기관명"].dropna().astype(str).unique().tolist())
    selected_org = st.selectbox("PDF를 생성할 기관 선택", org_list, key="multi_org_select")

    # 해당 기관의 행(보통 1행) 추출
    org_rows_df = rates_df[rates_df["기관명"].astype(str) == selected_org].copy()

    if st.button("📄 다수기관 정산 PDF 생성", key="btn_multi_pdf"):
        # 임시 파일 경로
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp_path = tmp.name

        # pdf_generator에서 다수기관용 PDF 생성
        generate_multi_pdf(
            save_path=tmp_path,
            org_rows_df=org_rows_df,
        )

        with open(tmp_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            label="📥 다수기관 대금청구서 PDF 다운로드",
            data=pdf_bytes,
            file_name=f"{selected_org}_다수기관대금청구서.pdf",
            mime="application/pdf",
        )

