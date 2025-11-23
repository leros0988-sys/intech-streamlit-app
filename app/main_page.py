import streamlit as st
from app.style import apply_global_styles

def main_page():
    apply_global_styles()

    # ------------------------------------
    # ① 중앙 이미지 (토끼 & 곰)
    # ------------------------------------
    st.markdown(
        "<div style='display:flex; justify-content:center; margin-top:20px; margin-bottom:10px;'>",
        unsafe_allow_html=True
    )
    st.image("app/images/imagesusagi_kuma.png", width=380)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    # ------------------------------------
    # ② 메인 제목 (네가 원하는 사이즈 적용)
    # ------------------------------------
    st.markdown("""
        <div class="title-text"
            style="
                font-size:38px;
                font-weight:1200;
                text-align:center;
                margin-bottom:28px;">
            📱 아이앤텍 전자고지 대금청구서 대시보드
        </div>
    """, unsafe_allow_html=True)

    # ------------------------------------
    # ③ 한 줄 환영 문구
    # ------------------------------------
    st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <h1 style="font-size:28px; font-weight:700; color:#333;">
                환영합니다!  당신의 이름은 무엇인가요? 💖
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # ------------------------------------
    # 이름 입력창 (placeholder)
    # ------------------------------------
    username = st.text_input(
        "",
        placeholder="이름을 입력해주세요.",
        label_visibility="collapsed"
    )

    # ------------------------------------
    # 인사문구 (이름 없어도 안 뜨는 게 더 자연스러움)
    # ------------------------------------
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
                추운 겨울이 다가왔어요! 따숩게 입고 다니세요. ❄️
            </div>
        """, unsafe_allow_html=True)

    # ------------------------------------
    # ④ 운영 안내 박스
    # ------------------------------------
    st.markdown("""
        <div style="
            background:white;
            border-radius:12px;
            padding:20px 25px;
            margin-top:10px;
            margin-bottom:35px;
            box-shadow:0 2px 12px rgba(0,0,0,0.06);
        ">
            <h3 style="margin:0; padding:0; font-size:22px;">📌 운영 안내</h3>
            <p style="font-size:17px; margin-top:10px;">
                전자고지 발송, 관리, 정산 기능을 보다 쉽게 사용할 수 있도록 제작되었습니다.<br>
                좌측 메뉴에서 원하는 기능을 선택해 이용해 주세요 🐻‍❄️
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ------------------------------------
    # ⑤ 방명록
    # ------------------------------------
    st.markdown("## 💬 방명록")

    if "guestbook" not in st.session_state:
        st.session_state.guestbook = []

    # 이름 없으면 자동 "익명"
    writer_name = username if username.strip() != "" else "익명"

    # 댓글 입력창 (이름 없어도 무조건 보임)
    comment = st.text_area("남기고 싶은 말을 적어주세요 ✨", height=60)

    if st.button("🌼 방명록 남기기"):
        if comment.strip():
            st.session_state.guestbook.append({"name": writer_name, "text": comment})
            st.success("작성되었습니다!")
            st.rerun()
        else:
            st.warning("내용을 입력해주세요!")

    # 방명록 출력
    if len(st.session_state.guestbook) == 0:
        st.info("아직 방명록이 비어있어요. 첫 글을 남겨보세요! ✏️")
    else:
        st.write("")
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

            # 삭제 버튼 (텍스트만 "삭제하기")
            if st.button("삭제하기", key=f"delete_{real_idx}"):
                st.session_state.guestbook.pop(real_idx)
                st.rerun()

    # ------------------------------------
    # ⑥ 유튜브 영상
    # ------------------------------------
    st.markdown("## 📺 쉬어가기...")
    st.video("https://youtu.be/0f2x_3zlz4I")
