import streamlit as st
import pandas as pd
from app.utils.loader import load_settings



def kakao_stats_page():
    st.markdown("## 💬 카카오 통계자료")

    df = st.session_state.get("raw_df")
    if df is None:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 엑셀을 업로드해주세요.")
        return

    kakao_df = filter_by_channel(df, "카카오")
    if kakao_df.empty:
        st.info("카카오 건이 없습니다.")
        return

    st.markdown("### 📊 카카오 원본 일부")
    st.dataframe(kakao_df.head(100), use_container_width=True)

    st.markdown("### 📑 카카오 SETTLE ID별 요약")
    summary = summarize_kakao(kakao_df)
    if summary.empty:
        st.info("'카카오 settle id' 기준 집계를 할 수 없습니다.")
    else:
        st.dataframe(summary, use_container_width=True)
