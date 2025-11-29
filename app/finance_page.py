import streamlit as st
from app.utils.calculator import summarize_settle


def finance_page():
    st.markdown("## 💰 정산 처리 페이지")

    if "raw_combined_df" not in st.session_state:
        st.warning("⚠ 먼저 '정산 업로드 센터'에서 파일을 업로드해주세요.")
        return

    df = st.session_state.raw_combined_df

    st.markdown("### 📌 SETTLE ID 기준 요약 생성")

    if st.button("정산 요약 만들기"):
        try:
            summary = summarize_settle(df)
            st.session_state["settle_summary"] = summary
            st.success("정산 요약 생성 완료!")
        except Exception as e:
            st.error(f"오류: {e}")

    if "settle_summary" in st.session_state:
        st.markdown("### 📄 정산 요약 자료")
        st.dataframe(st.session_state.settle_summary, use_container_width=True)
