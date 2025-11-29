import pandas as pd
import streamlit as st


def filter_by_channel(df, keyword_patterns):
    """
    채널별 필터링 (카카오/KT/네이버 공통)
    - df가 None일 때 방어
    - DF 형식 아닐 때 방어
    - 필수 컬럼 없을 때 방어
    """

    # 🔥 1) df None / 비정상 / 빈 DF 방지
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame()

    # 🔥 2) 필수 컬럼 검사
    required_cols = ["__source_file__", "__channel__", "__sheet__"]
    for col in required_cols:
        if col not in df.columns:
            return pd.DataFrame()

    # 🔥 3) 키워드 기반 OR 필터링
    mask = pd.Series(False, index=df.index)
    for key in keyword_patterns:
        mask |= df["__source_file__"].str.contains(key, case=False, na=False)
        mask |= df["__channel__"].str.contains(key, case=False, na=False)

    result = df[mask]
    return result if not result.empty else pd.DataFrame()


def show_statistics(df: pd.DataFrame, title: str):
    """
    일별 통계 + 기본 요약
    """

    st.markdown(f"## 📊 {title}")

    # 🔥 df None / empty 방지
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        st.info("데이터가 없습니다. 업로드 후 다시 시도해주세요.")
        return

    # --------------------------------------
    # 1) 데이터 미리보기
    # --------------------------------------
    with st.expander("📁 데이터 미리보기", expanded=False):
        st.dataframe(df, use_container_width=True, height=400)

    # 숫자 컬럼 탐색
    numeric_cols = [
        col for col in df.columns
        if pd.api.types.is_numeric_dtype(df[col])
    ]

    # 날짜 컬럼 탐색
    date_cols = [
        c for c in df.columns
        if "일" in c or "일자" in c or "date" in c.lower()
    ]

    # --------------------------------------
    # 2) 전체 요약
    # --------------------------------------
    st.markdown("### 📌 전체 요약")

    if numeric_cols:
        summary = df[numeric_cols].sum().to_frame(name="합계")
        st.dataframe(summary)
    else:
        st.info("요약할 숫자 컬럼이 없습니다.")

    # --------------------------------------
    # 3) 일자별 통계
    # --------------------------------------
    st.markdown("### 📅 일자별 통계")

    if date_cols:
        date_col = date_cols[0]

        try:
            daily = (
                df.groupby(date_col)[numeric_cols]
                .sum()
                .reset_index()
            )

            st.dataframe(daily, use_container_width=True)

            st.download_button(
                "📥 일자별 통계 다운로드 (CSV)",
                data=daily.to_csv(index=False, encoding="utf-8-sig"),
                file_name=f"{title}_daily.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"일자별 통계를 생성할 수 없습니다: {e}")
    else:
        st.info("일자를 나타내는 컬럼이 없습니다.")

