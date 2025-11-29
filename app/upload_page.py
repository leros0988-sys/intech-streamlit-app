import streamlit as st
import pandas as pd
from app.utils.file_reader import read_any_file

def upload_page():
    st.markdown("## 📂 정산 파일 업로드 센터")

    uploaded_files = st.file_uploader(
        "카카오/KT/네이버 통계자료 엑셀/CSV 업로드",
        accept_multiple_files=True,
        type=["xlsx", "xls", "csv"]
    )

    if uploaded_files:
        merged = []
        errors = []

        for f in uploaded_files:
            df = read_any_file(f)
            if df is None:
                errors.append(f"❌ {f.name}: 읽기 실패 (엑셀 아님 또는 손상됨)")
            else:
                df["__source_file"] = f.name
                merged.append(df)

        if errors:
            st.error("\n".join(errors))

        if len(merged) == 0:
            st.warning("올바른 파일이 없어서 저장하지 않았습니다.")
            return

        final_df = pd.concat(merged, ignore_index=True)
        st.session_state["uploaded_settlements"] = final_df

        st.success(f"📥 업로드 성공! 총 {len(merged)}개 파일 처리")
        st.dataframe(final_df.head(50), use_container_width=True)
