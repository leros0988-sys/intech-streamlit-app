import streamlit as st
import pandas as pd

def finance_page():
    st.markdown("<h1 style='text-align:center;'>💰 정산 관리</h1>", unsafe_allow_html=True)
    st.info("정산 기능을 여기에 추가할 수 있습니다.")

    # ------------------------------------------
    # 1) 정산 날짜 입력
    # ------------------------------------------
    date = st.date_input("정산 날짜")

    # ------------------------------------------
    # 2) 파일 업로드
    # ------------------------------------------
    st.subheader("📤 카카오/KT/네이버 발송 통계 업로드")

    kakao_file = st.file_uploader("카카오 통계 파일 업로드", type=["xlsx", "xls"], key="kakao")
    kt_file = st.file_uploader("KT 통계 파일 업로드", type=["xlsx", "xls"], key="kt")
    naver_file = st.file_uploader("네이버 통계 파일 업로드", type=["xlsx", "xls"], key="naver")

    st.markdown("---")

    # ------------------------------------------
    # 3) 계산 실행 버튼
    # ------------------------------------------
    if st.button("정산 계산 실행"):
        missing = []

        # 파일 누락 체크
        if kakao_file is None:
            missing.append("카카오")
        if kt_file is None:
            missing.append("KT")
        if naver_file is None:
            missing.append("네이버")

        if missing:
            st.error(f"❌ 다음 발송 통계 파일이 없습니다: {', '.join(missing)}")
            return

        # --------------------------------------
        # 파일 읽기
        # --------------------------------------
        try:
            kakao_df = pd.read_excel(kakao_file)
            kt_df = pd.read_excel(kt_file)
            naver_df = pd.read_excel(naver_file)
        except:
            st.error("파일을 읽는 도중 오류가 발생했습니다. 파일 형식을 확인해주세요.")
            return

        # --------------------------------------
        # 정산 로직 (임시)
        # --------------------------------------
        kakao_count = len(kakao_df)
        kt_count = len(kt_df)
        naver_count = len(naver_df)

        total_count = kakao_count + kt_count + naver_count

        st.success(f"정산이 완료되었습니다! 총 발송 {total_count}건")
        st.write(f"- 카카오 : {kakao_count} 건")
        st.write(f"- KT : {kt_count} 건")
        st.write(f"- 네이버 : {naver_count} 건")

        st.markdown("---")

        st.subheader("📝 특이사항 자동 감지")
        issues = []
        if kakao_count == 0: issues.append("카카오 통계 건수 0건")
        if kt_count == 0: issues.append("KT 통계 건수 0건")
        if naver_count == 0: issues.append("네이버 통계 건수 0건")

        if issues:
            st.warning("⚠ 다음 특이사항이 감지되었습니다:\n" + "\n".join([f"- {i}" for i in issues]))
        else:
            st.success("특이사항 없음")

    # ------------------------------------------
    # 메모 / 저장 버튼
    # ------------------------------------------
    st.markdown("---")
    memo = st.text_area("메모")
    if st.button("저장하기"):
        st.success("정산 데이터가 저장되었습니다 ✨")

