# app/partner_page.py

import streamlit as st
import pandas as pd
from app.utils.loader import load_partner_db


def partner_page():
    st.markdown("## 🤝 협력사 정산 (에프원 / 엑스아이티 자동 계산)")

    # -------------------------------------
    # 1) raw 데이터 확인
    # -------------------------------------
    if "raw_combined_df" not in st.session_state:
        st.warning("⚠ 먼저 [정산 업로드 및 전체 통계자료]에서 데이터를 업로드해주세요.")
        return

    df = st.session_state.raw_combined_df

    # -------------------------------------
    # 2) partner_db.xlsx 불러오기
    # -------------------------------------
    try:
        partner_db = load_partner_db()
    except Exception as e:
        st.error(f"❌ partner_db.xlsx 불러오기 실패: {e}")
        return

    st.markdown("### 📁 파트너 DB")
    st.dataframe(partner_db, use_container_width=True)

    # -------------------------------------
    # 3) 파트너 선택
    # -------------------------------------
    partner_list = partner_db["partner"].unique().tolist()

    selected_partner = st.selectbox(
        "정산할 협력사를 선택하세요",
        partner_list,
        index=0
    )

    partner_info = partner_db[partner_db["partner"] == selected_partner].iloc[0]

    rate_send = partner_info["send_rate"]
    rate_cert = partner_info["cert_rate"]

    st.info(
        f"""
🔹 **{selected_partner} 단가 정보**
- 발송 단가: {rate_send:,}원
- 인증 단가: {rate_cert:,}원
"""
    )

    # -------------------------------------
    # 4) 필터링된 데이터 가져오기
    # -------------------------------------
    # partner_db 내부 필드: partner_key
    partner_key = partner_info["partner_key"].lower()

    filtered = df[df["__source_file__"].str.contains(partner_key, case=False, na=False)]

    if filtered.empty:
        st.warning("해당 파트너의 데이터가 없습니다.")
        return

    st.markdown("### 📊 파트너 원본 데이터")
    st.dataframe(filtered, use_container_width=True)

    # -------------------------------------
    # 5) 숫자 컬럼 자동 탐색
    # -------------------------------------
    numeric_cols = [c for c in filtered.columns if pd.api.types.is_numeric_dtype(filtered[c])]

    # 카카오: '발송 건수', KT: '수신건수', 네이버: '발송요청건'
    # 파일마다 컬럼명이 다르므로 유연하게 처리
    send_candidates = ["발송", "수신건", "발송요청"]
    cert_candidates = ["인증", "열람", "조회"]

    def find_col(candidates):
        for col in numeric_cols:
            for key in candidates:
                if key in col:
                    return col
        return None

    send_col = find_col(send_candidates)
    cert_col = find_col(cert_candidates)

    if not send_col:
        st.error("❌ 발송 건수를 찾을 수 없습니다.")
        return

    if not cert_col:
        st.error("❌ 인증/열람 건수를 찾을 수 없습니다.")
        return

    send_total = filtered[send_col].sum()
    cert_total = filtered[cert_col].sum()

    # -------------------------------------
    # 6) 자동 계산
    # -------------------------------------
    send_price = send_total * rate_send
    cert_price = cert_total * rate_cert
    total_price = send_price + cert_price

    st.markdown("### 💰 자동 계산 결과")

    st.success(
        f"""
        ### 📌 {selected_partner} 정산 금액  
        - 발송 총 건수: **{send_total:,}건** → {send_price:,}원  
        - 인증 총 건수: **{cert_total:,}건** → {cert_price:,}원  
        ---
        ### ▶ 총 정산 금액: **{total_price:,}원**
        """
    )

    # -------------------------------------
    # 7) 다운로드용 DF 생성
    # -------------------------------------
    result_df = pd.DataFrame(
        [
            ["파트너", selected_partner],
            ["발송 건수", send_total],
            ["발송 단가", rate_send],
            ["발송 금액", send_price],
            ["인증 건수", cert_total],
            ["인증 단가", rate_cert],
            ["인증 금액", cert_price],
            ["총 금액", total_price],
        ],
        columns=["구분", "값"]
    )

    st.markdown("### 📄 다운로드용 정산표")
    st.dataframe(result_df, use_container_width=True)

    st.download_button(
        "📥 CSV 다운로드",
        data=result_df.to_csv(index=False, encoding="utf-8-sig"),
        file_name=f"{selected_partner}_정산.csv",
        mime="text/csv",
    )
