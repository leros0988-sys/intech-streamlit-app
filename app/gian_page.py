# app/gian_page.py

import streamlit as st
import pandas as pd
from app.utils.loader import load_partner_db


def _normalize_settle_id_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    다양한 settle id 컬럼명을 하나로 통일: SETTLE_ID
    예: 'Settle ID', 'SETTLE ID', 'settle id', '카카오 settle id' 등
    """
    candidates = ["SETTLE_ID", "Settle ID", "settle id", "카카오 settle id", "카카오 Settle ID"]
    col_map = {}

    for c in df.columns:
        name = str(c).strip()
        if name in candidates:
            col_map[name] = "SETTLE_ID"

    if col_map:
        df = df.rename(columns=col_map)

    return df


def _pick_amount_column(df: pd.DataFrame) -> str | None:
    """
    금액 관련 컬럼명 추론: '총금액', '금액', '정산금액' 중 있는 것 사용
    """
    for c in ["총금액", "금액", "정산금액"]:
        if c in df.columns:
            return c
    return None


def gian_page():
    st.markdown("<div class='title-text'>📝 기안 자료 생성</div>", unsafe_allow_html=True)
    st.write("")

    # 1) finance_page에서 병합된 df가 있어야 함
    if "combined_settle_df" not in st.session_state:
        st.warning("⚠ 먼저 '정산 업로드 센터'에서 통계 엑셀을 업로드하고 병합해야 합니다.")
        return

    df = st.session_state["combined_settle_df"].copy()
    df.columns = df.columns.map(lambda x: str(x).strip())

    # 2) 기관명 / SETTLE_ID 정리
    if "기관명" not in df.columns:
        st.error("병합된 데이터에 '기관명' 컬럼이 없습니다. 기안 자료를 만들 수 없습니다.")
        st.dataframe(df.head())
        return

    df = _normalize_settle_id_column(df)

    if "SETTLE_ID" not in df.columns:
        st.error("병합된 데이터에 SETTLE ID 컬럼(예: 'Settle ID', '카카오 settle id')이 없습니다.")
        st.dataframe(df.head())
        return

    # 3) 금액 컬럼 추론 (없으면 0으로 처리)
    amount_col = _pick_amount_column(df)
    if amount_col is None:
        df["총금액"] = 0
        amount_col = "총금액"

    # 4) 기관 + SETTLE_ID 기준 요약
    summary_df = (
        df.groupby(["기관명", "SETTLE_ID"])[amount_col]
        .sum()
        .reset_index()
        .rename(columns={amount_col: "총금액"})
        .sort_values(["기관명", "SETTLE_ID"])
    )

    st.markdown("### 📑 기관·SETTLE ID별 요약")
    st.dataframe(summary_df, use_container_width=True)

    # 5) SETTLE_ID 선택
    settle_list = summary_df["SETTLE_ID"].astype(str).unique().tolist()
    if not settle_list:
        st.warning("SETTLE ID 데이터가 없습니다.")
        return

    selected_id = st.selectbox("SETTLE ID 선택", settle_list)

    selected_row = summary_df[summary_df["SETTLE_ID"].astype(str) == str(selected_id)].iloc[0]
    org_name = selected_row["기관명"]
    total_amount = selected_row["총금액"]

    # 6) 담당자 DB 로드
    try:
        partner_db = load_partner_db()
    except Exception as e:
        st.error(f"기관 담당자 DB를 불러올 수 없습니다: {e}")
        return

    partner_db.columns = partner_db.columns.map(lambda x: str(x).strip())

    if "기관명" not in partner_db.columns:
        st.error("기관 담당자 DB에 '기관명' 컬럼이 없습니다.")
        st.dataframe(partner_db.head())
        return

    p = partner_db[partner_db["기관명"] == org_name]

    if p.empty:
        담당자 = "정보 없음"
        연락처 = "정보 없음"
    else:
        담당자 = p.iloc[0].get("담당자", "정보 없음")
        연락처 = p.iloc[0].get("연락처", "정보 없음")

    # 7) 기안문 자동 생성
    st.markdown("### 🧾 자동 생성된 기안문")

    draft_text = f"""
📌 **{org_name} 전자고지 정산 기안**

1. **정산 개요**
- 기관명: **{org_name}**
- SETTLE ID: **{selected_id}**
- 정산 금액(합산): **{total_amount:,}원**

2. **담당자 정보**
- 담당자: {담당자}
- 연락처: {연락처}

3. **특이사항**
- 카카오는 일자별 통계를 필수 첨부하여야 함
- 테스트발송(D10_2T, D11_2T)은 정산 제외 처리됨

4. **첨부자료**
- 일자별 발송통계 (Excel)
- 대금청구서 (PDF)
"""

    st.text_area("기안문", draft_text, height=350)

    st.download_button(
        label="📥 기안문 다운로드 (TXT)",
        data=draft_text,
        file_name=f"기안_{org_name}_{selected_id}.txt",
        mime="text/plain"
    )
