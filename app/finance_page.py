import streamlit as st
from app.utils.calculator import summarize_settle


def finance_page():
    st.markdown("## 💰 정산 처리 페이지")

    # 업로드 자료 없는 경우
    if "raw_combined_df" not in st.session_state:
        st.error("⚠ 먼저 [정산 업로드 및 전체 통계자료]에서 파일을 업로드하세요.")
        return

    df = st.session_state.raw_combined_df

    st.markdown("### 📌 SETTLE ID 기준 정산 요약")

    if st.button("정산 요약 만들기"):
        try:
            summary = summarize_settle(df)
            st.session_state.settle_summary = summary
            st.success("정산 요약 생성 완료!")
        except Exception as e:
            st.error(f"오류 발생: {e}")

    # 생성된 요약 보여주기
    if "settle_summary" in st.session_state:
        st.markdown("### 📄 정산 요약")
        st.dataframe(st.session_state.settle_summary, use_container_width=True)

