import streamlit as st
import pandas as pd

def kt_stats_page():
    st.markdown("## 📡 KT 통계자료")

    if "raw_combined_df" not in st.session_state:
        st.info("먼저 [정산 업로드 및 전체 통계자료]에서 엑셀을 업로드해주세요.")
        return

    df = st.session_state.raw_combined_df

    # 1) KT 파일만 필터링
    kt_df = df[df["__source_file__"].str.contains("KT|kt|케이티", case=False, na=False)]

    if kt_df.empty:
        st.warning("KT 관련 데이터가 없습니다.")
        return

    st.success("KT 자료 불러오기 완료!")

    # 컬럼 자동 탐지
    send_col = next((c for c in kt_df.columns if "발송" in c or "수신" in c), None)
    open_col = next((c for c in kt_df.columns if "열람" in c), None)

    if send_col is None:
        st.error("KT 데이터에서 발송 컬럼을 찾을 수 없습니다.")
        return

    if open_col is None:
        kt_df["열람건수"] = 0
        open_col = "열람건수"

    # 계산
    total_send = kt_df[send_col].sum()
    total_open = kt_df[open_col].sum()
    rate_open = (total_open / total_send * 100) if total_send > 0 else 0

    st.markdown("### 📌 전체 요약")
    st.write({
        "총 발송건수": int(total_send),
        "총 열람건수": int(total_open),
        "열람률(%)": round(rate_open, 2),
    })

    # 기관별 요약
    if "기관명" in kt_df.columns:
        agency_summary = kt_df.groupby("기관명")[[send_col, open_col]].sum()
        agency_summary["열람률"] = (agency_summary[open_col] / agency_summary[send_col] * 100).round(2)

        st.markdown("### 🏢 기관별 요약")
        st.dataframe(agency_summary, use_container_width=True)

    # 일자별 요약
    if "일자" in kt_df.columns:
        daily_summary = kt_df.groupby("일자")[[send_col, open_col]].sum()
        daily_summary["열람률"] = (daily_summary[open_col] / daily_summary[send_col] * 100).round(2)

        st.markdown("### 📅 일자별 요약")
        st.dataframe(daily_summary, use_container_width=True)
