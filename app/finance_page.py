import streamlit as st
import pandas as pd
import io

from app.utils.loader import load_rate_table, load_partner_db
from app.utils.validator import validate_uploaded_files
from app.utils.calculator import calculate_settlement
from app.utils.generator import generate_settlement_excel


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()


def finance_page():
    st.markdown("## 💰 정산 업로드 및 전체 통계자료")

    # DB 로드
    try:
        rate_db = load_rate_table()
        partner_db = load_partner_db()
    except Exception as e:
        st.error(f"DB 로드 오류: {e}")
        return

    with st.expander("📂 기준 DB 확인"):
        st.dataframe(rate_db.head(20))
        st.dataframe(partner_db.head(20))

    st.markdown("### 1) 통계자료 업로드")
    uploaded_files = st.file_uploader(
        "카카오/KT/네이버 통계 엑셀 여러 개 업로드 가능",
        type=["xlsx"],
        accept_multiple_files=True,
        key="settle_upload_finance"
    )

    if uploaded_files:
        try:
            validated = validate_uploaded_files(uploaded_files)
        except Exception as e:
            st.error(f"파일 검증 오류: {e}")
            return

        dfs = []
        for fname, df in validated.items():
            df["원본파일"] = fname
            dfs.append(df)

        merged = pd.concat(dfs, ignore_index=True)

        st.session_state["raw_settle_df"] = merged
        st.success(f"총 {len(uploaded_files)}개 파일 업로드 성공")

        with st.expander("업로드 원본 미리보기"):
            st.dataframe(merged.head(50))

    st.markdown("---")

    if "raw_settle_df" in st.session_state:
        if st.button("🔢 정산 계산 실행"):
            try:
                settled, issues = calculate_settlement(st.session_state["raw_settle_df"], rate_db)
                st.session_state["settled_df"] = settled
                st.session_state["issues_df"] = issues
                st.success("정산 계산 완료!")
            except Exception as e:
                st.error(f"정산 오류: {e}")

    if "settled_df" in st.session_state:
        settled_df = st.session_state["settled_df"]
        st.markdown("### 3) 정산 결과 요약")

        기관_list = sorted(settled_df["기관명"].unique())
        선택기관 = st.multiselect("다운로드할 기관 선택", 기관_list)

        결과 = settled_df if not 선택기관 else settled_df[settled_df["기관명"].isin(선택기관)]

        st.download_button(
            "📥 선택 기관 다운로드",
            data=df_to_excel_bytes(결과),
            file_name="정산_선택기관.xlsx"
        )

        st.download_button(
            "📥 전체 정산 다운로드",
            data=df_to_excel_bytes(settled_df),
            file_name="정산_전체.xlsx"
        )

    st.markdown("### 4) 특이사항 로그")
    if "issues_df" in st.session_state and not st.session_state["issues_df"].empty:
        issues_df = st.session_state["issues_df"]
        st.warning(f"⚠ 매칭 실패 {len(issues_df)}건")
        st.dataframe(issues_df)

        st.download_button(
            "📥 특이사항 다운로드",
            data=df_to_excel_bytes(issues_df),
            file_name="정산_특이사항.xlsx"
        )


