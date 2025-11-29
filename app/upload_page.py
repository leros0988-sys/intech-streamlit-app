# app/upload_page.py

from __future__ import annotations

import io
from typing import List, Dict

import pandas as pd
import streamlit as st

from app.utils.validator import validate_uploaded_files
from app.utils.logger import write_log


def _infer_channel_from_name(name: str) -> str:
    """파일명/시트명에서 채널 추론."""
    lower = name.lower()

    if "카카오" in name or "kakao" in lower:
        return "카카오"
    if "케이티" in name or "kt " in lower or lower.startswith("kt") or " kt" in lower:
        return "KT"
    if "네이버" in name or "naver" in lower:
        return "네이버"
    return "미분류"


def _to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="통합데이터")
    buf.seek(0)
    return buf.read()


def upload_page():

    st.markdown("## 📂 정산 업로드 및 전체 통계자료")

    st.markdown(
        """
        - 카카오 / KT / 네이버 통계 엑셀을 **여러 개 동시에** 업로드할 수 있습니다.  
        - 모든 시트를 읽어 하나의 raw_combined_df 로 병합합니다.  
        - 이후 정산 / 통계 / 기안문 생성 페이지에서 이 데이터를 사용합니다.
        """
    )

    uploaded_files = st.file_uploader(
        "정산용 통계 엑셀 파일들을 선택하세요 (여러 개 선택 가능)",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key="multi_upload_center",
    )

    if uploaded_files:

        # 1) validate_uploaded_files: dict → dict 구조 (파일 → 시트 → DF)
        validated: Dict[str, Dict[str, pd.DataFrame]] = validate_uploaded_files(uploaded_files)

        frames: List[pd.DataFrame] = []
        per_file_info: List[dict] = []

        # 🔥 핵심: dict → DF 변환 루프
        for file_name, sheet_dict in validated.items():

            # sheet_dict = {"Sheet1": df1, "Sheet2": df2}
            for sheet_name, df in sheet_dict.items():

                if df is None or df.empty:
                    continue

                tmp = df.copy()

                # 메타 컬럼 부착
                tmp["__source_file__"] = file_name
                tmp["__sheet__"] = sheet_name
                tmp["__channel__"] = _infer_channel_from_name(file_name)

                frames.append(tmp)

                per_file_info.append(
                    {
                        "파일명": file_name,
                        "시트명": sheet_name,
                        "행 수": len(tmp),
                        "추정 채널": _infer_channel_from_name(file_name),
                    }
                )

        if not frames:
            st.error("업로드된 파일에 유효한 데이터가 없습니다.")
            return

        # 2) 병합
        combined = pd.concat(frames, ignore_index=True)

        # 3) 세션 저장 (🔥 핵심)
        st.session_state["raw_combined_df"] = combined
        st.session_state["uploaded_files_meta"] = per_file_info

        # 4) 로그 기록
        user = st.session_state.get("user", "unknown")
        try:
            write_log(user, f"정산 통계 업로드 완료: {len(per_file_info)}개 시트, {len(combined)}행")
        except:
            pass

        st.success(
            f"✅ 업로드 완료 — {len(per_file_info)}개 시트, 총 {len(combined):,}행 병합됨"
        )

        # -------------------------------------
        # 업로드 요약
        # -------------------------------------
        with st.expander("📄 업로드된 파일/시트 요약", expanded=False):
            st.dataframe(pd.DataFrame(per_file_info), use_container_width=True)

        # -------------------------------------
        # 병합 데이터 미리보기
        # -------------------------------------
        with st.expander("🔎 병합된 전체 데이터 미리보기", expanded=True):
            st.dataframe(combined.head(300), use_container_width=True, height=400)

        # -------------------------------------
        # 다운로드
        # -------------------------------------
        st.markdown("### 💾 병합된 원본 데이터 다운로드")

        col1, col2 = st.columns(2)

        with col1:
            excel_bytes = _to_excel_bytes(combined)
            st.download_button(
                "📥 통합 데이터 엑셀 다운로드",
                data=excel_bytes,
                file_name="정산_통합데이터.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        with col2:
            csv_data = combined.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "📥 통합 데이터 CSV 다운로드",
                data=csv_data,
                file_name="정산_통합데이터.csv",
                mime="text/csv",
            )

    else:
        st.info("정산용 엑셀 파일들을 업로드하세요. 여러 개를 한 번에 선택할 수 있습니다.")
