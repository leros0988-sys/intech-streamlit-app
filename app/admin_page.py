import streamlit as st

def admin_page():

    if st.session_state.user != "admin":
        st.error("관리자만 접근 가능합니다.")
        return

    st.markdown('<div class="title-text">🔧 관리자 메뉴</div>', unsafe_allow_html=True)

    st.markdown('<div class="cute-box">', unsafe_allow_html=True)
    st.write("• 사용자 계정 설정")
    st.write("• 시스템 점검")
    st.write("• 로그 기록 조회")
    st.write("• 발송 통계 확인")
    st.markdown('</div>', unsafe_allow_html=True)

