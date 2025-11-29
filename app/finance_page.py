# app/finance_page.py

from __future__ import annotations

import io
import pandas as pd
import streamlit as st


# ------------------------------
# 📌 기관명 정규화
# ------------------------------
def normalize_org(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 우선순위: 기관 → 기관명 → 이용기관명
    if "기관" in df.columns:
        return df

    if "기관명" in df.columns:
        df.rename(columns={"기관명": "기관"}, inplace=True)
        return df

    if "이용기관명" in df.columns:
        df.rename(columns={"이용기관명": "기관"}, inplace=True)
        return df

    df["기관"] = "미지정"
    return df


# ------------------------------
# 📌 숫자 컬럼 자동 감지
# ------------------------------
def get_numeric_columns(df: pd.DataFrame):
    numeric_cols = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
    return numeric_cols


# ------------------------------
# 📌 기관 × 채널 × (파일) 기준 합계 요약
# ------------------------------
def summarize_for_finance(df: pd.DataFrame) -> pd.DataFrame:

    df = normalize_org(df)

    # 채널이 없다면 기본값
    if "__channel__" not in df.columns:
        df["__channel__"] = "미분류"

    # 파일명 컬럼이 없다면 기본값
    if "__source_file__" not in df.columns and "__source_file" in df.columns:
        df.rename(columns={"__source_file": "__source_file__"}, inplace=True)

    if "__source_file__" not in df.columns:
        df["__source_file__"] = ""

    numeric_cols = get_numeric_columns(df)

    # 그룹 기준
    group_cols = ["기관", "__channel__", "__source_file__"]

    if not numeric_cols:
        # 숫자 하나도 없으면 행수만 집계
        return (
            df.groupby(group_cols)
            .size()
            .reset_index(name="row_count")
        )

    summary = (
        df.groupby(group_cols)[numeric_cols]
        .sum()
        .reset_index()
    )

    return summary


# ------------------------------
# 📌 DataFrame → Excel 변환
# ------------------------------
def to_excel(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="정산요약")
    buf.seek(0)
    return buf.read()


# ------------------------------
# 📌 메인 페이지
# ------------------------------
def finance_page():

    st.markdown("## 💰 정산 처리 페이지")
    st.write("업로드된 통합 데이터를 기반으로 기관·채널별 정산 요약을 생성합니다.")

    # --------------------------
    # raw_combined_df 존재 확인
    # --------------------------
    if "raw_combined_df" not in st.session_state:
        st.warning("⚠ 먼저 **정산 업로드 및 전체 통계자료** 페이지에서 통계파일을 업로드해주세요.")
        return

    df: pd.DataFrame = st.session_state.raw_combined_df

    # --------------------------
    # 원본 데이터 미리보기
    # --------------------------
    with st.expander("📂 병합 원본 데이터 미리보기", expanded=False):
        st.dataframe(df.head(200), use_container_width=True)

    st.markdown("---")

    # --------------------------
    # 정산 요약 생성
    # --------------------------
    st.markdown("### 📌 기관·채널별 정산 요약 생성")

    if st.button("정산 요약 새로 만들기"):
        try:
            summary = summarize_for_finance(df)
            st.session_state["finance_summary"] = summary
            st.success("정산 요약 생성 완료!")
        except Exception as e:
            st.error(f"요약 생성 오류: {e}")

    summary = st.session_state.get("finance_summary")

    if summary is None:
        st.info("정산 요약이 아직 없습니다. 상단 버튼을 눌러 생성하세요.")
        return

    # --------------------------
    # 요약 테이블 표시
    # --------------------------
    st.markdown("### 📄 정산 요약 테이블")
    st.dataframe(summary, use_container_width=True, height=450)

    st.markdown("---")

    # --------------------------
    # 다운로드 영역
    # --------------------------
    st.markdown("### 💾 정산 요약 다운로드")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📥 전체 요약 엑셀 다운로드",
            data=to_excel(summary),
            file_name="정산_요약_전체.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col2:
        csv_data = summary.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 전체 요약 CSV 다운로드",
            data=csv_data,
            file_name="정산_요약_전체.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # --------------------------
    # 기관별 다운로드
    # --------------------------
    st.markdown("### 🏛 기관별 다운로드")

    org_list = sorted(summary["기관"].unique())
    selected_org = st.selectbox("기관 선택", org_list)

    org_df = summary[summary["기관"] == selected_org]

    st.dataframe(org_df, use_container_width=True)

    st.download_button(
        f"📥 {selected_org} 정산 요약 다운로드",
        data=to_excel(org_df),
        file_name=f"정산요약_{selected_org}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
