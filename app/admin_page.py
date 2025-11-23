import streamlit as st


def admin_page():
    st.markdown("## 🛠 관리자 전용 메뉴")

    st.info(
        """
        이 영역은 **관리자 계정**으로 로그인했을 때만 접근 가능합니다.  
        - 로그인 로그 확인 → **로그 조회** 메뉴  
        - 시스템/파일 경로/이미지/보안 값 설정 → **설정** 메뉴  

        여기서는 간단히 현재 세션 상태를 요약해서 보여줍니다.
        """
    )

    st.markdown("### 세션 요약")
    keys = [
        "username",
        "is_admin",
        "auto_logout_minutes",
        "rate_table_path",
        "partner_db_path",
        "main_image_path",
        "youtube_url",
    ]
    for k in keys:
        st.write(f"- **{k}**: `{st.session_state.get(k)}`")


