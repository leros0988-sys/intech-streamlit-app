import streamlit as st
import pandas as pd
from app.utils.loader import load_settings

def naver_stats_page():
    st.markdown("## 📨 네이버 통계자료")

    df = st.session_state.get("raw_df")
    if df is None:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 엑셀을 업로드해주세요.")
        return

    naver_df = filter_by_channel(df, "네이버")
    if naver_df.empty:
        st.info("네이버 건이 없습니다.")
        return

    st.markdown("### 📊 네이버 원본 일부")
    st.dataframe(naver_df.head(100), use_container_width=True)
