import streamlit as st
import pandas as pd

# ----------------------------------------------------
# 엑셀 파일 읽기 (파일명이 달라도 자동 인식)
# ----------------------------------------------------
def read_partner_excel(uploaded_files):
    dfs = []

    for f in uploaded_files:
        try:
            df = pd.read_excel(f)
            df["__source_file__"] = f.name
            dfs.append(df)
        except Exception as e:
            st.error(f"{f.name} 읽는 중 오류: {e}")

    if not dfs:
        return None

    return pd.concat(dfs, ignore_index=True)


# ----------------------------------------------------
# 협력사별 정산 계산 로직
# ----------------------------------------------------
def calc_partner_fee(df):
    """
    df에 다음 컬럼 기준으로 계산:
    - 발송건수 / 인증건수 자동 탐지
    - 파일명에 '엑스아이티', '에프원', 'F1', 'XIT' 등 포함되면 단가 자동 적용
    """

    # 기본 컬럼 자동 탐지
    col_send = None
    col_cert = None

    for c in df.columns:
        if "발송" in c or "수신" in c:
            col_send = c
        if "인증" in c or "열람" in c:
            col_cert = c

    if col_send is None:
        st.error("※ 발송건수 컬럼을 찾을 수 없습니다.")
        return None
    if col_cert is None:
        st.warning("※ 인증/열람 컬럼이 없어 인증건수는 0으로 처리합니다.")
        df["인증건수"] = 0
        col_cert = "인증건수"

    # ------------------------------------------------------
    # 협력사 구분: 파일명 기준
    # ------------------------------------------------------
    filename = str(df["__source_file__"].iloc[0])

    if any(k in filename for k in ["엑스아이티", "XIT", "xit", "x아이티"]):
        # 엑스아이티: 발송 20원, 인증 10원
        send_fee = 20
        cert_fee = 10
        partner = "엑스아이티"

    elif any(k in filename for k in ["에프원", "F1", "f1", "에프원아이엔씨"]):
        # 에프원: 발송 60원, 인증 0원
        send_fee = 60
        cert_fee = 0
        partner = "에프원아이엔씨"

    else:
        send_fee = 0
        cert_fee = 0
        partner = "기타(단가 미등록)"

    # ------------------------------------------------------
    # 계산
    # ------------------------------------------------------
    df["정산금액"] = df[col_send] * send_fee + df[col_cert] * cert_fee

    summary = {
        "협력사명": partner,
        "총 발송건수": int(df[col_send].sum()),
        "총 인증건수": int(df[col_cert].sum()),
        "정산 단가(발송)": send_fee,
        "정산 단가(인증)": cert_fee,
        "총 정산금액": int(df["정산금액"].sum()),
        "파일명": filename,
    }

    return summary, df


# ----------------------------------------------------
# 최종 페이지
# ----------------------------------------------------
def partner_page():
    st.markdown("## 🤝 협력사 정산 (에프원 / 엑스아이티)")

    uploaded = st.file_uploader(
        "협력사 정산 엑셀을 업로드하세요 (여러 개 가능)",
        type=["xlsx", "xls"],
        accept_multiple_files=True
    )

    if not uploaded:
        st.info("※ 엑셀 파일을 올리면 자동으로 정산됩니다.")
        return

    df = read_partner_excel(uploaded)
    if df is None:
        return

    st.success("파일 불러오기 완료!")
    st.dataframe(df.head(), use_container_width=True)

    summary, calc_df = calc_partner_fee(df)

    st.markdown("### 📌 정산 결과 요약")
    st.write(summary)

    st.markdown("### 📄 상세 정산 계산표")
    st.dataframe(calc_df, use_container_width=True)

    st.download_button(
        "📥 정산 계산표 다운로드",
        calc_df.to_csv(index=False, encoding="utf-8-sig"),
        file_name=f"{summary['협력사명']}_정산결과.csv",
        mime="text/csv"
    )

