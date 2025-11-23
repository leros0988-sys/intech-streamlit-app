import streamlit as st

def apply_global_styles():
    st.markdown("""
        <style>

        /* 전체 배경 */
        .stApp {
            background-color: #FFEDEF !important;
        }

        /* 사이드바 기본 배경 (원래 회색 + 흰색 느낌) */
        section[data-testid="stSidebar"] {
            background-color: white !important;
            border-right: 1px solid #e6e6e6 !important;
        }

        /* 사이드바 메뉴 폰트 원래 크기 */
        [data-testid="stSidebar"] * {
            font-size: 16px !important;
        }

        /* 라디오버튼 (메뉴) 기본 스타일 유지 */
        .stRadio > label {
            font-size: 16px !important;
        }

        /* 입력창 디자인 (로그인 포함) */
        input[type="text"], input[type="password"] {
            background-color: #F4F7FA !important;
            border-radius: 6px !important;
        }

        </style>
    """, unsafe_allow_html=True)
