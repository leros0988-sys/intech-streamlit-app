# app/finance_page.py

import streamlit as st
import pandas as pd
import io


def _df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """DataFrame → 엑셀 바이너리로 변환"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()


def finance_page():
    st.markdown("## 💰 정산 업로드 센터")
    st.write("카카오 / KT / 네이버 등 통계 엑셀을 여러 개 올려서 한 번에 병합하고, 선택적으로 다운로드할 수 있습니다.")

    # 1) 여러 개 엑셀 업로드
    uploaded_files = st.file_uploader(
        "통계 엑셀 파일들을 모두 선택해서 업로드하세요. (여러 개 선택 가능)",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        key="finance_upload_files",
    )

    if not uploaded_files:
        st.info("먼저 통계 엑셀 파일들을 업로드해주세요.")
        return

    st.success(f"현재 업로드된 파일 개수: **{len(uploaded_files)}개**")
    for f in uploaded_files:
        st.write(f"· {f.name}")

    # 2) 업로드된 엑셀 전부 읽어서 병합
    dfs = []
    for f in uploaded_files:
        try:
            df = pd.read_excel(f)
        except Exception as e:
            st.error(f"{f.name} 읽기 실패: {e}")
            return

        if df.empty:
            st.warning(f"{f.name} : 데이터가 없습니다 (비어 있는 엑셀)")
            continue

        # 컬럼 이름 양쪽 공백 제거
        df.columns = df.columns.map(lambda x: str(x).strip())
        # 원본 파일명 표시
        df["__원본파일"] = f.name
        dfs.append(df)

    if not dfs:
        st.error("유효한 데이터가 있는 엑셀 파일이 없습니다.")
        return

    combined = pd.concat(dfs, ignore_index=True)

    # 다른 페이지에서 쓰고 싶으면 여기서 참조 가능
    st.session_state["combined_settle_df"] = combined

    st.markdown("---")
    st.markdown("### 🔍 병합된 원본 미리보기")
    st.dataframe(combined.head(100), use_container_width=True)

    # 3) '기관명' 컬럼이 있으면 기관별 선택 필터 제공
    st.markdown("### 🎯 기관 선택 후 다운로드")

    if "기관명" in combined.columns:
        org_list = (
            combined["기관명"]
            .dropna()
            .astype(str)
            .sort_values()
            .unique()
            .tolist()
        )

        selected_orgs = st.multiselect(
            "다운로드할 기관을 선택하세요. (선택 안 하면 전체 병합본 기준)",
            org_list,
        )

        if selected_orgs:
            filtered = combined[combined["기관명"].isin(selected_orgs)]
        else:
            filtered = combined.copy()
    else:
        st.info("⚠ 병합된 데이터에 '기관명' 컬럼이 없어 기관별 필터는 사용 불가합니다. 전체만 다운로드할 수 있습니다.")
        filtered = combined.copy()
        selected_orgs = []

    st.markdown("### 📥 엑셀 다운로드")

    col1, col2 = st.columns(2)

    with col1:
        # 선택한 기관만 다운로드 (기관 선택이 없으면 버튼 비활성화)
        if selected_orgs:
            bytes_selected = _df_to_excel_bytes(filtered)
            st.download_button(
                "📥 선택한 기관만 엑셀 다운로드",
                data=bytes_selected,
                file_name="정산_선택기관.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.caption("※ 기관을 선택하면 '선택 기관만 다운로드' 버튼이 활성화됩니다.")

    with col2:
        bytes_all = _df_to_excel_bytes(combined)
        st.download_button(
            "📥 전체 병합본 엑셀 다운로드",
            data=bytes_all,
            file_name="정산_전체병합.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


