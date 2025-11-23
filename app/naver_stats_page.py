# app/naver_stats_page.py
import streamlit as st
import pandas as pd

def naver_stats_page():
    st.markdown("## 💚 네이버 통계자료")

    if "raw_settle_df" not in st.session_state:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 파일을 업로드해줘.")
        return

    df: pd.DataFrame = st.session_state["raw_settle_df"]
    naver_df = df[df["중계자"] == "네이버"].copy() if "중계자" in df.columns else df.copy()

    st.dataframe(naver_df.head(200), use_container_width=True)
