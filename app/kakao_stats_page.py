# app/kakao_stats_page.py

import streamlit as st
import pandas as pd
from app.utils.stats_common import filter_by_channel, show_statistics


def kakao_stats_page():
    st.markdown("## 💛 카카오 통계자료")

    # -------------------------------------
    # 1) 업로드 데이터 체크 (방탄)
    # -------------------------------------
    df = st.session_state.get("raw_combined_df", None)

    if df is None:
        st.error("⚠ 먼저 '정산 업로드 및 전체 통계자료'에서 엑셀을 업로드해주세요.")
        return

    if not isinstance(df, pd.DataFrame):
        st.error("⚠ 업로드 데이터가 손상되었습니다. 다시 업로드해주세요.")
        return

    if df.empty:
        st.error("⚠ 업로드된 데이터가 비어 있습니다.")
        return

    # -------------------------------------
    # 2) 카카오 데이터 필터링
    # -------------------------------------
    kakao_df = filter_by_channel(df, ["카카오", "kakao"])

    if kakao_df is None or kakao_df.empty:
        st.info("📂 카카오 관련 데이터가 없습니다.")
        return

    # -------------------------------------
    # 3) 통계 표시
    # -------------------------------------
    show_statistics(kakao_df, "카카오 통계자료")
