import streamlit as st
from app.utils.logger import write_log

def login_page():

    ADMIN_ID = st.secrets["auth"]["ADMIN_ID"]
    ADMIN_PW = st.secrets["auth"]["ADMIN_PW"]
    USER_ID = st.secrets["auth"]["USER_ID"]
    USER_PW = st.secrets["auth"]["USER_PW"]

    fail_limit = 5

    if "login_fail_count" not in st.session_state:
        st.session_state.login_fail_count = 0
    if "locked" not in st.session_state:
        st.session_state.locked = False

    st.markdown('<div class="title-text">📱 e mobile 정산 대시보드</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">로그인을 해주세요。</div>', unsafe_allow_html=True)

    if st.session_state.locked:
        st.error(f"로그인 실패 {fail_limit}회 초과로 계정이 잠겼습니다.")
        return

    user = st.text_input("ID 를 입력해주세요")
    password = st.text_input("PASSWORD 를 입력해주세요", type="password")

    if st.button("로그인"):

        # --------------------------
        # 관리자 로그인
        # --------------------------
        if user == ADMIN_ID and password == ADMIN_PW:
            write_log(user, "로그인 성공 (관리자)")
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.session_state.page = "메인 대시보드"
            st.rerun()

        # --------------------------
        # 일반 사용자 로그인
        # --------------------------
        elif user == USER_ID and password == USER_PW:
            write_log(user, "로그인 성공 (일반 사용자)")
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.session_state.page = "메인 대시보드"
            st.rerun()

        # --------------------------
        # 로그인 실패
        # --------------------------
        else:
            write_log(user, "로그인 실패")
            st.session_state.login_fail_count += 1
            remain = fail_limit - st.session_state.login_fail_count

            if remain <= 0:
                st.session_state.locked = True
                st.error("로그인 실패 횟수 초과로 계정이 잠겼습니다.")
            else:
                st.error(f"IDまたはパスワードが正しくありません (남은 시도 {remain}회)")
