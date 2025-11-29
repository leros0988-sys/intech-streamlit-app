import streamlit as st
import pandas as pd
from io import BytesIO

# 정산 요약 계산 함수
from app.utils.calculator import summarize_settle


def to_excel(df: pd.DataFrame) -> bytes:
    """DataFrame → 엑셀(byte) 변환"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="summary")
    return output.getvalue()


def finance_page():
    st.markdown("## 💰 정산 처리 페이지")

    # 업로드한 전체 통합 DF 확인
    if "raw_combined_df" not in st.session_state:
        st.warning("⚠ 먼저 '정산 업로드 및 전체 통계자료'에서 파일을 업로드해주세요.")
        return

    df = st.session_state.raw_combined_df

    st.markdown("### 📌 업로드된 원본 자료")
    st.dataframe(df.head(50), use_container_width=True)

    st.markdown("---")
    st.markdown("### 📌 SETTLE ID 기준 정산 요약 생성")

    # 버튼: 요약 생성
    if st.button("정산 요약 생성하기"):
        try:
            summary = summarize_settle(df)
            st.session_state["settle_summary"] = summary
            st.success("정산 요약 생성 완료!")
        except Exception as e:
            st.error(f"오류 발생: {e}")

    # 이미 생성된 정산 요약이 있으면 출력
    if "settle_summary" in st.session_state:
        summary = st.session_state.settle_summary

        st.markdown("### 📄 정산 요약 결과")
        st.dataframe(summary, use_container_width=True)

        st.markdown("### 📥 다운로드")
        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📂 정산 요약 엑셀 다운로드",
                data=to_excel(summary),
                file_name="정산요약.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with col2:
            st.download_button(
                label="📂 원본전체 + 요약 전체 ZIP(준비중)",
                data=b"",  # STEP 1에서는 구현 제외
                file_name="전체정산자료.zip",
                disabled=True,
            )

