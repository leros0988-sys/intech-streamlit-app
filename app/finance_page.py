import streamlit as st
import pandas as pd
import io

def df_to_excel_bytes(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.getvalue()


def finance_page():
    st.markdown("## 💰 정산 처리 페이지")

    if "uploaded_settlements" not in st.session_state:
        st.warning("먼저 '정산 업로드 센터'에서 파일을 업로드해주세요.")
        return

    raw_df = st.session_state["uploaded_settlements"]

    st.success("📊 업로드 데이터 확인됨.")
    st.dataframe(raw_df.head(30), use_container_width=True)

    # ---- 정산 계산 ----
    if st.button("🔢 정산 계산 실행"):
        df = raw_df.copy()

        # 여기서 네가 원하는 계산 로직 추가 가능
        df["총금액"] = 0  

        st.session_state["settlement_done"] = df
        st.success("정산 계산 완료!")

    # ---- 계산 후 다운로드 ----
    if "settlement_done" in st.session_state:
        result = st.session_state["settlement_done"]

        st.markdown("### 📥 정산 결과 다운로드")

        st.download_button(
            label="전체 다운로드",
            data=df_to_excel_bytes(result),
            file_name="정산결과_전체.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        기관목록 = sorted(result["__source_file"].unique())
        selected = st.multiselect("파일별 선택 다운로드", 기관목록)

        if selected:
            filtered = result[result["__source_file"].isin(selected)]
            st.download_button(
                "선택 파일만 다운로드",
                data=df_to_excel_bytes(filtered),
                file_name="정산결과_선택.xlsx"
            )

        )
