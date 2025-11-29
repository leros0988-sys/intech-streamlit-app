# app/finance_page.py

import io
from typing import List

import pandas as pd
import streamlit as st


def _normalize_org_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    기관 이름 컬럼을 하나로 통일해서 '기관' 컬럼으로 만든다.
    - '기관명' 이 있으면 그걸 사용
    - 없고 '이용기관명' 이 있으면 그걸 사용
    - 둘 다 없으면 '기관' = '미지정'
    """
    df = df.copy()

    if "기관" in df.columns:
        return df

    if "기관명" in df.columns:
        df.rename(columns={"기관명": "기관"}, inplace=True)
    elif "이용기관명" in df.columns:
        df.rename(columns={"이용기관명": "기관"}, inplace=True)
    else:
        df["기관"] = "미지정"

    return df


def _get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    합계낼 수 있는 숫자형 컬럼만 추린다.
    (일자나 텍스트, SETTLE_ID 같은 건 제외)
    """
    numeric_cols: List[str] = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # 너무 이상한 컬럼은 필요하면 나중에 여기서 걸러줄 수 있음
            numeric_cols.append(col)
    return numeric_cols


def _summarize_for_invoice(df: pd.DataFrame) -> pd.DataFrame:
    """
    병합된 원시 데이터(raw_combined_df)를
    '기관' + '__source_file'(원본 파일 단위) 기준으로 합계낸 요약표로 만든다.
    - 나중에 여기서 SETTLE ID 매핑, 채널별 단가 적용 등을 확장할 수 있음.
    """
    df = _normalize_org_column(df)

    # 그룹 기준 컬럼
    group_cols: List[str] = ["기관"]
    if "__source_file" in df.columns:
        group_cols.append("__source_file")

    numeric_cols = _get_numeric_columns(df)
    if not numeric_cols:
        # 혹시 숫자 컬럼이 하나도 없으면 그냥 행 개수만 보여주기
        count_df = (
            df.groupby(group_cols)
            .size()
            .reset_index(name="row_count")
        )
        return count_df

    summary = (
        df.groupby(group_cols)[numeric_cols]
        .sum()
        .reset_index()
    )
    return summary


def finance_page():
    st.markdown("## 💰 정산 처리 페이지")

    # 업로드된 병합 데이터가 없으면 경고
    if "raw_combined_df" not in st.session_state:
        st.warning("⚠ 먼저 **[정산 업로드 및 전체 통계자료]** 메뉴에서 엑셀을 업로드해주세요.")
        return

    df: pd.DataFrame = st.session_state.raw_combined_df

    # ---------------------------
    # 1) 원시 병합 데이터 간단 미리보기
    # ---------------------------
    with st.expander("📂 병합 데이터 미리보기", expanded=False):
        st.dataframe(df, use_container_width=True, height=400)

    # ---------------------------
    # 2) 기관·파일(채널)별 정산 요약 생성
    # ---------------------------
    st.markdown("### 📌 기관·파일(채널)별 정산 요약")

    col_btn1, col_btn2 = st.columns([1, 3])

    with col_btn1:
        if st.button("정산 요약 새로 만들기", use_container_width=True):
            try:
                summary = _summarize_for_invoice(df)
                st.session_state["finance_summary"] = summary
                st.success("정산 요약을 생성했어요.")
            except Exception as e:
                st.error(f"정산 요약 생성 중 오류가 발생했습니다: {e}")

    summary: pd.DataFrame | None = st.session_state.get("finance_summary")

    if summary is None:
        st.info("아직 생성된 정산 요약이 없습니다. 위 버튼을 눌러 만들어 주세요.")
        return

    # ---------------------------
    # 3) 요약 데이터 표시
    # ---------------------------
    st.markdown("#### 📄 정산 요약 표")
    st.dataframe(summary, use_container_width=True, height=400)

    # ---------------------------
    # 4) 다운로드 (Excel / CSV)
    # ---------------------------
    st.markdown("#### 💾 정산 요약 다운로드")

    # Excel
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        summary.to_excel(writer, index=False, sheet_name="정산요약")
    excel_buffer.seek(0)

    st.download_button(
        label="📥 정산 요약 엑셀 다운로드",
        data=excel_buffer,
        file_name="정산_요약.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True,
    )

    # CSV
    csv_data = summary.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 정산 요약 CSV 다운로드",
        data=csv_data,
        file_name="정산_요약.csv",
        mime="text/csv",
        use_container_width=True,
    )


