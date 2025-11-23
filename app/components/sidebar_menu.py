import streamlit as st


def draw_sidebar(is_admin: bool = False) -> str:
    """사이드바 라디오 메뉴 그리기 후 선택값 반환"""

    with st.sidebar:
        st.markdown("메뉴")

        # 기본 메뉴
        menu_items = [
            "메인 대시보드",
            "정산 업로드 및 전체 통계자료",
            "카카오 통계자료",
            "KT 통계자료",
            "네이버 통계자료",
            "협력사 정산",
            "기안 자료 생성",
        ]

        # 관리자용 메뉴 노출
        if is_admin:
            menu_items.extend(
                [
                    "관리자 메뉴",
                    "로그 조회",
                    "설정",
                ]
            )

        # 로그아웃은 항상 마지막에 따로
        menu_items.append("로그아웃")

        choice = st.radio(
            label="",
            options=menu_items,
            index=0,
        )

    return choice
