import streamlit as st


def naver_stats_page():
    st.markdown("## 📨 네이버 통계자료")

    df = st.session_state.get("raw_settle_df")
    if df is None:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 엑셀을 업로드해주세요.")
        return

    channel_col = None
    for cand in ["중계자", "채널", "발송채널", "중계사"]:
        if cand in df.columns:
            channel_col = cand
            break

    if channel_col is None:
        st.error("카카오/KT/네이버를 구분할 수 있는 '중계자/채널' 컬럼을 찾을 수 없습니다.")
        st.dataframe(df.head(50), use_container_width=True)
        return

    naver_df = df[df[channel_col].astype(str).str.contains("네이버", na=False)]

    if naver_df.empty:
        st.info("네이버 건이 없습니다.")
        return

    st.markdown("### 📊 네이버 건수 요약")
    st.write(f"- 네이버 총 행 수: **{len(naver_df):,}**")

    st.dataframe(naver_df.head(100), use_container_width=True)
