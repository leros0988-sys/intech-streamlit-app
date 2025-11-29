import streamlit as st

# ---- 스타일 유지 ----
from app.style import apply_global_styles

# ---- 페이지 import ----
from app.login_page import login_page
from app.main_page import main_page
from app.upload_page import upload_page
from app.finance_page import finance_page
from app.gian_page import gian_page
from app.logs_page import logs_page
from app.partner_page import partner_page
from app.kakao_stats_page import kakao_stats_page
from app.kt_stats_page import kt_stats_page
from app.naver_stats_page import naver_stats_page
from app.admin_page import admin_page
from app.settings_page import settings_page


# ---------------------------------------
# 🔵 Session 초기 설정 (초기화 방지 구조)
# ---------------------------------------
def init_session():
    defaults = {
        "logged_in": False,
        "user": None,
        "is_admin": False,
        "page": "login",
        "raw_combined_df": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------
# 🔵 페이지 라우팅 컨트롤러
# ---------------------------------------
def route_to(page_name: str):
    """rerun 지옥 피하면서 페이지 변경"""
    st.session_state.page = page_name
    st.session_state["_last_page"] = page_name


# ---------------------------------------
# 🔵 전체 앱 실행
# ---------------------------------------
def run_app():
    # 기본 세션 로딩
    init_session()

    # 전역 스타일 적용
    apply_global_styles()

    # 로그인 안 되어 있으면 무조건 로그인페이지만 노출
    if not st.session_state.logged_in:
        login_page()
        return

    # ----------------------------
    # 🔵 좌측 사이드바 (안정형)
    # ----------------------------
    menu = st.sidebar.radio(
        "📌 메뉴",
        [
            "메인 대시보드",
            "정산 업로드 및 전체 통계자료",
            "정산 처리 페이지",
            "카카오 통계자료",
            "KT 통계자료",
            "네이버 통계자료",
            "협력사 정산",
            "기안 자료 생성",
            "로그 조회",
            "관리자 메뉴",
            "설정",
            "로그아웃",
        ],
        index=[
            "메인 대시보드",
            "정산 업로드 및 전체 통계자료",
            "정산 처리 페이지",
            "카카오 통계자료",
            "KT 통계자료",
            "네이버 통계자료",
            "협력사 정산",
            "기안 자료 생성",
            "로그 조회",
            "관리자 메뉴",
            "설정",
            "로그아웃",
        ].index(st.session_state.get("_last_page", "메인 대시보드")),
    )

    # 로그아웃 처리
    if menu == "로그아웃":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.is_admin = False
        st.session_state.page = "login"
        st.session_state["_last_page"] = "login"
        st.rerun()

    # 현재 페이지로 기록
    route_to(menu)

    # ----------------------------
    # 🔵 라우팅 (절대 초기화 안 됨)
    # ----------------------------
    match st.session_state.page:

        case "메인 대시보드":
            main_page()

        case "정산 업로드 및 전체 통계자료":
            upload_page()

        case "정산 처리 페이지":
            finance_page()

        case "카카오 통계자료":
            kakao_stats_page()

        case "KT 통계자료":
            kt_stats_page()

        case "네이버 통계자료":
            naver_stats_page()

        case "협력사 정산":
            partner_page()

        case "기안 자료 생성":
            gian_page()

        case "로그 조회":
            logs_page()

        case "관리자 메뉴":
            admin_page()

        case "설정":
            settings_page()

        case _:
            main_page()


# ---------------------------------------
# 🔵 앱 시작
# ---------------------------------------
if __name__ == "__main__":
    run_app()
