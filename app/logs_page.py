import streamlit as st
from app.utils.logger import load_login_logs


def logs_page():
    st.markdown("## 📜 로그인 로그 조회")

    df = load_login_logs()
    if df is None or df.empty:
        st.info("아직 기록된 로그인 로그가 없습니다.")
        return

    st.dataframe(df, use_container_width=True)

    st.markdown("### 🔎 필터")
    col1, col2 = st.columns(2)
    with col1:
        user = st.text_input("사용자 필터 (부분 일치)")
    with col2:
        status = st.multiselect("상태", options=df["status"].unique().tolist())

    filtered = df.copy()
    if user:
        filtered = filtered[filtered["username"].str.contains(user, na=False)]
    if status:
        filtered = filtered[filtered["status"].isin(status)]

    st.markdown("### 결과")
    st.dataframe(filtered, use_container_width=True)
