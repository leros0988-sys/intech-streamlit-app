import streamlit as st
import pandas as pd

def finance_page():
    st.markdown('<div class="title-text">💰 정산 관리</div>', unsafe_allow_html=True)
    st.write("")
    
    # 탭 구성
    tab_upload, tab_settle, tab_draft, tab_partner = st.tabs(
        ["📤 파일 업로드", "📊 정산 결과", "📝 기안자료", "🤝 협력사 정산"]
    )

    # ----------------------------------------
    # 1) 📤 파일 업로드 탭
    # ----------------------------------------
    with tab_upload:
        st.subheader("📤 정산 엑셀 업로드")

        kakao_file = st.file_uploader("카카오 정산 파일 업로드", type=["xlsx"])
        kt_file = st.file_uploader("KT 정산 파일 업로드", type=["xlsx"])
        naver_file = st.file_uploader("네이버 정산 파일 업로드", type=["xlsx"])

        st.write("---")
        st.subheader("📑 기준 정보 업로드")

        rate_table = st.file_uploader("단가표(rate_table.xlsx) 업로드", type=["xlsx"])
        contact_table = st.file_uploader("기관 담당자 DB 업로드", type=["xlsx"])
        mapping_table = st.file_uploader("SETTLE ID ↔ 서식명 매핑표 업로드", type=["xlsx"])

        if st.button("📦 저장하기"):
            st.session_state["kakao"] = kakao_file
            st.session_state["kt"] = kt_file
            st.session_state["naver"] = naver_file
            st.session_state["rate"] = rate_table
            st.session_state["contact"] = contact_table
            st.session_state["mapping"] = mapping_table

            st.success("업로드 완료! 다음 탭에서 정산이 가능합니다 ✨")


    # ----------------------------------------
    # 2) 📊 정산 결과 탭
    # ----------------------------------------
    with tab_settle:
        st.subheader("📊 정산 결과")

        if "kakao" not in st.session_state:
            st.warning("⚠ 먼저 파일 업로드를 해주세요.")
        else:
            st.success("정산 로직 들어갈 영역 (자동화 계산 영역)")

            # 여기에 도제결이 제공한 정산 규칙 기반 로직 들어감
            # 카카오 / KT / 네이버 정산
            # D10_2T / D11_2T 자동 제외
            # 발송 / 인증 계산
            # 단가 매핑
            # 특이사항 검출
            # 최종 테이블 출력
            pass

    # ----------------------------------------
    # 3) 📝 기안자료 탭
    # ----------------------------------------
    with tab_draft:
        st.subheader("📝 기안자료 자동 생성")

        if "contact" not in st.session_state:
            st.warning("⚠ 담당자 DB 업로드 필요")
        else:
            st.success("기안자료 생성 로직 들어갈 자리")


    # ----------------------------------------
    # 4) 🤝 협력사 정산 탭
    # ----------------------------------------
    with tab_partner:
        st.subheader("🤝 협력사 정산 (엑스아이티 · 에프원)")

        if "kakao" not in st.session_state:
            st.warning("⚠ 먼저 파일 업로드를 해주세요.")
        else:
            st.success("협력사 정산 계산 로직 들어갈 자리")
            
