import streamlit as st
import pandas as pd

from app.utils.loader import load_partner_db
from app.utils.calculator import summarize_by_settle_id


def gian_page():
    st.markdown("<div class='title-text'>📝 기안 자료 생성</div>", unsafe_allow_html=True)
    st.write("")

    # 정산 페이지에서 생성된 settled_df 사용
    if "settled_df" not in st.session_state:
        st.warning("⚠ 먼저 '정산 업로드 및 전체 통계자료'에서 정산 계산을 실행해주세요.")
        return

    settled_df = st.session_state["settled_df"]

    # 파트너 DB
    try:
        partner_db = load_partner_db()
    except:
        st.error("기관 담당자 DB 파일을 불러올 수 없습니다. settings.json 경로를 확인하세요.")
        return

    # 기안용 요약 (기관명 + Settle ID + 총금액)
    summary_df = summarize_by_settle_id(settled_df)

    st.markdown("### 📑 SETTLE ID별 정산 요약")
    st.dataframe(summary_df)

    # SETTLE ID 선택
    settle_ids = summary_df["Settle ID"].unique().tolist()
    selected_id = st.selectbox("SETTLE ID 선택", settle_ids)

    selected_row = summary_df[summary_df["Settle ID"] == selected_id].iloc[0]
    org_name = selected_row["기관명"]
    total_amount = selected_row["총금액"]

    # 담당자 매핑
    partner_info = partner_db[partner_db["기관명"] == org_name]

    if partner_info.empty:
        담당자 = "정보 없음"
        연락처 = "정보 없음"
    else:
        담당자 = partner_info.iloc[0]["담당자"]
        연락처 = partner_info.iloc[0]["연락처"]

    # 기안문 생성
    st.markdown("### 🧾 자동 생성된 기안문")

    draft_text = f"""
📌 **{org_name} 전자고지 정산 기안**

1. **정산 개요**
- 기관명: **{org_name}**
- SETTLE ID: **{selected_id}**
- 정산 금액: **{total_amount:,}원**

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
        "📥 기안문 다운로드 (TXT)",
        draft_text,
        file_name=f"기안_{org_name}_{selected_id}.txt",
        mime="text/plain"
    )
