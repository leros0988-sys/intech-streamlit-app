import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))

import streamlit as st
from app.login_page import login_page
from app.main_page import main_page
...


# 스타일
from app.style import apply_global_styles

# 페이지들
from app.login_page import login_page
from app.main_page import main_page
from app.finance_page import finance_page
from app.upload_page import upload_page
from app.kakao_stats_page import kakao_stats_page
from app.kt_stats_page import kt_stats_page
from app.naver_stats_page import naver_stats_page
from app.partner_page import partner_page
from app.gian_page import gian_page
from app.logs_page import logs_page
from app.admin_page import admin_page
from app.settings_page import settings_page

# -------------------------------------------------------
# Session 초기값 설정
# -------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "login"

# -------------------------------------------------------
# 페이지 라우팅
# -------------------------------------------------------
def run_app():

    apply_global_styles()

    # ------------------------------
    # 로그인 안 되었으면 로그인 페이지로
    # ------------------------------
    if not st.session_state.logged_in:
        login_page()
        return

    # ------------------------------
    # 로그인 이후: 좌측 메뉴
    # ------------------------------
    menu = st.sidebar.radio(
        "📌 메뉴",
        [
            "메인 대시보드",
            "정산 업로드 및 전체 통계자료",
            "카카오 통계자료",
            "KT 통계자료",
            "네이버 통계자료",
            "협력사 정산",
            "기안 자료 생성",
            "관리자 메뉴",
            "로그 조회",
            "설정",
            "로그아웃",
        ]
    )

    # ------------------------------
    # 메뉴 이동
    # ------------------------------
    if menu == "메인 대시보드":
        main_page()
    elif menu == "정산 업로드 및 전체 통계자료":
        upload_page()
    elif menu == "카카오 통계자료":
        kakao_stats_page()
    elif menu == "KT 통계자료":
        kt_stats_page()
    elif menu == "네이버 통계자료":
        naver_stats_page()
    elif menu == "협력사 정산":
        partner_page()
    elif menu == "기안 자료 생성":
        document_page()
    elif menu == "관리자 메뉴":
        admin_page()
    elif menu == "로그 조회":
        logs_page()
    elif menu == "설정":
        settings_page()
    elif menu == "로그아웃":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()


# -------------------------------------------------------
# 앱 실행
# -------------------------------------------------------
if __name__ == "__main__":
    run_app()
