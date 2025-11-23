import streamlit as st
import pandas as pd

from app.utils.validator import validate_uploaded_files
from app.utils.loader import load_rate_table, load_partner_db

def upload_page():
    st.markdown("## 📂 정산 업로드 및 전체 통계자료")

    file = st.file_uploader("정산 엑셀 업로드 (카카오/KT/네이버 통합 or 월별 통계)", type=["xlsx", "xls"])

    if file is None:
        st.info("먼저 정산 엑셀을 업로드해주세요.")
        return

    try:
        df = pd.read_excel(file)
    except Exception as e:
        st.error(f"엑셀 읽기 오류: {e}")
        return

    # 세션에 저장 → 다른 페이지에서 공통 사용
    st.session_state["raw_df"] = df

    st.success(f"✅ 업로드 완료! (rows: {len(df)})")

    # 검증 메시지
    warnings = validate_uploaded_df(df)
    for msg in warnings:
        st.warning(msg)

    st.markdown("### 🔎 원본 일부")
    st.dataframe(df.head(50), use_container_width=True)

    # 간단 집계
    st.markdown("### 📊 간단 집계")

    total_rows = len(df)
    st.write(f"- 총 행 수: **{total_rows:,}**")

    amount_col = None
    for cand in ["금액", "청구금액", "정산금액", "합계"]:
        if cand in df.columns:
            amount_col = cand
            break

    if amount_col:
        total_amount = df[amount_col].fillna(0).sum()
        st.write(f"- {amount_col} 합계: **{total_amount:,} 원**")
    else:
        st.write("- 금액 컬럼(금액/청구금액/정산금액/합계)을 찾지 못했습니다.")
