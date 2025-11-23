import streamlit as st

def apply_global_styles():
    st.markdown(
        """
        <style>

        /* 전체 앱 배경 */
        .stApp {
            background-color: #fdeff4 !important;
        }

        /* 사이드바 기본 스타일 */
        section[data-testid="stSidebar"] {
            background-color: #fdeff4 !important;
        }

        /* 사이드바 라디오버튼 글씨 */
        div[data-testid="stSidebar"] label {
            font-size: 16px !important;
            font-weight: 600 !important;
            color: #333 !important;
        }

        /* 라디오 버튼 */
        div[data-testid="stSidebar"] input[type="radio"] {
            transform: scale(1.2);
            margin-right: 8px;
        }

        /* 메인 본문 글자 */
        .stMarkdown, p, label, span {
            font-size: 16px !important;
        }

        /* 제목 스타일 */
        h1, h2, h3 {
            color: #333 !important;
            font-weight: 700 !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

