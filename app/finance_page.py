import streamlit as st
import pandas as pd
import io


def _df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()


def finance_page():
    st.markdown("## 💰 정산 업로드 센터")
    st.write("카카오 / KT / 네이버 통계 엑셀을 여러 개 올려 한 번에 병합하고, 선택/전체 다운로드 할 수 있습니다.")

    uploaded_files = st.file_uploader(
        "통계 엑셀 파일을 여러 개 선택하세요.",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        key="finance_upload_files",
    )

    if not uploaded_files:
        st.info("먼저 통계 엑셀들을 업로드하세요.")
        return

    dfs = []
    for f in uploaded_files:
        df = pd.read_excel(f)
        df.columns = df.columns.map(lambda x: str(x).strip())
        df["__원본파일"] = f.name
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)

    st.session_state["combined_settle_df"] = combined

    st.markdown("### 🔍 병합된 원본 미리보기")
    st.dataframe(combined.head(100), use_container_width=True)

    st.markdown("---")
    st.markdown("### 🎯 기관 선택 후 다운로드")

    if "기관명" in combined.columns:
        orgs = sorted(combined["기관명"].dropna().unique())
        selected = st.multiselect("기관 선택", orgs)

        if selected:
            filtered = combined[combined["기관명"].isin(selected)]
        else:
            filtered = combined.copy()
    else:
        st.info("⚠ '기관명' 컬럼이 없어 전체 다운로드만 가능합니다.")
        filtered = combined

    col1, col2 = st.columns(2)

    with col1:
        if "기관명" in combined.columns and selected:
            st.download_button(
                "📥 선택 기관만 다운로드",
                data=_df_to_excel_bytes(filtered),
                file_name="정산_선택기관.xlsx",
            )
        else:
            st.caption("기관을 선택하면 활성화됩니다.")

    with col2:
        st.download_button(
            "📥 전체 병합본 다운로드",
            data=_df_to_excel_bytes(combined),
            file_name="정산_전체병합.xlsx",
        )
