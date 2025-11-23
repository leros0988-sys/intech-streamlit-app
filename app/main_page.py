# -------------------------
# 이번 달 운영 요약 (정산서 수 = 카카오 SETTLE ID 유니크)
# -------------------------
st.markdown("### 📊 이번 달 운영 요약")

df = st.session_state.get("raw_settle_df")

total_statements = 0
total_amount = 0

if df is not None:

    # 카카오 SETTLE ID만 정산 기준
    settle_col = "카카오 settle id"

    if settle_col in df.columns:
        # 정산서 개수 = 카카오 settle id 유니크 개수
        total_statements = df[settle_col].dropna().astype(str).nunique()
    else:
        st.warning("⚠️ 업로드한 엑셀에서 '카카오 settle id' 컬럼을 찾을 수 없습니다.")

    # 금액 컬럼 찾기
    amount_col = None
    for cand in ["금액", "청구금액", "정산금액", "합계"]:
        if cand in df.columns:
            amount_col = cand
            break

    if amount_col:
        total_amount = df[amount_col].fillna(0).sum()

# UI 출력
st.markdown(
    f"""
    <div style="
        background:white;
        border-radius:12px;
        padding:20px 25px;
        margin-top:10px;
        margin-bottom:35px;
        box-shadow:0 2px 12px rgba(0,0,0,0.06);
    ">
        <h3 style="margin:0; padding:0; font-size:22px;">📌 이번 달 정산 요약</h3>
        <p style="font-size:17px; margin-top:10px;">
            • 이번 달 총 <b>대금청구서</b> 개수 : <b>{total_statements:,} 건</b><br>
            • 총 정산 금액 : <b>{total_amount:,} 원</b><br>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
