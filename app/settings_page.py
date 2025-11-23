import streamlit as st
from utils.loader import load_settings, save_settings
import os

def settings_page():
    st.markdown("## ⚙️ 설정 메뉴")

    settings = load_settings()

    # ----------------------------
    # 파일 경로 설정
    # ----------------------------
    st.subheader("📁 파일 경로 설정")

    rate_path = st.text_input("요율표(rate_table.xlsx) 경로", settings.get("rate_table_path"))
    partner_path = st.text_input("기관담당자DB.xlsx 경로", settings.get("partner_db_path"))

    # ----------------------------
    # 메인 이미지 변경
    # ----------------------------
    st.subheader("🖼 메인 이미지 변경")

    uploaded_img = st.file_uploader("새 메인 이미지 업로드", type=["png", "jpg", "jpeg"])
    img_path = settings.get("main_image")

    if uploaded_img:
        save_path = f"app/images/updated_main_img.png"
        with open(save_path, "wb") as f:
            f.write(uploaded_img.read())
        img_path = save_path
        st.success("이미지 업데이트 완료!")

    # ----------------------------
    # Youtube 변경
    # ----------------------------
    st.subheader("📺 메인 페이지 유튜브 링크 변경")
    youtube = st.text_input("YouTube URL", settings.get("youtube_url"))

    # ----------------------------
    # 환영 문구 변경
    # ----------------------------
    st.subheader("💬 환영 문구 변경")
    welcome = st.text_input("메인 환영 문구", settings.get("welcome_text"))

    # ----------------------------
    # 저장 버튼
    # ----------------------------
    if st.button("💾 모든 설정 저장"):
        new_settings = {
            "rate_table_path": rate_path,
            "partner_db_path": partner_path,
            "main_image": img_path,
            "youtube_url": youtube,
            "welcome_text": welcome
        }
        save_settings(new_settings)
        st.success("설정이 저장되었습니다.")
        st.rerun()
