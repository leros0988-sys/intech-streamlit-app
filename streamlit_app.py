import time
import streamlit as st
from app.login_page import login_page
from app.main_page import main_page
from app.settings_page import settings_page
from app.kakao_stats_page import kakao_stats_page
from app.kt_stats_page import kt_stats_page
from app.naver_stats_page import naver_stats_page
from app.upload_page import upload_page
from app.document_page import document_page
from app.logs_page import logs_page
from app.finance_page import finance_page
from app.partner_page import partner_page

LOGIN_TIMEOUT = 1800  # 30min
MAX_FAIL = 5

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "last_action" not in st.session_state:
    st.session_state.last_action = time.time()

if "fail_count" not in st.session_state:
    st.session_state.fail_count = 0

# -----------------------------------
# 자동 로그아웃 검사
# -----------------------------------
def check_timeout():
    if not st.session_state.logged_in:
        return
    now = time.time()
    if now - st.session_state.last_action > LOGIN_TIMEOUT:
        st.warning("30분 이상 활동 없음 → 자동 로그아웃 되었습니다.")
        st.session_state.logged_in = False
        return True
    st.session_state.last_action = now
    return False


# -----------------------------------
# 로그인 처리
# -----------------------------------
if not st.session_state.logged_in:
    login_page()
    st.stop()

if check_timeout():
    st.stop()

# -----------------------------------
# 사이드바 메뉴
# -----------------------------------
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
        "로그아웃"
    ]
)

# -----------------------------------
# 페이지 라우팅
# -----------------------------------

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

elif menu == "로그 조회":
    logs_page()

elif menu == "관리자 메뉴":
    st.info("추후 관리자 전용 기능 추가 가능")

elif menu == "설정":
    settings_page()

elif menu == "로그아웃":
    st.session_state.logged_in = False
    st.rerun()

