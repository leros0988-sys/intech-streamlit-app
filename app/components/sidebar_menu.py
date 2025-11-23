import streamlit as st

def draw_sidebar():
    with st.sidebar:
        st.markdown("## 🌸 메뉴")
        return st.radio(
            "",
            ["메인", "정산 관리", "설정", "관리자", "로그아웃"],
            index=0
        )

