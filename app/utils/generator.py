import pandas as pd
import io
from datetime import datetime


def generate_settlement_excel(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    return buf.read()


def generate_bill(df: pd.DataFrame, save_path="대금청구서_원본.xlsx"):
    """
    기관별 sheet로 나눠서 대금청구서 원본 엑셀 생성
    (로컬 저장용 – Streamlit 클라우드에서는 경로만 참고)
    """
    writer = pd.ExcelWriter(save_path, engine="openpyxl")

    for 기관 in df["기관명"].dropna().unique():
        sub = df[df["기관명"] == 기관]
        sheet = str(기관)[:31]
        sub.to_excel(writer, sheet_name=sheet, index=False)

    writer.close()
    return save_path


def generate_draft_text(summary_df: pd.DataFrame, period_label: str) -> str:
    """
    정산 요약(기관별 합산 DF) + 기간 라벨(예: '2025년 9월분')을 받아
    기안문 초안 텍스트 생성.
    summary_df: 컬럼에 ['기관명','부서명','총금액'] 존재한다고 가정
    """
    today = datetime.today().strftime("%Y년 %m월 %d일")

    lines = []
    lines.append(f"{period_label} 전자고지 수수료 정산(안)")
    lines.append("")
    lines.append("1. 제안배경")
    lines.append(
        "   ○ 당사는 전자고지 서비스 제공에 따른 3사(카카오, KT, 네이버) 발송 및 인증 수수료를 "
        "기관별로 정산하여 대금 청구를 진행하고자 합니다."
    )
    lines.append("")
    lines.append("2. 정산 내역 요약")
    total = summary_df["총금액"].sum()
    lines.append(f"   ○ 전체 정산 금액 합계: {total:,.0f}원")
    lines.append("   ○ 기관별 정산 금액은 아래와 같습니다.")
    lines.append("")

    # 기관/부서별 상세
    for _, row in summary_df.iterrows():
        기관 = row.get("기관명", "")
        부서 = row.get("부서명", "")
        금액 = row.get("총금액", 0)
        lines.append(f"     - {기관} {부서}: {금액:,.0f}원")

    lines.append("")
    lines.append("3. 요청 사항")
    lines.append(
        "   ○ 상기 정산 내역을 검토하시어 이상이 없을 경우, "
        "대금 청구 및 수금 절차를 진행할 수 있도록 승인 요청드립니다."
    )
    lines.append("")
    lines.append(f"4. 기타")
    lines.append(
        "   ○ 세부 산출 근거(발송 건수, 인증 건수, 단가, 플랫폼별 내역 등)는 "
        "첨부된 정산 결과 엑셀을 참고 바랍니다."
    )
    lines.append("")
    lines.append(f"작성일자: {today}")
    lines.append("작성부서: 전자문서사업부")
    lines.append("작성자: __________________")

    return "\n".join(lines)

