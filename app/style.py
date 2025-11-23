import streamlit as st

def apply_global_styles():
    st.markdown(
        """
        <style>

        /* 전체 배경 */
        .stApp {
            background-color: #FFEFF4 !important;
        }

        /* 사이드바 배경 → 흰색 */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
        }

        /* 사이드바 내부 패딩 조절 */
        [data-testid="stSidebar"] > div {
            padding-top: 20px !important;
        }

        /* 사이드바 라디오 버튼(메뉴) 글자 크기 */
        div[role="radiogroup"] > label > div {
            font-size: 1.1rem !important;
            font-weight: 600 !important;   /* 글자 약간 두껍게 */
        }

        /* 사이드바 이모지(앞줄의 아이콘) 숨기기 */
        .css-1y4p8pa, .css-12w0qpk {
            display: none !important;
        }

        /* 메뉴 선택된 항목 강조 */
        div[role="radiogroup"] > label[aria-checked="true"] > div {
            color: #D6336C !important;
        }

        /* 메인 컨테이너 여백 */
        .block-container {
            padding-top: 2rem !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
