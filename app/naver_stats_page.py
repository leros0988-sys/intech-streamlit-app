# app/naver_stats_page.py

import streamlit as st
import pandas as pd
from app.utils.stats_common import filter_by_channel, show_statistics


def naver_stats_page():
    st.markdown("## 🟢 네이버 통계 페이지")

    if "raw_combined_df" not in st.session_state:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 파일을 업로드해주세요.")
        return

    df: pd.DataFrame = st.session_state.raw_combined_df

    # NAVER 필터링
    nv_df = filter_by_channel(df, ["네이버", "naver"])

    # 통계 표시
    show_statistics(nv_df, "NAVER")

