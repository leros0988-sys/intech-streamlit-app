import streamlit as st

def apply_global_styles():
    st.markdown("""
    <style>
    .stApp {
        background: #ffe6ec !important;
        font-family: "Pretendard", "Noto Sans JP", sans-serif;
    }

    /* 제목 */
    .title-text {
        font-size: 42px;
        font-weight: 900;
        text-align: center;
        color: #333;
        margin-top: 20px;
    }

    .subtitle-text {
        font-size: 20px;
        text-align: center;
        color: #666;
        margin-bottom: 25px;
    }

    /* 귀여운 박스 */
    .cute-box {
        background: white;
        padding: 25px;
        border-radius: 18px;
        border: 2px solid #ffb6c9;
        box-shadow: 2px 2px 10px rgba(255, 150, 170, 0.25);
        margin-top: 20px;
    }

    /* 버튼 스타일 */
    .stButton>button {
        background-color: #ff8fb5;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 10px 25px;
        font-size: 16px;
        font-weight: bold;
    }

    .stButton>button:hover {
        background-color: #ff6f9f;
    }

    </style>
    """, unsafe_allow_html=True)

    /* 🔥 전체 사이드바 배경을 완전히 흰색으로 변경 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;