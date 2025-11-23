import time
import streamlit as st

from app.login_page import login_page
from app.main_page import main_page
from app.settings_page import settings_page
from app.upload_page import upload_page
from app.kakao_stats_page import kakao_stats_page
from app.kt_stats_page import kt_stats_page
from app.naver_stats_page import naver_stats_page
from app.partner_page import partner_page
from app.document_page import document_page
from app.logs_page import logs_page  # 없으면 빈 페이지로 만들어둬도 됨
from app.finance_page import finance_page  # 예전 페이지 쓰고 있으면 유지
from app.utils.loader import load_settings


def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "last_action" not in st.session_state:
        st.session_state.last_action = None


def check_timeout():
    """자동 로그아웃 체크"""
    settings = load_settings()
    auto_minutes = int(settings.get("auto_logout_minutes", 30))

    if not st.session_state.logged_in:
        return False

    now = time.time()
    if st.session_state.last_action is None:
        st.session_state.last_action = now
        return False

    if now - st.session_state.last_action > auto_minutes * 60:
        st.warning(f"{auto_minutes}분 이상 활동이 없어 자동 로그아웃 되었습니다.")
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.last_action = None
        return True

    # 활동 있음 → 타임스탬프 갱신
    st.session_state.last_action = now
    return False


def run_app():
    init_session()

    if not st.session_state.logged_in:
        login_page()
        return

    if check_timeout():
        # 자동 로그아웃된 경우
        login_page()
        return

    # --------------------------
    # 사이드바 메뉴
    # --------------------------
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
        ],
    )

    # --------------------------
    # 라우팅
    # --------------------------
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
        st.info("여기에 관리자 전용 기능을 추가할 수 있습니다.")

    elif menu == "로그 조회":
        logs_page()

    elif menu == "설정":
        settings_page()

    elif menu == "로그아웃":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.last_action = None
        st.success("로그아웃 되었습니다.")
        login_page()


if __name__ == "__main__":
    run_app()
