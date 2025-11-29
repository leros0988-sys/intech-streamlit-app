import streamlit as st
from app.utils.stats_common import filter_by_channel, show_statistics

def naver_stats_page():
    st.markdown("## 💚 네이버 통계자료")

    df = st.session_state.get("raw_combined_df", None)

    if df is None:
        st.info("데이터가 없습니다. 먼저 업로드하세요.")
        return

    nv_df = filter_by_channel(df, ["네이버", "naver"])

    if nv_df is None or nv_df.empty:
        st.info("네이버 자료가 없습니다.")
        return

    show_statistics(nv_df, "네이버 통계자료")
