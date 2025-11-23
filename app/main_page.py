import streamlit as st
from utils.loader import load_settings, load_rate_table
from app.style import apply_global_styles

def main_page():
    apply_global_styles()
    settings = load_settings()

    # --------------------------
    # 이미지
    # --------------------------
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    st.image(settings.get("main_image"), width=380)
    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------
    # 제목
    # --------------------------
    st.markdown("""
        <h1 style='text-align:center; font-size:36px; font-weight:900; margin-top:10px;'>
            📱 아이앤텍 전자고지 대금청구서 대시보드
        </h1>
    """, unsafe_allow_html=True)

    # --------------------------
    # 환영 문구
    # --------------------------
    st.markdown(f"""
    <h2 style='text-align:center; font-size:24px; margin-bottom:20px;'>
        {settings.get("welcome_text")}
    </h2>
    """, unsafe_allow_html=True)

    # --------------------------
    # 운영 요약 박스
    # --------------------------
    st.markdown("## 📊 이번 달 운영 요약")

    df = st.session_state.get("raw_settle_df")
    if df is not None:
        total_send = len(df)
        total_amount = df["금액"].sum() if "금액" in df.columns else 0

        st.markdown(f"""
            <div style="
                background:white; padding:20px; border-radius:12px;
                box-shadow:0 2px 8px rgba(0,0,0,0.06);">
                <h3>📌 이번 달 총 발송량: {total_send:,} 건</h3>
                <h3>💰 총 대금청구 금액: {total_amount:,} 원</h3>
            </div>
        """, unsafe_allow_html=True)

    # --------------------------
    # 유튜브
    # --------------------------
    st.markdown("## 📺 쉬어가기…")
    st.video(settings.get("youtube_url"))

