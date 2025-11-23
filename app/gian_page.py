import streamlit as st
import pandas as pd
from utils.loader import load_partner_db
from utils.calculator import summarize_by_settle_id


def gian_page():
    st.markdown("<div class='title-text'>📝 기안 자료 생성</div>", unsafe_allow_html=True)
    st.write("")

    # 업로드 안 되어 있으면 안내
    if "uploaded_settlements" not in st.session_state:
        st.warning("⚠ 먼저 '정산 업로드 센터'에서 정산 파일을 업로드해주세요.")
        return

    uploaded = st.session_state.uploaded_settlements

    # 파트너 테이블 로드
    try:
        partner_db = load_partner_db()
    except:
        st.error("담당자 DB를 불러올 수 없습니다. 설정에서 경로를 확인해주세요.")
        return

    # SETTLE ID 기준 정리
    combined_df = pd.concat([x["df"] for x in uploaded], ignore_index=True)
    summary_df = summarize_by_settle_id(combined_df)

    st.markdown("### 📑 SETTLE ID별 기안 자료 미리보기")
    st.dataframe(summary_df)

    # 기관 선택
    settle_ids = summary_df["SETTLE_ID"].unique().tolist()
    selected_id = st.selectbox("기관 / SETTLE ID 선택", settle_ids)

    selected_row = summary_df[summary_df["SETTLE_ID"] == selected_id].iloc[0]

    # 담당자 DB 매핑
    org_name = selected_row["기관명"]
    partner_info = partner_db[partner_db["기관명"] == org_name]

    if partner_info.empty:
        담당자 = "정보 없음"
        연락처 = "정보 없음"
    else:
        담당자 = partner_info.iloc[0]["담당자"]
        연락처 = partner_info.iloc[0]["연락처"]

    # 기안 텍스트 자동 생성
    st.markdown("### 🧾 자동 생성된 기안문")

    draft_text = f"""
📌 **{org_name} 전자고지 정산 기안**

1. **정산 개요**
- 기관명: **{org_name}**
- SETTLE ID: **{selected_id}**
- 정산 기간: 업로드된 통계자료 기준
- 총 발송건수: **{selected_row['발송건수']:,}건**
- 총 인증건수: **{selected_row['인증건수']:,}건**
- 정산 금액: **{selected_row['금액']:,}원**

2. **담당자 정보**
- 담당자: {담당자}
- 연락처: {연락처}

3. **특이사항**
- 카카오는 일자별 통계를 필수 첨부하여야 함
- 테스트발송(D10_2T, D11_2T)은 정산 제외 처리됨

4. **첨부자료**
- 일자별 발송통계 (Excel)
- 대금청구서 (PDF)
"""

    st.text_area("기안문", draft_text, height=350)

    st.download_button(
        label="📥 기안문 다운로드 (TXT)",
        data=draft_text,
        file_name=f"기안_{org_name}_{selected_id}.txt",
        mime="text/plain"
    )
