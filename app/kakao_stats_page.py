# app/kakao_stats_page.py

import streamlit as st
import pandas as pd
from app.utils.stats_common import filter_by_channel, show_statistics


def kakao_stats_page():
    st.markdown("## 🟡 카카오 통계 페이지")

    if "raw_combined_df" not in st.session_state:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 파일을 업로드해주세요.")
        return

    df: pd.DataFrame = st.session_state.raw_combined_df

    # 카카오 필터링
    kakao_df = filter_by_channel(df, ["카카오", "kakao"])

    # 통계 표시
    show_statistics(kakao_df, "카카오")
