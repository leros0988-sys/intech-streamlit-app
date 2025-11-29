import pandas as pd
import streamlit as st


def filter_by_channel(df, keyword_patterns):
    """
    채널별 필터링 (카카오/KT/네이버), 완전 방탄녀석
    """

    # 🔥 1) df 자체가 None → 빈 DF 반환
    if df is None:
        return pd.DataFrame()

    # 🔥 2) 타입 검증
    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    # 🔥 3) 비어 있는 DF 방지
    if df.empty:
        return pd.DataFrame()

    # 🔥 4) 필수 컬럼 검증 (__source_file__, __channel__)
    required_cols = ["__source_file__", "__channel__"]
    for col in required_cols:
        if col not in df.columns:
            # 컬럼이 없으면 절대 죽지 않음
            return pd.DataFrame()

    # 🔥 5) 실제 필터링
    mask = pd.Series(False, index=df.index)

    for keyword in keyword_patterns:
        mask |= df["__source_file__"].str.contains(keyword, case=False, na=False)
        mask |= df["__channel__"].str.contains(keyword, case=False, na=False)

    filtered = df[mask]

    # 결과가 비어도 그냥 빈 DF 반환 (오류 없음)
    return filtered.copy() if not filtered.empty else pd.DataFrame()


def show_statistics(df: pd.DataFrame, title: str):
    """
    일별 통계 표시 (df None 방탄 버전)
    """

    st.markdown(f"## 📊 {title}")

    # 🔥 1) df가 None / 비정상 / 빈 DF
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        st.info("데이터가 없습니다. 업로드 후 다시 시도해주세요.")
        return

    # 🔥 2) 데이터 미리보기
    with st.expander("📁 데이터 미리보기", expanded=False):
        st.dataframe(df, use_container_width=True, height=400)

    # 숫자 컬럼 자동 감지
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    # 날짜 컬럼
    date_cols = [c for c in df.columns if "일자" in c or "일" in c or "date" in c.lower()]

    # 🔥 3) 전체 요약
    st.markdown("### 📌 전체 요약")

    if numeric_cols:
        summary = df[numeric_cols].sum().to_frame("합계")
        st.dataframe(summary)
    else:
        st.info("숫자 컬럼이 없습니다.")

    # 🔥 4) 일자별 통계
    st.markdown("### 📅 일자별 통계")

    if date_cols:
        date_col = date_cols[0]
        try:
            daily = df.groupby(date_col)[numeric_cols].sum().reset_index()
            st.dataframe(daily, use_container_width=True)
        except Exception as e:
            st.error(f"일자별 통계 생성 오류: {e}")
    else:
        st.info("일자 컬럼을 찾지 못했습니다.")
