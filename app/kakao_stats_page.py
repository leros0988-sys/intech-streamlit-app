import streamlit as st


def kakao_stats_page():
    st.markdown("## 💬 카카오 통계자료")

    df = st.session_state.get("raw_settle_df")
    if df is None:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 엑셀을 업로드해주세요.")
        return

    # 중계자 / 채널 컬럼 추정
    channel_col = None
    for cand in ["중계자", "채널", "발송채널", "중계사"]:
        if cand in df.columns:
            channel_col = cand
            break

    if channel_col is None:
        st.error("카카오/KT/네이버를 구분할 수 있는 '중계자/채널' 컬럼을 찾을 수 없습니다.")
        st.dataframe(df.head(50), use_container_width=True)
        return

    kakao_df = df[df[channel_col].astype(str).str.contains("카카오", na=False)]

    if kakao_df.empty:
        st.info("카카오 건이 없습니다.")
        return

    st.markdown("### 📊 카카오 건수 요약")
    st.write(f"- 카카오 총 행 수: **{len(kakao_df):,}**")

    st.dataframe(kakao_df.head(100), use_container_width=True)
