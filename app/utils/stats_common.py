# app/utils/stats_common.py

import pandas as pd
import streamlit as st


def filter_by_channel(df: pd.DataFrame, keyword_patterns):
    """
    업로드된 raw_combined_df 중 특정 채널(카카오/KT/네이버) 데이터만 필터링.
    '__source_file__'에서 문자열 패턴을 찾는 방식.
    """
    if "__source_file__" not in df.columns:
        st.error("업로드되지 않은 데이터입니다. '__source_file__' 컬럼이 없습니다.")
        return pd.DataFrame()

    pattern = "|".join(keyword_patterns)
    mask = df["__source_file__"].str.contains(pattern, case=False, na=False)
    return df[mask].copy()


def show_statistics(df: pd.DataFrame, title: str):
    """
    일별 통계 (있는 경우) + 기본 요약을 보여준다.
    """
    st.markdown(f"## 📊 {title}")

    if df.empty:
        st.info("해당 채널 자료가 없습니다.")
        return

    # 전체 미리보기
    with st.expander("📁 데이터 미리보기", expanded=False):
        st.dataframe(df, use_container_width=True, height=400)

    # 숫자 컬럼 자동 감지
    numeric_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

    # 간단 그룹핑: 일자 or 날짜 컬럼 탐색
    date_cols = [c for c in df.columns if "일" in c or "date" in c.lower() or "일자" in c]

    # --------------------------
    # 1) 기본 요약 (전체 합계)
    # --------------------------
    st.markdown("### 📌 전체 요약")
    try:
        summary = df[numeric_cols].sum().to_frame(name="합계")
        st.dataframe(summary)
    except:
        st.info("요약할 숫자 컬럼이 없습니다.")

    # --------------------------
    # 2) 일자별 통계
    # --------------------------
    st.markdown("### 📅 일자별 통계")
    if date_cols:
        date_col = date_cols[0]
        try:
            daily = df.groupby(date_col)[numeric_cols].sum().reset_index()
            st.dataframe(daily, use_container_width=True)

            # 다운로드 버튼
            st.download_button(
                "📥 일자별 통계 다운로드 (CSV)",
                data=daily.to_csv(index=False, encoding="utf-8-sig"),
                file_name=f"{title}_일자별통계.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"일자별 통계를 생성할 수 없습니다: {e}")
    else:
        st.info("일자 컬럼을 찾을 수 없습니다.")
