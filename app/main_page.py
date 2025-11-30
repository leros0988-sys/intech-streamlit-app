# ---------------------------------------------------------
# 🔥 메인 페이지 - 유튜브 영상 정상 재생 완전판 (오류 153 방지)
# ---------------------------------------------------------

import streamlit as st
import streamlit.components.v1 as components
from app.style import apply_global_styles
from app.utils.loader import load_settings


def main_page():
    apply_global_styles()
    settings = load_settings()

    # ------------------------------------------------------
    # 상단 이미지
    # ------------------------------------------------------
    st.markdown(
        "<div style='display:flex; justify-content:center; margin-top:20px; margin-bottom:10px;'>",
        unsafe_allow_html=True
    )
    st.image(settings.get("main_image_path", "app/images/imagesusagi_kuma.png"), width=380)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    # ------------------------------------------------------
    # 메인 제목
    # ------------------------------------------------------
    st.markdown("""
        <div style="
            font-size:34px;
            font-weight:900;
            text-align:center;
            margin-bottom:28px;">
            📱 아이앤텍 전자고지 대금청구서 대시보드 📱
        </div>
    """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # 정산 요약
    # ------------------------------------------------------
    df = st.session_state.get("raw_df")
    total_statements = 0
    total_amount = 0

    if df is not None:
        if "카카오 settle id" in df.columns:
            total_statements = df["카카오 settle id"].dropna().astype(str).nunique()

        amount_col = None
        for cand in ["금액", "청구금액", "정산금액", "합계"]:
            if cand in df.columns:
                amount_col = cand
                break

        if amount_col:
            total_amount = df[amount_col].fillna(0).sum()

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
            <h3 style="margin:0; padding:0; font-size:22px;"> 12월 정산 요약</h3>
            <p style="font-size:17px; margin-top:10px;">
                • 12월 총 대금청구서 : <b>{total_statements:,} 건</b><br>
                • 12월 총 정산 금액 : <b>{total_amount:,} 원</b><br>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------
    # 공지사항
    # ------------------------------------------------------
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
            <h3 style="margin:0; padding:0; font-size:22px;">공지사항</h3>
            <p style="font-size:17px; margin-top:10px;">
                {settings.get("dashboard_text")}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------
    # 이름 입력
    # ------------------------------------------------------
    st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <h1 style="font-size:28px; font-weight:700; color:#333;">
                환영합니다!  당신의 이름은 무엇인가요? 💖
            </h1>
        </div>
    """, unsafe_allow_html=True)

    username = st.text_input(
        "",
        placeholder="이름을 입력해주세요.",
        label_visibility="collapsed"
    )

    if username.strip() != "":
        st.markdown(f"""
            <div style="
                background:#fff7fb;
                padding:18px 22px;
                border-radius:12px;
                margin-top:15px;
                margin-bottom:30px;
                text-align:center;
                font-size:19px;
                box-shadow:0 2px 8px rgba(0,0,0,0.07);
            ">
                🌼 <strong>{username}</strong> 님,<br>
                날씨가 많이 추워졌네요. 따숩게 입고 다니세요. ❄️
            </div>
        """, unsafe_allow_html=True)

    # ------------------------------------------------------
    # 방명록 기능
    # ------------------------------------------------------
    st.markdown("## 💬 방명록")

    if "guestbook" not in st.session_state:
        st.session_state.guestbook = []

    writer = username if username.strip() else "익명"
    comment = st.text_area("남기고 싶은 말을 적어주세요 ✨", height=60)

    if st.button("🌼 방명록 남기기"):
        if comment.strip():
            st.session_state.guestbook.append({"name": writer, "text": comment})
            st.success("작성되었습니다!")
            st.rerun()
        else:
            st.warning("내용을 입력해주세요.")

    if len(st.session_state.guestbook) == 0:
        st.info("아직 방명록이 비어있어요. 첫 글을 남겨보세요! ✏️")
    else:
        for idx, item in enumerate(reversed(st.session_state.guestbook)):
            true_idx = len(st.session_state.guestbook) - 1 - idx
            st.markdown(
                f"""
                <div style="
                    background:#fff9fb;
                    padding:14px 18px;
                    border-radius:12px;
                    margin-bottom:10px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.05);
                ">
                    <strong>{item['name']}</strong><br>
                    <span style="font-size:16px;">{item['text']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("삭제하기", key=f"del_{true_idx}"):
                st.session_state.guestbook.pop(true_idx)
                st.rerun()

    # ------------------------------------------------------
    # 🔥 유튜브 영상 (153 오류 없는 완전 안전 방식)
    # ------------------------------------------------------

    st.markdown("<div style='margin-top:40px;'></div>", unsafe_allow_html=True)

    youtube_url = "https://www.youtube.com/embed/0f2x_3zlz4I"  # ← 여기에 네 영상 ID만 교체하면 됨

    components.html(
        f"""
        <div style="display:flex; justify-content:center; margin-top:20px; margin-bottom:40px;">
            <iframe
                width="750"
                height="422"
                src="{youtube_url}"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowfullscreen>
            </iframe>
        </div>
        """,
        height=500,
    )
