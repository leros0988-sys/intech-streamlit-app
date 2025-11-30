# ---------------------------------------
# streamlit_app.py (완전 재작성 버전)
# ---------------------------------------
import streamlit as st

from app.style import apply_global_styles

# ----- 페이지들 -----
from app.login_page import login_page
from app.main_page import main_page
from app.pages.settlement_page import settlement_page  # 🔥 새 정산 페이지
from app.logs_page import logs_page
from app.admin_page import admin_page
from app.settings_page import settings_page


# ---------------------------------------
# 🔵 Session 초기 설정
# ---------------------------------------
def init_session():
    defaults = {
        "logged_in": False,
        "user": None,
        "is_admin": False,
        "page": "login",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------
# 🔵 전체 앱 실행
# ---------------------------------------
def run_app():
    init_session()
    apply_global_styles()

    # ----------------------------
    # 로그인 안 되어 있으면 로그인 페이지
    # ----------------------------
    if not st.session_state.logged_in:
        login_page()
        return

    # ----------------------------
    # 📌 사이드바 메뉴
    # ----------------------------
    menu = st.sidebar.radio(
        "📌 메뉴",
        [
            "메인 대시보드",
            "정산 페이지",        # 🔥 정산 전체 기능 1곳에 통합
            "로그 조회",
            "관리자 메뉴",
            "설정",
            "로그아웃",
        ]
    )

    # 로그아웃
    if menu == "로그아웃":
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()

    # ----------------------------
    # 📌 라우팅
    # ----------------------------
    st.session_state.page = menu

    match menu:
        case "메인 대시보드":
            main_page()
        case "정산 페이지":
            settlement_page()
        case "로그 조회":
            logs_page()
        case "관리자 메뉴":
            admin_page()
        case "설정":
            settings_page()
        case _:
            main_page()


# ---------------------------------------
# 앱 시작
# ---------------------------------------
if __name__ == "__main__":
    run_app()
