import streamlit as st
import pandas as pd

from app.utils.loader import load_rate_table, load_partner_db
from app.utils.validator import validate_uploaded_df
from app.utils.calculator import calculate_settlement
from app.utils.generator import generate_settlement_excel

def _df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()


def finance_page():
    st.markdown("## 💰 정산 업로드 및 전체 통계자료")

    # --- 0) 기준 DB 로드 -------------------------------------------------
    try:
        rate_db = load_rate_table()
        partner_db = load_partner_db()
    except Exception as e:
        st.error(f"기준 DB 로드 오류: {e}")
        return

    with st.expander("📂 로드된 기준 DB 확인하기", expanded=False):
        st.write("### 요율표 (rate_table.xlsx)")
        st.dataframe(rate_db.head(30), use_container_width=True)
        st.write("### 기관 담당자 정보 DB")
        st.dataframe(partner_db.head(30), use_container_width=True)

    st.markdown("---")

    # --- 1) 통계자료 업로드 ----------------------------------------------
    st.markdown("### 1) 통계자료 엑셀 업로드")

    uploaded_files = st.file_uploader(
        "카카오 / KT / 네이버 통계 엑셀을 모두 선택해서 올려줘 (여러 개 선택 가능)",
        type=["xlsx"],
        accept_multiple_files=True,
        key="settle_upload",
    )

    if uploaded_files:
        try:
            validated = validate_uploaded_files(uploaded_files)
        except Exception as e:
            st.error(f"업로드 파일 검증 실패: {e}")
            return

        dfs = []
        for name, df in validated.items():
            tmp = df.copy()
            tmp["__source_file"] = name
            dfs.append(tmp)

        try:
            raw_df = pd.concat(dfs, ignore_index=True)
        except ValueError:
            st.error("업로드된 파일에 유효한 데이터가 없습니다.")
            return

        st.session_state["raw_settle_df"] = raw_df
        st.success(f"✅ {len(uploaded_files)}개 파일 업로드 및 병합 완료.")

        with st.expander("업로드 원본 미리보기", expanded=False):
            st.dataframe(raw_df.head(100), use_container_width=True)

    st.markdown("---")

    # --- 2) 정산 계산 ----------------------------------------------------
    if "raw_settle_df" in st.session_state:
        st.markdown("### 2) 요율표 기준 정산 계산")

        if st.button("🔢 정산 계산 실행하기"):
            try:
                settled_df, issues_df = calculate_settlement(
                    st.session_state["raw_settle_df"], rate_db
                )
                st.session_state["settled_df"] = settled_df
                st.session_state["issues_df"] = issues_df
                st.success("정산 계산이 완료되었습니다.")
            except Exception as e:
                st.error(f"정산 계산 중 오류: {e}")

    # --- 3) 정산 결과 요약 -----------------------------------------------
    if "settled_df" in st.session_state:
        settled_df: pd.DataFrame = st.session_state["settled_df"]

        st.markdown("### 3) 정산 결과 요약")

        # 기관별 / 부서별 집계
        group_cols = ["기관명", "부서명"]
        if not all(col in settled_df.columns for col in group_cols):
            st.error("정산 결과에 기관명/부서명 컬럼이 없습니다. 컬럼명을 다시 확인해주세요.")
        else:
            summary = (
                settled_df.groupby(group_cols)["총금액"]
                .sum()
                .reset_index()
                .sort_values(["기관명", "부서명"])
            )
            st.dataframe(summary, use_container_width=True)

        # --- 4) 선택 다운로드 --------------------------------------------
        st.markdown("### 4) 정산 결과 다운로드")

        기관_list = sorted(settled_df.get("기관명", []))
        selected_기관 = st.multiselect(
            "다운로드할 기관을 선택하세요. (선택 안 하면 전체 다운로드)",
            기관_list,
        )

        if selected_기관:
            filtered = settled_df[settled_df["기관명"].isin(selected_기관)]
        else:
            filtered = settled_df

        col1, col2 = st.columns(2)

        with col1:
            excel_bytes_selected = _df_to_excel_bytes(filtered)
            st.download_button(
                "📥 선택 기관만 엑셀 다운로드",
                data=excel_bytes_selected,
                file_name="정산결과_선택기관.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with col2:
            excel_bytes_all = _df_to_excel_bytes(settled_df)
            st.download_button(
                "📥 전체 정산결과 엑셀 다운로드",
                data=excel_bytes_all,
                file_name="정산결과_전체.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        # 대금청구서 양식 그대로 쓰고 싶으면 여기서 generate_bill 호출
        if st.button("🧾 대금청구서용 원본 엑셀 생성"):
            path = generate_bill(settled_df, save_path="대금청구서_원본.xlsx")
            st.success(f"로컬 경로에 '{path}' 로 저장되었습니다. (Streamlit 클라우드에서는 로컬 파일은 참고용)")

    # --- 5) 특이사항 로그 (매핑 누락) -----------------------------------
    st.markdown("---")
    st.markdown("### 5) 특이사항 로그 (요율 매칭 누락, 기관/부서/문서 오류)")

    issues_df: pd.DataFrame | None = st.session_state.get("issues_df")
    if issues_df is None or issues_df.empty:
        st.info("현재까지 기록된 특이사항이 없습니다.")
    else:
        st.warning(f"⚠ 요율 매칭 실패 행 {len(issues_df)}건이 있습니다. 아래 데이터를 확인해주세요.")
        st.dataframe(issues_df, use_container_width=True)

        issues_bytes = _df_to_excel_bytes(issues_df)
        st.download_button(
            "📥 특이사항 로그 엑셀 다운로드",
            data=issues_bytes,
            file_name="정산_특이사항로그.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )







