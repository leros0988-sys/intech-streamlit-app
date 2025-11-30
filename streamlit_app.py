# ---------------------------------------
# streamlit_app.py (도제결 완전 최종 수정 버전)
# ---------------------------------------
import streamlit as st

from app.style import apply_global_styles

# ----- 페이지들 -----
from app.login_page import login_page
from app.main_page import main_page
from app.pages.settlement_page import settlement_page
from app.logs_page import logs_page
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

    # ----------------------------------
    # 로그인 안 되어 있으면 로그인 페이지
    # ----------------------------------
    if not st.session_state.logged_in:
        login_page()
        return

    # ----------------------------------
    # 📌 사이드바 메뉴 구성
    # ----------------------------------
    if st.session_state.is_admin:
        menu_items = [
            "메인 대시보드",
            "정산 페이지",
            "로그 조회",
            "설정",
            "로그아웃",
        ]
    else:
        menu_items = [
            "메인 대시보드",
            "정산 페이지",
            "로그아웃",
        ]

    menu = st.sidebar.radio("📌 메뉴", menu_items)

    # ----------------------------------
    # 📌 로그아웃
    # ----------------------------------
    if menu == "로그아웃":
        # 🔥 key 전체 삭제 + rerun = 안전한 로그아웃
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state.clear()
        st.rerun()
        return

    # ----------------------------------
    # 📌 라우팅
    # ----------------------------------
    if menu == "메인 대시보드":
        main_page()

    elif menu == "정산 페이지":
        settlement_page()

    elif menu == "로그 조회":
        if st.session_state.is_admin:
            logs_page()
        else:
            st.error("접근 권한이 없습니다.")

    elif menu == "설정":
        if st.session_state.is_admin:
            settings_page()
        else:
            st.error("접근 권한이 없습니다.")

    else:
        main_page()


# ---------------------------------------
# 앱 시작
# ---------------------------------------
if __name__ == "__main__":
    run_app()
