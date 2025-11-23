# pages/2_정산결과.py
import streamlit as st
import pandas as pd
from utils.loader import load_rate_table, load_partner_db
from utils.calculator import calculate_partner_fee

def app():

    st.markdown("<h1 style='text-align:center;'>📊 정산 결과</h1>", unsafe_allow_html=True)
    st.info("정산 파일을 업로드하면 자동으로 계산됩니다.")

    uploaded = st.file_uploader("정산용 엑셀 파일 업로드", type=["xlsx"])

    if uploaded is not None:
        try:
            df = pd.read_excel(uploaded)

            # 로더에서 DB/요율표 불러오기
            rate_table = load_rate_table()
            partner_db = load_partner_db()

            # 계산
            result = calculate_partner_fee(df)

            st.success("정산 완료!")
            st.dataframe(result, use_container_width=True)

            # ===== 다운로드 버튼 =====
            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    "📥 정산 결과 다운로드 (엑셀)",
                    data=result.to_excel(index=False, engine="xlsxwriter"),
                    file_name="정산결과.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

            with col2:
                st.download_button(
                    "📄 정산 결과 (PDF 생성 예정)",
                    data=b"",
                    file_name="정산결과.pdf",
                )

        except Exception as e:
            st.error(f"오류 발생: {e}")
    else:
        st.warning("엑셀 파일을 업로드해주세요.")
