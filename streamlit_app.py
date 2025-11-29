import streamlit as st

from app.login_page import login_page
from app.main_page import main_page
from app.upload_page import upload_page
from app.finance_page import finance_page
from app.gian_page import gian_page
from app.logs_page import logs_page


# -----------------------------
# 세션 초기값
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"


# -----------------------------
# 페이지 이동 함수
# -----------------------------
def go(page_name):
    st.session_state.page = page_name
    st.experimental_rerun()


# -----------------------------
# 라우팅
# -----------------------------
def run_app():

    # 로그인 안 되어 있으면 로그인 화면만 보여줌
    if not st.session_state.logged_in:
        login_page()
        return

    # ---- 사이드 메뉴 ----
    menu = st.sidebar.radio(
        "📌 메뉴",
        [
            "메인",
            "정산 업로드 센터",
            "정산 처리 페이지",
            "기안 생성",
            "로그 조회",
            "로그아웃",
        ]
    )

    if menu == "로그아웃":
        st.session_state.logged_in = False
        st.session_state.page = "login"
        st.experimental_rerun()

    # ---- 라우팅 ----
    if menu == "메인":
        main_page()
    elif menu == "정산 업로드 센터":
        upload_page()
    elif menu == "정산 처리 페이지":
        finance_page()
    elif menu == "기안 생성":
        gian_page()
    elif menu == "로그 조회":
        logs_page()


# -----------------------------
# 앱 실행
# -----------------------------
if __name__ == "__main__":
    run_app()
