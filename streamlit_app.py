import datetime as dt
import streamlit as st

from app.style import set_page_style
from app.components.sidebar_menu import draw_sidebar

from app.login_page import login_page
from app.main_page import main_page
from app.upload_page import upload_page
from app.kakao_stats_page import kakao_stats_page
from app.kt_stats_page import kt_stats_page
from app.naver_stats_page import naver_stats_page
from app.partner_page import partner_page
from app.document_page import document_page
from app.logs_page import logs_page
from app.admin_page import admin_page
from app.settings_page import settings_page

from utils.logger import log_login_event, log_logout_event


# -----------------------------
#  사용자 계정 설정
# -----------------------------
# role: "admin" 이면 관리자 메뉴 노출, "user" 면 일반 계정
USER_CREDENTIALS = {
    "intech2001": {"password": "1234", "role": "admin"},
    "intech2014": {"password": "8888", "role": "user"},
}

MAX_FAILED_LOGIN = 5   # 5회 실패 시 잠금
DEFAULT_AUTO_LOGOUT_MIN = 30  # 기본 자동 로그아웃 30분


def init_session():
    """세션 상태 기본값 초기화"""
    defaults = {
        "logged_in": False,
        "username": None,
        "is_admin": False,
        "failed_attempts": 0,
        "locked_until": None,          # dt.datetime or None
        "last_activity": None,         # dt.datetime or None
        "auto_logout_minutes": DEFAULT_AUTO_LOGOUT_MIN,
        "main_image_path": "app/images/default_usagi_kuma.png",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "rate_table_path": "rate_table.xlsx",
        "partner_db_path": "partner_db.xlsx",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def is_account_locked() -> bool:
    """계정 잠금 여부 확인"""
    locked_until = st.session_state.get("locked_until")
    if locked_until is None:
        return False

    now = dt.datetime.now()
    if now < locked_until:
        remain = locked_until - now
        minutes = int(remain.total_seconds() // 60)
        seconds = int(remain.total_seconds() % 60)
        st.error(
            f"⚠️ 로그인 실패 {MAX_FAILED_LOGIN}회로 계정이 잠겼습니다. "
            f"약 {minutes}분 {seconds}초 후 다시 시도하세요."
        )
        return True

    # 잠금 시간 지났으면 해제
    st.session_state["locked_until"] = None
    st.session_state["failed_attempts"] = 0
    return False


def update_last_activity():
    st.session_state["last_activity"] = dt.datetime.now()


def check_auto_logout():
    """마지막 활동 후 auto_logout_minutes 경과하면 자동 로그아웃"""
    if not st.session_state.get("logged_in"):
        return

    last = st.session_state.get("last_activity")
    minutes = st.session_state.get("auto_logout_minutes", DEFAULT_AUTO_LOGOUT_MIN)
    if last is None:
        update_last_activity()
        return

    now = dt.datetime.now()
    delta = now - last
    if delta.total_seconds() > minutes * 60:
        username = st.session_state.get("username")
        log_logout_event(username, reason="auto_logout")
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["is_admin"] = False
        st.session_state["last_activity"] = None

        st.warning("⏰ 장시간 활동이 없어 자동 로그아웃되었습니다. 다시 로그인해주세요.")
        st.stop()


def handle_login_flow():
    """로그인 처리 + 실패/잠금 관리"""
    if is_account_locked():
        st.stop()

    username, password, submitted = login_page()

    if not submitted:
        st.stop()

    user_info = USER_CREDENTIALS.get(username)

    # 비밀번호 검증
    if user_info and user_info["password"] == password:
        # 성공
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["is_admin"] = user_info["role"] == "admin"
        st.session_state["failed_attempts"] = 0
        st.session_state["locked_until"] = None
        update_last_activity()

        log_login_event(username, status="success")
        st.success(f"✅ {username}님 환영합니다!")
    else:
        # 실패
        st.session_state["failed_attempts"] += 1
        failed = st.session_state["failed_attempts"]
        log_login_event(username or "UNKNOWN", status="failed")

        if failed >= MAX_FAILED_LOGIN:
            # 10분 잠금 (원하면 숫자 바꿔도 됨)
            st.session_state["locked_until"] = dt.datetime.now() + dt.timedelta(minutes=10)
            st.error(
                f"로그인 실패가 {failed}회 발생하여 계정이 잠겼습니다. "
                "10분 후 다시 시도해주세요."
            )
        else:
            remain = MAX_FAILED_LOGIN - failed
            st.error(f"아이디 또는 비밀번호가 올바르지 않습니다. (남은 시도: {remain}회)")

        st.stop()


def handle_logout(manual: bool = True):
    """로그아웃 처리"""
    username = st.session_state.get("username")
    log_logout_event(username, reason="manual" if manual else "system")

    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["is_admin"] = False
    st.session_state["last_activity"] = None


def route_menu(menu: str):
    """사이드바 메뉴에 따라 페이지 라우팅"""
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
        handle_logout(manual=True)
        st.success("👋 로그아웃되었습니다. 다시 로그인하려면 아이디와 비밀번호를 입력하세요.")
    else:
        main_page()


def run_app():
    set_page_style()
    init_session()

    # 자동 로그아웃 체크
    check_auto_logout()

    if not st.session_state.get("logged_in"):
        handle_login_flow()
        # 로그인 성공 후 다시 실행되면서 아래 로직으로 넘어감

    # 로그인 상태라면 마지막 활동 갱신
    update_last_activity()

    # 사이드바 그리기 (관리자 여부 전달)
    menu = draw_sidebar(is_admin=st.session_state.get("is_admin", False))

    # 메인 영역 라우팅
    route_menu(menu)


if __name__ == "__main__":
    run_app()

