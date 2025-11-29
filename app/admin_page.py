import streamlit as st
from app.utils.loader import load_settings, save_settings


def admin_page():
    st.markdown("## 🔧 관리자 설정")

    settings = load_settings()

    fail = st.number_input("로그인 실패 제한 횟수", 1, 10, settings.get("login_fail_limit", 5))

    if st.button("저장"):
        settings["login_fail_limit"] = fail
        save_settings(settings)
        st.success("저장되었습니다.")
