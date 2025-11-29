# app/upload_page.py

from __future__ import annotations
import io
import pandas as pd
import streamlit as st
from typing import List, Dict

from app.utils.validator import validate_uploaded_files
from app.utils.logger import write_log


# -------------------------------------------------------
# 채널 추론 함수
# -------------------------------------------------------
def _infer_channel_from_name(name: str) -> str:
    lower = name.lower()
    if "카카오" in name or "kakao" in lower:
        return "카카오"
    if "케이티" in name or "kt " in lower or lower.startswith("kt") or " kt" in lower:
        return "KT"
    if "네이버" in name or "naver" in lower:
        return "네이버"
    return "미분류"


# -------------------------------------------------------
# DF → Excel 변환
# -------------------------------------------------------
def _to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="통합데이터")
    buf.seek(0)
    return buf.read()


# -------------------------------------------------------
# 업로드 페이지
# -------------------------------------------------------
def upload_page():

    st.markdown("## 📂 정산 업로드 및 전체 통계자료")
    st.markdown("""
        - 카카오 / KT / 네이버 통계 파일을 **여러 개 동시에 업로드**할 수 있습니다.  
        - 각 파일의 **모든 시트**를 읽어서 하나의 통합 테이블로 병합합니다.  
        - 이후 모든 정산·통계 페이지는 이 병합 데이터를 기반으로 동작합니다.
    """)

    # ---------------------------------------------
    # 업로드 버튼
    # ---------------------------------------------
    uploaded_files = st.file_uploader(
        "📌 정산용 통계 엑셀 파일들 (다중 선택 가능)",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key="multi_upload_center",
    )

    # ---------------------------------------------
    # 업로드 처리
    # ---------------------------------------------
    if uploaded_files:

        # 🔥 파일 → 시트 → DataFrame 구조 변환
        validated = validate_uploaded_files(uploaded_files)

        frames: List[pd.DataFrame] = []
        per_file_info: List[dict] = []

        # -----------------------------------------
        # 파일명 → 시트명 → DataFrame 루프
        # -----------------------------------------
        for file_name, sheet_dict in validated.items():

            for sheet_name, df in sheet_dict.items():

                # 🔥 df None 방지
                if not isinstance(df, pd.DataFrame):
                    continue
                if df.empty:
                    continue

                tmp = df.copy()

                # 메타컬럼
                tmp["__source_file__"] = file_name
                tmp["__sheet__"] = sheet_name
                tmp["__channel__"] = _infer_channel_from_name(file_name)

                frames.append(tmp)

                per_file_info.append({
                    "파일명": file_name,
                    "시트명": sheet_name,
                    "행수": len(tmp),
                    "추정 채널": _infer_channel_from_name(file_name),
                })

        # 🔥 유효한 DF가 전혀 없는 경우
        if not frames:
            st.error("❌ 업로드된 파일에서 읽을 수 있는 데이터가 없습니다.")
            return

        # -----------------------------------------
        # 병합
        # -----------------------------------------
        combined = pd.concat(frames, ignore_index=True)

        # -----------------------------------------
        # 세션 저장 (핵심)
        # -----------------------------------------
        st.session_state["raw_combined_df"] = combined
        st.session_state["uploaded_files_meta"] = per_file_info

        # -----------------------------------------
        # 로그 기록
        # -----------------------------------------
        user = st.session_state.get("user", "unknown")
        try:
            write_log(
                user,
                f"{len(per_file_info)}개 시트 업로드, 총 {len(combined)}행 병합"
            )
        except:
            pass

        # -----------------------------------------
        # 완료 메시지
        # -----------------------------------------
        st.success(
            f"✅ 병합 완료 — {len(per_file_info)}개 시트, 총 **{len(combined):,}행**"
        )

        # -----------------------------------------
        # 파일 및 시트 요약
        # -----------------------------------------
        with st.expander("📄 파일/시트 요약 보기", expanded=False):
            st.dataframe(pd.DataFrame(per_file_info), use_container_width=True)

        # -----------------------------------------
        # 통합 데이터 미리보기
        # -----------------------------------------
        with st.expander("🔎 병합된 전체 데이터 미리보기", expanded=True):
            st.dataframe(
                combined.head(300),
                use_container_width=True,
                height=450,
            )

        # -----------------------------------------
        # 다운로드 버튼
        # -----------------------------------------
        st.markdown("### 💾 병합된 데이터 다운로드")
        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📥 통합 데이터 (Excel)",
                data=_to_excel_bytes(combined),
                file_name="정산_통합데이터.xlsx",
            )

        with col2:
            st.download_button(
                "📥 통합 데이터 (CSV)",
                data=combined.to_csv(index=False, encoding="utf-8-sig"),
                file_name="정산_통합데이터.csv",
            )

    else:
        st.info("정산용 엑셀 파일들을 업로드해주세요. 여러 개 선택 가능합니다.")
