import streamlit as st
import pandas as pd

from utils.loader import load_rate_table


def upload_page():
    st.markdown("## 📂 정산 업로드 및 전체 통계자료")

    st.info("D10_2, D11_2 전체 발송/인증/수신 데이터를 업로드하면 통계와 채널별 집계를 볼 수 있습니다.")

    uploaded_file = st.file_uploader(
        "카카오/KT/네이버 통합 정산 엑셀 업로드 (예: D10_2, D11_2 결과)",
        type=["xlsx", "xls"],
    )

    if uploaded_file is None:
        st.warning("먼저 정산 데이터를 업로드해주세요.")
        return

    try:
        df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"엑셀을 읽는 중 오류가 발생했습니다: {e}")
        return

    # 세션에 원본 저장 (다른 페이지에서 공통 사용)
    st.session_state["raw_settle_df"] = df

    st.success(f"✅ 데이터 업로드 완료! (rows: {len(df)})")

    st.markdown("### 🔎 원본 일부 미리보기")
    st.dataframe(df.head(50), use_container_width=True)

    st.markdown("### 📊 간단 요약 통계")

    st.write(df.describe(include="all"))

    # 요율표 불러와서 간단히 보여주기 (정상 동작 확인용)
    rate_df = load_rate_table(show_error=False)
    if rate_df is not None:
        with st.expander("요율표(rate_table.xlsx) 미리보기"):
            st.dataframe(rate_df.head(20), use_container_width=True)
