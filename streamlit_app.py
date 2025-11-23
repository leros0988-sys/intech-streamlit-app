import streamlit as st
from components.sidebar_menu import draw_sidebar

from app.main_page import main_page
from app.finance_page import finance_page
from app.kakao_stats_page import kakao_stats_page
from app.kt_stats_page import kt_stats_page
from app.naver_stats_page import naver_stats_page
from app.partner_page import partner_page
from app.document_page import document_page
from app.admin_page import admin_page
from app.logs_page import logs_page


def run_app():

    if "page" not in st.session_state:
        st.session_state["page"] = "main"

    draw_sidebar()

    page = st.session_state["page"]

    if page == "main":
        main_page()
    elif page == "finance":
        finance_page()
    elif page == "kakao":
        kakao_stats_page()
    elif page == "kt":
        kt_stats_page()
    elif page == "naver":
        naver_stats_page()
    elif page == "partner":
        partner_page()
    elif page == "document":
        document_page()
    elif page == "logs":
        logs_page()
    elif page == "admin":
        admin_page()
    else:
        main_page()


if __name__ == "__main__":
    run_app()

