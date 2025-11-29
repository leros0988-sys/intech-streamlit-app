import streamlit as st
import pandas as pd


def upload_page():
    st.markdown("## 📂 정산 업로드 센터")

    uploaded_files = st.file_uploader(
        "📌 여러 개의 정산 엑셀 파일을 올려주세요.",
        type=["xlsx"],
        accept_multiple_files=True,
        key="upload_center"
    )

    if not uploaded_files:
        st.info("정산 파일을 업로드해주세요.")
        return

    dfs = []
    for f in uploaded_files:
        try:
            df = pd.read_excel(f)
            df["__source_file"] = f.name
            dfs.append(df)
        except Exception as e:
            st.error(f"{f.name} 읽는 중 오류: {e}")
            return

    combined = pd.concat(dfs, ignore_index=True)
    st.session_state.uploaded_settlements = [
        {"name": f.name, "df": pd.read_excel(f)} for f in uploaded_files
    ]
    st.session_state.raw_combined_df = combined

    st.success(f"{len(uploaded_files)}개 파일 업로드 및 병합 완료!")

    with st.expander("📄 병합 데이터 미리보기"):
        st.dataframe(combined.head(200), use_container_width=True)

