# app/logs_page.py

import streamlit as st
from app.utils.logger import read_logs

def logs_page():
    st.markdown("## 📜 시스템 로그 조회")

    logs = read_logs()

    if not logs:
        st.info("아직 기록된 로그가 없습니다.")
        return

    for line in reversed(logs):
        st.markdown(f"<div style='padding:6px 0;'>{line}</div>", unsafe_allow_html=True)
