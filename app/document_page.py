import io
import pandas as pd
import streamlit as st

from utils.loader import load_partner_db
from utils.generator import generate_document


def _df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)
    return buf.read()


def document_page():
    st.markdown("## 📄 기안 자료 생성")

    if "settled_df" not in st.session_state:
        st.warning("정산 결과가 없습니다. 먼저 [정산 업로드 및 전체 통계자료]에서 정산을 완료해주세요.")
        return

    settled_df: pd.DataFrame = st.session_state["settled_df"]

    try:
        partner_db = load_partner_db()
    except Exception as e:
        st.error(f"기관 담당자 DB 로드 실패: {e}")
        return

    st.info("정산 결과 + 기관 담당자 DB를 합쳐서 기안용 표(기관명, 부서, 담당자, 연락처, 금액 등)를 만들어.")

    # 예시: 기관명 / 부서명 기준으로 join
    merged = pd.merge(
        settled_df,
        partner_db,
        left_on=["기관명", "부서명"],
        right_on=["기관명", "부서명"],
        how="left",
        suffixes=("", "_담당"),
    )

    # 기안 표에 필요한 컬럼만 추려내기 (너 엑셀 양식에 맞게 수정)
    cols = [
        "기관명",
        "부서명",
        "문서명",
        "건수",
        "총금액",
        "담당자명",
        "연락처",
        "이메일",
        # 필요하면 더 추가
    ]
    available_cols = [c for c in cols if c in merged.columns]
    doc_df = merged[available_cols].copy()

    st.dataframe(doc_df.head(100), use_container_width=True)

    # 엑셀 다운로드 (기안표)
    bytes_doc = _df_to_excel_bytes(doc_df)
    st.download_button(
        "📥 기안자료 엑셀 다운로드",
        data=bytes_doc,
        file_name="기안자료_자동생성.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # 로컬 저장 (참고용)
    path = generate_document(doc_df, save_path="기안자료_자동생성.xlsx")
    st.caption(f"로컬 파일로도 '{path}' 이름으로 저장됨 (클라우드에선 참고용).")
