import streamlit as st
import pandas as pd
from app.utils.loader import load_partner_db


def gian_page():
    st.markdown("## 📝 기안 자료 생성")

    if "combined_settle_df" not in st.session_state:
        st.warning("⚠ 먼저 정산 업로드 센터에서 엑셀 파일을 올려 병합해야 합니다.")
        return

    df = st.session_state["combined_settle_df"].copy()
    df.columns = df.columns.map(lambda x: str(x).strip())

    if "기관명" not in df.columns:
        st.error("기관명 컬럼이 없습니다.")
        return

    # SETTLE ID 컬럼 정규화
    settle_candidates = [c for c in df.columns if "settle" in c.lower()]
    if not settle_candidates:
        st.error("SETTLE ID 컬럼이 없습니다.")
        return

    df = df.rename(columns={settle_candidates[0]: "SETTLE_ID"})

    # 금액 추론
    amount_col = None
    for c in ["총금액", "금액", "정산금액"]:
        if c in df.columns:
            amount_col = c
            break
    if amount_col is None:
        df["총금액"] = 0
        amount_col = "총금액"

    summary = (
        df.groupby(["기관명", "SETTLE_ID"])[amount_col]
        .sum()
        .reset_index()
        .rename(columns={amount_col: "총금액"})
    )

    st.dataframe(summary)

    ids = summary["SETTLE_ID"].astype(str).unique()
    selected = st.selectbox("SETTLE ID 선택", ids)

    row = summary[summary["SETTLE_ID"].astype(str) == selected].iloc[0]
    org = row["기관명"]
    total = row["총금액"]

    partner = load_partner_db()
    partner = partner.rename(columns=lambda x: str(x).strip())
    match = partner[partner["기관명"] == org]

    if match.empty:
        담당자 = "정보 없음"
        연락처 = "정보 없음"
    else:
        담당자 = match.iloc[0].get("담당자", "정보 없음")
        연락처 = match.iloc[0].get("연락처", "정보 없음")

    draft = f"""
📌 **{org} 전자고지 정산 기안**

- 기관명: {org}
- SETTLE ID: {selected}
- 총 정산금액: {total:,}원

담당자: {담당자}
연락처: {연락처}

※ 테스트 발송(D10_2T, D11_2T)은 정산 제외
"""

    st.text_area("기안문", draft, height=300)

    st.download_button(
        "📥 기안문 다운로드",
        data=draft,
        file_name=f"기안_{org}_{selected}.txt",
    )
