# app/kakao_stats_page.py
import streamlit as st
import pandas as pd

def kakao_stats_page():
    st.markdown("## 💛 카카오 통계자료")
    st.info("D10_2 / D11_2, 테스트 발송(D10_2T, D11_2T) 제거 등의 전처리 로직을 여기에 넣으면 돼.")

    if "raw_settle_df" not in st.session_state:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 파일을 업로드해줘.")
        return

    df: pd.DataFrame = st.session_state["raw_settle_df"]
    kakao_df = df[df["중계자"] == "카카오"].copy() if "중계자" in df.columns else df.copy()

    st.dataframe(kakao_df.head(200), use_container_width=True)
