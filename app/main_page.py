import streamlit as st
from app.style import apply_global_styles
from app.utils.loader import load_settings


# -----------------------------------------------------
# 🔥 유튜브 링크를 안전하게 embed로 변환하는 함수
#   (오류 153 방지: st.video() 대신 iframe 직접 삽입)
# -----------------------------------------------------
def embed_youtube(url: str):
    if not url:
        return

    # 1) youtu.be → watch?v=
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"

    # 2) shorts → watch?v=
    if "youtube.com/shorts/" in url:
        video_id = url.split("shorts/")[1].split("?")[0]
        url = f"https://www.youtube.com/watch?v={video_id}"

    # 3) m.youtube.com → www.youtube.com
    if "m.youtube.com" in url:
        url = url.replace("m.youtube.com", "www.youtube.com")

    # 4) watch?v= → embed 변환
    embed_url = url
    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1].split("&")[0]
        embed_url = f"https://www.youtube.com/embed/{video_id}"

    # 5) iframe 삽입
    st.components.v1.html(
        f"""
        <iframe width="100%" height="520"
        src="{embed_url}"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen></iframe>
        """,
        height=540
    )



# -----------------------------------------------------
# 📌 메인 페이지
# -----------------------------------------------------
def main_page():
    apply_global_styles()
    settings = load_settings()

    # ------------------------------------
    # 상단 이미지
    # ------------------------------------
    st.markdown(
        "<div style='display:flex; justify-content:center; margin-top:20px; margin-bottom:10px;'>",
        unsafe_allow_html=True
    )
    st.image(settings.get("main_image_path", "app/images/imagesusagi_kuma.png"), width=380)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    # ------------------------------------
    # 메인 제목
    # ------------------------------------
    st.markdown("""
        <div class="title-text"
            style="
                font-size:34px;
                font-weight:900;
                text-align:center;
                margin-bottom:28px;">
            📱 아이앤텍 전자고지 대금청구서 대시보드 📱
        </div>
    """, unsafe_allow_html=True)

    df = st.session_state.get("raw_df")
    total_statements = 0
    total_amount = 0

    if df is not None:
        # 카카오 settle id 기준 정산서 개수
        if "카카오 settle id" in df.columns:
            total_statements = df["카카오 settle id"].dropna().astype(str).nunique()

        # 금액 컬럼 탐색
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

    # ------------------------------------
    # 공지사항
    # ------------------------------------
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

    # ------------------------------------
    # 이름 입력
    # ------------------------------------
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

    # ------------------------------------
    # 방명록
    # ------------------------------------
    st.markdown("## 💬 방명록")

    if "guestbook" not in st.session_state:
        st.session_state.guestbook = []

    writer_name = username if username.strip() != "" else "익명"
    comment = st.text_area("남기고 싶은 말을 적어주세요 ✨", height=60)

    if st.button("🌼 방명록 남기기"):
        if comment.strip():
            st.session_state.guestbook.append({"name": writer_name, "text": comment})
            st.success("작성되었습니다!")
            st.rerun()
        else:
            st.warning("내용을 입력해주세요!")

    if len(st.session_state.guestbook) == 0:
        st.info("아직 방명록이 비어있어요. 첫 글을 남겨보세요! ✏️")
    else:
        for idx, item in enumerate(reversed(st.session_state.guestbook)):
            real_idx = len(st.session_state.guestbook) - 1 - idx

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

            if st.button("삭제하기", key=f"delete_{real_idx}"):
                st.session_state.guestbook.pop(real_idx)
                st.rerun()

    # ------------------------------------
    # 유튜브 영상 재생 (오류 153 완전 방지)
    # ------------------------------------
    st.markdown("## 📺 쉬어가기")
    embed_youtube(settings.get("youtube_url", ""))

