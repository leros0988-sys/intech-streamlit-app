import streamlit as st
from app.utils.logger import load_login_logs


def logs_page():
    st.markdown("## 📜 로그인 로그")

    logs = load_login_logs()
    st.dataframe(logs, use_container_width=True)

