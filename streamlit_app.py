import streamlit as st
from app.style import apply_global_styles
from app.login_page import login_page
from app.main_page import main_page
from app.sidebar_menu import draw_sidebar
from app.admin_page import admin_page
from app.finance_page import finance_page

# ----------------------------
# 세션 기본값 설정
# ----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None

# ----------------------------
# 페이지 라우팅
# ----------------------------
def run_app():
    apply_global_styles()

    # 로그인 이전 → 로그인 화면만
    if not st.session_state.logged_in:
        login_page()
        return
    
    # 로그인 이후 → 사이드바 표시
    menu = draw_sidebar()

    if menu == "메인":
        main_page()
    elif menu == "정산 관리":
        finance_page()
    elif menu == "관리자":
        admin_page()
    elif menu == "로그아웃":
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.session_state.user = None
        st.rerun()

# 실행
run_app()
