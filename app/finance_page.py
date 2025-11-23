import streamlit as st
import pandas as pd
from utils.loader import load_rate_table, load_partner_db
from utils.validator import validate_uploaded_files

def finance_page():
    st.markdown("<h1 style='text-align:center;'>💰 정산 관리</h1>", unsafe_allow_html=True)
    st.info("정산 기능을 여기에 추가할 수 있습니다.")

    # -----------------------------------------------------
    # 1) 정산 월 선택
    # -----------------------------------------------------
    st.markdown("### 📅 정산 월 선택")
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("연도", [2024, 2025, 2026], index=1)
    with col2:
        month = st.selectbox("월", list(range(1, 13)))

    st.markdown("---")

    # -----------------------------------------------------
    # 2) 정산 파일 업로드
    # -----------------------------------------------------
    st.markdown("### 📂 카카오 · KT · 네이버 정산 파일 업로드")

    kakao_file = st.file_uploader("카카오 정산 파일 (xlsx)", type=["xlsx"], key="kakao_upload")
    kt_file = st.file_uploader("KT 정산 파일 (xlsx)", type=["xlsx"], key="kt_upload")
    naver_file = st.file_uploader("네이버 정산 파일 (xlsx)", type=["xlsx"], key="naver_upload")

    st.markdown("---")

    # -----------------------------------------------------
    # 3) 기관 DB / 정산단가 DB 자동 로드
    # -----------------------------------------------------
    with st.expander("📁 로드된 기준 DB 확인하기"):
        rate_db = load_rate_table()
        partner_db = load_partner_db()

        st.write("### ✔ 정산단가 DB (rate_table)")
        st.dataframe(rate_db)

        st.write("### ✔ 기관 담당자 DB")
        st.dataframe(partner_db)

    st.markdown("---")

    # -----------------------------------------------------
    # 4) validation 체크
    # -----------------------------------------------------
    st.markdown("### 🔍 파일 검증")

    if st.button("검증하기"):
        result = validate_uploaded_files(kakao_file, kt_file, naver_file)

        if result["status"] == "error":
            st.error(result["message"])
        else:
            st.success("업로드된 파일 구조 검증 통과 ✔")
            st.session_state["validated"] = True

    st.markdown("---")

    # -----------------------------------------------------
    # 5) 정산 실행
    # -----------------------------------------------------
    st.markdown("### ⚙ 정산 계산 실행")

    if "validated" in st.session_state and st.session_state["validated"]:
        if st.button("정산 실행"):
            st.success("정산 계산 로직이 여기 들어갈 자리입니다.")
            st.info("다음 단계에서 calculator.py 로직을 추가할게.")

    else:
        st.warning("⏳ 파일 검증 먼저 해주세요.")

    st.markdown("---")

    # -----------------------------------------------------
    # 6) 파일 다운로드 구역
    # -----------------------------------------------------
    st.markdown("### ⬇ 다운로드")

    col_a, col_b, col_c = st.columns(3)

    with col_a:
        st.download_button("📘 기관 정산 결과(엑셀)", data=b"", file_name=f"{year}_{month}_기관정산.xlsx")
    with col_b:
        st.download_button("📙 협력사 정산 결과(엑셀)", data=b"", file_name=f"{year}_{month}_협력사정산.xlsx")
    with col_c:
        st.download_button("📕 대금청구서(PDF)", data=b"", file_name=f"{year}_{month}_대금청구서.pdf")

    st.markdown("---")

    # -----------------------------------------------------
    # 7) 특이사항 로그 (누락·매핑 오류)
    # -----------------------------------------------------
    st.markdown("### 📝 특이사항 로그")
    st.info("여기에 매핑 오류, 담당자 정보 누락, 서식 매칭 오류 등을 표시할 예정입니다.")



