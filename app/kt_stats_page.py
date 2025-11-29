import streamlit as st
from app.utils.stats_common import filter_by_channel, show_statistics

def kt_stats_page():
    st.markdown("## 💙 KT 통계자료")

    df = st.session_state.get("raw_combined_df", None)

    if df is None:
        st.info("데이터가 없습니다. 먼저 업로드하세요.")
        return

    kt_df = filter_by_channel(df, ["KT", "kt"])

    if kt_df is None or kt_df.empty:
        st.info("KT 자료가 없습니다.")
        return

    show_statistics(kt_df, "KT 통계자료")
