import streamlit as st
import os
from app.utils.loader import load_settings, save_settings


def settings_page():
    st.markdown("<div class='title-text'>⚙ 설정</div>", unsafe_allow_html=True)

    # -------------------------------
    # 안전한 settings 로드
    # -------------------------------
    settings = load_settings()
    if settings is None:
        settings = {}   # ← None일 때만 초기화

    # -------------------------------
    # ① 메인 이미지 변경
    # -------------------------------
    st.markdown("### 🖼 메인 이미지 변경")

    current_path = settings.get("main_image_path", "(등록 없음)")
    st.caption(f"현재 이미지 경로: `{current_path}`")

    img_file = st.file_uploader("새 메인 이미지 업로드 (png/jpg)", type=["png", "jpg", "jpeg"])

    if img_file is not None:
        os.makedirs("app/images", exist_ok=True)

        save_path = os.path.join("app", "images", "updated_main_img.png")

        with open(save_path, "wb") as f:
            f.write(img_file.getbuffer())

        settings["main_image_path"] = save_path
        save_settings(settings)
        st.success("메인 이미지가 변경되었습니다!")

    # 즉시 표시
    if settings.get("main_image_path") and os.path.exists(settings["main_image_path"]):
        st.image(settings["main_image_path"], width=260)

    st.markdown("---")

    # -------------------------------
    # ② 대시보드 안내 문구
    # -------------------------------
    st.markdown("### 📝 메인 대시보드 안내 문구")

    guide_text = settings.get("dashboard_text", "")
    new_text = st.text_area("운영 안내 문구", value=guide_text, height=80)

    if st.button("운영 안내 문구 저장"):
        settings["dashboard_text"] = new_text
        save_settings(settings)
        st.success("운영 안내 문구 저장됨!")

    st.markdown("---")

    # -------------------------------
    # ③ 유튜브 링크
    # -------------------------------
    st.markdown("### 📺 메인 유튜브 링크")

    new_url = st.text_input("YouTube URL", value=settings.get("youtube_url", ""))

    if st.button("유튜브 링크 저장"):
        settings["youtube_url"] = new_url
        save_settings(settings)
        st.success("유튜브 링크 저장됨!")

    st.markdown("---")

    # -------------------------------
    # ④ 엑셀 파일 경로
    # -------------------------------
    st.markdown("### 📂 엑셀 파일 경로 설정")

    rate_path = st.text_input(
        "요율표(rate_table.xlsx) 경로",
        value=settings.get("rate_table_path", "rate_table.xlsx")
    )
    partner_path = st.text_input(
        "기관 담당자 DB(partner_db.xlsx) 경로",
        value=settings.get("partner_db_path", "partner_db.xlsx")
    )

    if st.button("엑셀 경로 저장"):
        settings["rate_table_path"] = rate_path
        settings["partner_db_path"] = partner_path
        save_settings(settings)
        st.success("엑셀 경로 저장됨!")

    st.markdown("---")

    # -------------------------------
    # ⑤ 보안 옵션
    # -------------------------------
    st.markdown("### 🔐 보안 옵션")

    login_fail_limit = st.number_input(
        "로그인 실패 허용 횟수",
        min_value=1,
        max_value=10,
        value=int(settings.get("login_fail_limit", 5)),
        step=1,
    )

    auto_logout_minutes = st.number_input(
        "자동 로그아웃 시간(분)",
        min_value=5,
        max_value=180,
        value=int(settings.get("auto_logout_minutes", 30)),
        step=5,
    )

    if st.button("보안 설정 저장"):
        settings["login_fail_limit"] = int(login_fail_limit)
        settings["auto_logout_minutes"] = int(auto_logout_minutes)
        save_settings(settings)
        st.success("보안 설정 저장됨!")
