# app/naver_stats_page.py

import streamlit as st
import pandas as pd
from app.utils.stats_common import filter_by_channel, show_statistics


def naver_stats_page():
    st.markdown("## 💚 네이버 통계자료")

    # ---- 데이터 체크 ----
    df = st.session_state.get("raw_combined_df", None)

    if df is None:
        st.error("⚠ '정산 업로드 및 전체 통계자료'에서 데이터를 먼저 업로드하세요.")
        return

    if not isinstance(df, pd.DataFrame):
        st.error("⚠ 데이터 형식이 손상되었습니다. 다시 업로드해주세요.")
        return

    if df.empty:
        st.error("⚠ 업로드된 데이터가 비어 있습니다.")
        return

    # ---- 필터링 ----
    nv_df = filter_by_channel(df, ["네이버", "naver"])

    if nv_df is None or nv_df.empty:
        st.info("📂 네이버 관련 데이터가 없습니다.")
        return

    # ---- 통계 출력 ----
    show_statistics(nv_df, "네이버 통계자료")
