import streamlit as st
import pandas as pd
from app.utils.file_reader import read_any_file


def upload_page():
    st.markdown("## 📤 정산 업로드 및 전체 통계자료")

    uploaded_files = st.file_uploader(
        "📂 여러 개의 엑셀 파일을 업로드하세요",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True
    )

    if uploaded_files:
        all_dfs = []
        error_files = []

        for file in uploaded_files:
            try:
                df = read_any_file(file)
                df["__source_file__"] = file.name
                all_dfs.append(df)
            except Exception as e:
                error_files.append(f"{file.name} 읽는 중 오류: {e}")

        if error_files:
            st.error("⚠ 오류가 발생한 파일들:\n" + "\n".join(error_files))

        if all_dfs:
            combined = pd.concat(all_dfs, ignore_index=True)
            st.session_state.raw_combined_df = combined

            st.success(f"총 {len(all_dfs)}개 파일 병합 완료!")
            st.dataframe(combined.head(200), use_container_width=True)

        else:
            st.warning("업로드된 자료에서 읽을 수 있는 파일이 없습니다.")
