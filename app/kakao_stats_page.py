import streamlit as st
from app.utils.stats_common import filter_by_channel, show_statistics

def kakao_stats_page():
    st.markdown("## 💛 카카오 통계자료")

    df = st.session_state.get("raw_combined_df", None)

    # 🔥 raw DF 방탄
    if df is None:
        st.info("데이터가 없습니다. 먼저 통계 파일을 업로드하세요.")
        return

    kakao_df = filter_by_channel(df, ["카카오", "kakao"])

    # 🔥 필터 결과 방탄
    if kakao_df is None or kakao_df.empty:
        st.info("카카오 관련 데이터가 없습니다.")
        return

    show_statistics(kakao_df, "카카오 통계자료")
