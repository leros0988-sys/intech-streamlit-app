import streamlit as st
from utils.calculator import filter_by_channel


def kt_stats_page():
    st.markdown("## 📡 KT 통계자료")

    df = st.session_state.get("raw_df")
    if df is None:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 엑셀을 업로드해주세요.")
        return

    kt_df = filter_by_channel(df, "KT")
    if kt_df.empty:
        st.info("KT 건이 없습니다.")
        return

    st.markdown("### 📊 KT 원본 일부")
    st.dataframe(kt_df.head(100), use_container_width=True)

    st.info("세부 KT 정산 로직(D10_2, D11_2 등)은 추후 세부 규칙 반영해서 확장할 수 있습니다.")
