import streamlit as st
from app.utils.loader import load_settings

USER_CREDENTIALS = {
    "intech2001": "Qtncjwkrwndlqcjrowls40#",
    "intech2014": "vlftkwmrtodWW^^",
}


def login_page():
    settings = load_settings()
    fail_limit = int(settings.get("login_fail_limit", 5))

    if "login_fail_count" not in st.session_state:
        st.session_state.login_fail_count = 0
    if "locked" not in st.session_state:
        st.session_state.locked = False

    st.markdown('<div class="title-text">e mobile 정산 대시보드</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">로그인을 해주세요。</div>', unsafe_allow_html=True)

    if st.session_state.locked:
        st.error(f"로그인 실패 {fail_limit}회 초과로 계정이 잠겼습니다. 잠시 후 다시 시도해주세요.")
        return

    user = st.text_input("ID 를 입력해주세요")
    password = st.text_input("PASSWORD 를 입력해주세요", type="password")

    if st.button("로그인"):
        if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == password:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.page = "main"
            st.session_state.login_fail_count = 0
            st.session_state.locked = False
            st.session_state.last_action = None  # 로그인 시 타임스탬프는 streamlit_app에서 세팅
            st.rerun()
        else:
            st.session_state.login_fail_count += 1
            remain = fail_limit - st.session_state.login_fail_count
            if remain <= 0:
                st.session_state.locked = True
                st.error(f"로그인 실패 {fail_limit}회로 계정이 잠겼습니다.")
            else:
                st.error(f"IDまたはパスワードが正しくありません (남은 시도: {remain}회)")
