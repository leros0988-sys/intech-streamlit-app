import streamlit as st
from app.utils.logger import load_login_logs


def logs_page():

    st.markdown("## 📝 로그인 로그 조회")

    logs = load_login_logs()   # 리스트 반환됨

    if not logs or len(logs) == 0:
        st.info("아직 기록된 로그인 로그가 없습니다.")
        return

    # 리스트 → DataFrame 변환 (표시용)
    df = [{"로그기록": line} for line in logs]

    st.dataframe(df, use_container_width=True)

    st.markdown("### 🔍 필터")
    keyword = st.text_input("검색어 입력", "")

    if keyword:
        filtered = [line for line in logs if keyword in line]
        filtered_df = [{"로그기록": line} for line in filtered]
        st.dataframe(filtered_df, use_container_width=True)
