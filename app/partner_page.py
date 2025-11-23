import io
import pandas as pd
import streamlit as st

from utils.loader import load_rate_table
from utils.calculator import calculate_settlement


def _df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()


def partner_page():
    st.markdown("## 🤝 협력사 정산 (엑스아이티 / 에프원 등)")

    if "raw_settle_df" not in st.session_state:
        st.warning("먼저 [정산 업로드 및 전체 통계자료]에서 파일을 업로드하고 정산을 한 번 돌려줘.")
        return

    if "settled_df" not in st.session_state:
        st.warning("정산 결과가 없습니다. [정산 업로드 및 전체 통계자료]에서 정산 계산을 먼저 실행해줘.")
        return

    settled_df: pd.DataFrame = st.session_state["settled_df"]

    st.info("협력사 기준(중계자, 채널 등)에 맞게 필터링해서 엑셀로 내려받는 기능.")

    # 예시: 중계자 컬럼 기준으로 협력사 구분
    if "중계자" not in settled_df.columns:
        st.error("정산 결과에 '중계자' 컬럼이 없습니다. 협력사 구분 기준을 다시 확인해주세요.")
        return

    partner_list = sorted(settled_df["중계자"])
    selected_partner = st.selectbox("협력사를 선택해주세요.", partner_list)

    partner_df = settled_df[settled_df["중계자"] == selected_partner].copy()

    st.dataframe(partner_df, use_container_width=True)

    bytes_partner = _df_to_excel_bytes(partner_df)
    st.download_button(
        f"📥 {selected_partner} 정산 엑셀 다운로드",
        data=bytes_partner,
        file_name=f"협력사정산_{selected_partner}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
