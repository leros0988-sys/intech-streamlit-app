# app/upload_page.py

from __future__ import annotations

import io
from typing import List, Dict

import pandas as pd
import streamlit as st

from app.utils.validator import validate_uploaded_files
from app.utils.logger import write_log


def _infer_channel_from_name(name: str) -> str:
    """
    파일명/시트명에서 채널(카카오/KT/네이버)을 대충 추론한다.
    - 나중에 kakao_stats_page / kt_stats_page / naver_stats_page 에서도 참고 가능.
    """
    lower = name.lower()

    if "카카오" in name or "kakao" in lower:
        return "카카오"
    if "케이티" in name or "kt " in lower or lower.startswith("kt") or " kt" in lower:
        return "KT"
    if "네이버" in name or "naver" in lower:
        return "네이버"

    return "미분류"


def _to_excel_bytes(df: pd.DataFrame) -> bytes:
    """
    DataFrame -> 엑셀 바이너리 (다운로드용)
    """
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="통합데이터")
    buf.seek(0)
    return buf.read()


def upload_page():
    """
    '정산 업로드 및 전체 통계자료' 페이지.
    - 카카오 / KT / 네이버 / 기타 통계 엑셀 여러 개 업로드
    - 모든 시트를 읽어 하나의 raw_combined_df 로 병합
    - 각 행에 __source_file__, __sheet__, __channel__ 정보 추가
    - 병합 결과를 session_state["raw_combined_df"] 에 저장
    - 병합본 미리보기 + 엑셀/CSV 다운로드
    """

    st.markdown("## 📂 정산 업로드 및 전체 통계자료")

    st.markdown(
        """
        - 카카오 / KT / 네이버 통계 엑셀을 **여러 개 한 번에** 업로드할 수 있어요.  
        - 각 파일의 **모든 시트**를 읽어서 하나의 테이블로 합칩니다.  
        - 이후 정산 처리, 3사 통계, 기안 생성 등은 이 병합 결과를 기반으로 동작합니다.
        """
    )

    uploaded_files = st.file_uploader(
        "정산용 통계 엑셀 파일들을 모두 선택해서 업로드해주세요 (여러 개 선택 가능)",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key="multi_upload_center",
    )

    # -----------------------------------
    # 업로드 & 병합 처리
    # -----------------------------------
    if uploaded_files:
        # 1) 파일별로 읽어서 {파일명: DF} 형태로 얻기
        validated: Dict[str, pd.DataFrame] = validate_uploaded_files(uploaded_files)

        frames: List[pd.DataFrame] = []
        per_file_info: List[dict] = []

        for name, df in validated.items():
            if df.empty:
                continue

            tmp = df.copy()

            # __source_file__ / __sheet__ 컬럼이 없다면 기본값 보정
            if "__source_file__" not in tmp.columns:
                tmp["__source_file__"] = name
            # file_reader 에서 시트명 붙여줬지만 혹시 없을 수도 있으니
            if "__sheet__" not in tmp.columns:
                tmp["__sheet__"] = ""

            # 채널 추론 컬럼 추가 (파일명 + 시트명 기반)
            channel_guess = _infer_channel_from_name(name)
            tmp["__channel__"] = channel_guess

            frames.append(tmp)

            per_file_info.append(
                {
                    "파일명": name,
                    "행 수": len(tmp),
                    "추정 채널": channel_guess,
                }
            )

        if not frames:
            st.error("업로드된 파일들에서 유효한 데이터가 하나도 없습니다.")
            return

        # 2) 전체 병합
        combined = pd.concat(frames, ignore_index=True)

        # 3) 세션에 저장
        st.session_state["raw_combined_df"] = combined
        st.session_state["uploaded_files_meta"] = per_file_info

        # 4) 로그 기록 (로그인한 사용자 이름이 있으면 함께 기록)
        user = st.session_state.get("user", "unknown")
        try:
            write_log(user, f"정산 통계 엑셀 {len(per_file_info)}개 업로드, 총 {len(combined)}행 병합")
        except Exception:
            # 로그 실패해도 앱이 죽으면 안 되므로 조용히 무시
            pass

        st.success(
            f"✅ 업로드 완료: {len(per_file_info)}개 파일, "
            f"총 {len(combined):,}행이 병합되었습니다."
        )

        # -----------------------------------
        # 업로드된 파일 요약 정보
        # -----------------------------------
        with st.expander("📄 업로드된 파일 요약 보기", expanded=False):
            info_df = pd.DataFrame(per_file_info)
            st.dataframe(info_df, use_container_width=True)

        # -----------------------------------
        # 병합 데이터 미리보기
        # -----------------------------------
        with st.expander("🔎 병합된 전체 데이터 미리보기", expanded=True):
            st.dataframe(
                combined.head(300),
                use_container_width=True,
                height=400,
            )

        # -----------------------------------
        # 병합본 다운로드 (엑셀 / CSV)
        # -----------------------------------
        st.markdown("---")
        st.markdown("### 💾 병합된 원본 데이터 다운로드")

        col1, col2 = st.columns(2)

        with col1:
            excel_bytes = _to_excel_bytes(combined)
            st.download_button(
                "📥 통합 데이터 엑셀 다운로드",
                data=excel_bytes,
                file_name="정산_통합데이터.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        with col2:
            csv_data = combined.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "📥 통합 데이터 CSV 다운로드",
                data=csv_data,
                file_name="정산_통합데이터.csv",
                mime="text/csv",
                use_container_width=True,
            )

    else:
        # 아직 업로드 안 했을 때 안내
        st.info(
            "왼쪽 또는 위의 **파일 선택 버튼**을 눌러 "
            "정산용 통계 엑셀 파일들을 업로드해주세요. "
            "여러 개를 한 번에 선택해도 됩니다."
        )

