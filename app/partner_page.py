import streamlit as st


def partner_page():
    st.markdown("## 🤝 협력사 정산")

    st.info("에프원 / 엑스아이티 정산 로직은 추후 단가표 기준으로 계산 로직을 넣을 예정.")
    st.write("- 에프원: 발송 60원, 인증 0원")
    st.write("- 엑스아이티: 발송 20원, 인증 10원")

    st.warning("지금은 구조만 잡아두었어요 ㅠㅠ 개발자분들이 고쳐주시겠지.")
