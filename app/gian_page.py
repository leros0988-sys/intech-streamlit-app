import streamlit as st
from app.utils.loader import load_partner_db


def gian_page():
    st.markdown("## 📝 기안 생성 페이지")

    if "settle_summary" not in st.session_state:
        st.warning("⚠ 먼저 정산 요약을 생성해주세요.")
        return

    summary = st.session_state.settle_summary
    partner_db = load_partner_db()

    settle_ids = summary["SETTLE_ID"].unique().tolist()
    selected = st.selectbox("SETTLE ID 선택", settle_ids)

    row = summary[summary["SETTLE_ID"] == selected].iloc[0]
    org = row["기관명"]

    partner = partner_db[partner_db["기관명"] == org]

    담당자 = partner.iloc[0]["담당자"] if not partner.empty else "정보 없음"
    연락처 = partner.iloc[0]["연락처"] if not partner.empty else "정보 없음"

    draft = f"""
📌 {org} 전자고지 정산 기안

- SETTLE ID: {selected}
- 기관명: {org}
- 발송건수: {row['발송건수']:,}건
- 인증건수: {row['인증건수']:,}건
- 정산금액: {row['금액']:,}원

📞 담당자: {담당자} / {연락처}
"""

    st.text_area("기안문", draft, height=250)

    st.download_button(
        "TXT 다운로드",
        data=draft,
        file_name=f"기안_{org}_{selected}.txt",
        mime="text/plain"
    )

