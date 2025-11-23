import streamlit as st
from components.sidebar_menu import draw_sidebar
from app.main_page import main_page
from app.finance_page import finance_page
from app.upload_page import upload_page
from app.kakao_stats_page import kakao_stats_page
from app.kt_stats_page import kt_stats_page
from app.naver_stats_page import naver_stats_page
from app.partner_page import partner_page
from app.document_page import document_page
from app.admin_page import admin_page
from app.logs_page import logs_page

def run_app():
    st.set_page_config(layout="wide")

    menu = draw_sidebar()

    if menu == "메인 대시보드":
        main_page()
    elif menu == "정산 업로드 및 전체 통계자료":
        finance_page()
    elif menu == "카카오 통계자료":
        kakao_stats_page()
    elif menu == "KT 통계자료":
        kt_stats_page()
    elif menu == "네이버 통계자료":
        naver_stats_page()
    elif menu == "협력사 정산":
        partner_page()
    elif menu == "기안 자료 생성":
        document_page()
    elif menu == "관리자 메뉴":
        admin_page()
    elif menu == "로그 조회":
        logs_page()
    elif menu == "설정":
        st.info("설정 페이지 준비중…")
    elif menu == "로그아웃":
        st.success("로그아웃 되었습니다.")

if __name__ == "__main__":
    run_app()
