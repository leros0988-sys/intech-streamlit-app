import streamlit as st

USER_CREDENTIALS = {
    "intech2001": "Qtncjwkrwndlqcjrowls40#",
    "intech2014": "vlftkwmrtodWW^^"
}

def login_page():
    st.markdown('<div class="title-text">e mobile 정산 대시보드</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-text">로그인을 해주세요。</div>', unsafe_allow_html=True)

    user = st.text_input("ID 를 입력해주세요")
    password = st.text_input("PASSWORD 를 입력해주세요", type="password")

    if st.button("로그인"):
        if user in USER_CREDENTIALS and USER_CREDENTIALS[user] == password:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.session_state.page = "main"
            st.rerun()
        else:
            st.error("IDまたはパスワードが正しくありません")

