"""
app/utils/generator.py

- (주)아이앤텍 2025년 전자고지 정산 시트 템플릿을 이용해서
  기관별 대금청구서 엑셀(+선택적으로 PDF)을 만들어 주는 모듈.

이 모듈은 "엑셀 템플릿을 어떻게 채울지"만 책임진다.
3사 통계를 어떻게 요약해서 넘겨줄지는 finance_page 쪽에서 처리하면 된다.
"""

from __future__ import annotations

import os
import subprocess
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Literal, Optional, Tuple

import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet


ChannelCombo = Literal["kakao_only", "kakao_kt", "kakao_kt_naver"]


# ======================================================================
#  기본 자료형
# ======================================================================

@dataclass
class MonthlyCount:
    """월간 합계 건수 (발송 / 인증)."""
    send: int = 0
    auth: int = 0

    @classmethod
    def from_any(cls, data: Dict) -> "MonthlyCount":
        """
        dict 로 들어온 값을 안전하게 int 로 변환해서 MonthlyCount 로 만든다.
        키 이름은 자유롭게 쓰되, 기본적으로 '발송', '인증', 'send', 'auth' 를 우선 사용.
        """
        def _pick(d: Dict, keys: Iterable[str]) -> int:
            for k in keys:
                if k in d and pd.notna(d[k]):
                    try:
                        return int(d[k])
                    except Exception:
                        pass
            return 0

        send = _pick(data, ["발송", "발송건수", "송신", "send"])
        auth = _pick(data, ["인증", "인증건수", "열람시인증", "auth"])
        return cls(send=send, auth=auth)


# ======================================================================
#  채널 조합 판별
# ======================================================================

def detect_channel_combo(channels: Iterable[str]) -> ChannelCombo:
    """
    채널 문자열 목록을 보고
    - 카카오만 있으면 kakao_only
    - 카카오 + KT (네이버 없음) 이면 kakao_kt
    - 카카오 + 네이버 / 카카오 + KT + 네이버 는 kakao_kt_naver 로 본다.
    """
    lower = {str(ch).lower() for ch in channels}
    has_kakao = any("kakao" in ch or "카카오" in ch for ch in lower)
    has_kt = any("kt" in ch for ch in lower)
    has_naver = any("naver" in ch or "네이버" in ch for ch in lower)

    # 기본적으로 카카오는 항상 있다고 가정 (전자고지 기준)
    if has_kakao and not has_kt and not has_naver:
        return "kakao_only"
    if has_kakao and has_kt and not has_naver:
        return "kakao_kt"
    # 카카오 + 네이버 / 카카오 + KT + 네이버 모두 여기로
    return "kakao_kt_naver"


# ======================================================================
#  내부 유틸 함수들
# ======================================================================

def _ensure_dir(path: Path) -> None:
    """파일을 저장하기 전에 상위 폴더가 없으면 만들어준다."""
    path.parent.mkdir(parents=True, exist_ok=True)


def _day_from_value(v) -> Optional[int]:
    """
    Kakao 일자 컬럼 값에서 '일(day)' 을 뽑는다.
    - datetime / Timestamp -> .day
    - '2025-09-01' 같은 문자열 -> pandas 로 파싱 시도
    - '1', '01' 같은 문자열 -> int
    """
    if pd.isna(v):
        return None

    # pandas Timestamp / datetime 계열
    if hasattr(v, "day"):
        try:
            d = int(v.day)
            if 1 <= d <= 31:
                return d
        except Exception:
            pass

    # 숫자 직접 들어온 경우 (1, 2, 3 ...)
    if isinstance(v, (int, float)):
        d = int(v)
        if 1 <= d <= 31:
            return d

    # 문자열일 경우
    if isinstance(v, str):
        v = v.strip()
        # 순수 숫자
        if v.isdigit():
            d = int(v)
            if 1 <= d <= 31:
                return d
        # 날짜 형식으로 한 번 더 시도
        try:
            parsed = pd.to_datetime(v, errors="raise")
            d = int(parsed.day)
            if 1 <= d <= 31:
                return d
        except Exception:
            pass

    return None


def _aggregate_kakao_daily(
    kakao_daily_df: pd.DataFrame,
    date_col: str,
    send_col: str,
    auth_col: str,
) -> Dict[int, Tuple[int, int]]:
    """
    카카오 일자별 데이터에서
    - key: 일(day: 1~31)
    - value: (발송합계, 인증합계)
    로 모아준다.
    """
    # 컬럼 이름이 살짝 달라도 되도록 대소문자/공백을 느슨하게 처리
    def _resolve_col(df: pd.DataFrame, target: str, default: str) -> str:
        if target in df.columns:
            return target
        # "발송 건수" vs "발송건수" 등 유사한 것 찾아보기
        target_norm = target.replace(" ", "")
        for c in df.columns:
            if c == target:
                return c
            if c.replace(" ", "") == target_norm:
                return c
        # 못 찾으면 default
        return default

    if kakao_daily_df.empty:
        return {}

    date_col = _resolve_col(kakao_daily_df, date_col, kakao_daily_df.columns[0])
    send_col = _resolve_col(kakao_daily_df, send_col, kakao_daily_df.columns[1])
    auth_col = _resolve_col(kakao_daily_df, auth_col, kakao_daily_df.columns[2])

    result: Dict[int, Tuple[int, int]] = {}

    for _, row in kakao_daily_df.iterrows():
        day = _day_from_value(row[date_col])
        if day is None:
            continue

        send = row.get(send_col, 0)
        auth = row.get(auth_col, 0)

        try:
            send_i = int(send) if pd.notna(send) else 0
        except Exception:
            send_i = 0
        try:
            auth_i = int(auth) if pd.notna(auth) else 0
        except Exception:
            auth_i = 0

        cur_send, cur_auth = result.get(day, (0, 0))
        result[day] = (cur_send + send_i, cur_auth + auth_i)

    return result


def _fill_kakao_daily_to_sheet(
    ws_detail: Worksheet,
    daily_map: Dict[int, Tuple[int, int]],
) -> None:
    """
    '상세내역' 또는 '상세내역(다수)' 시트에
    day -> (발송, 인증) 정보를 넣는다.

    템플릿 기준:
    - 1일은 row 10, 2일은 row 11 ... 31일은 row 40
    - 발송건수: 열 D
    - 인증건수: 열 G
    기존에 들어있던 수식(전체DB 참조)은 전부 덮어쓴다.
    """
    # 먼저 기존 값(혹시 수동 입력된 것/수식)이 있다면 모두 지워준다.
    for row in range(10, 41):  # 10 ~ 40
        ws_detail[f"D{row}"] = None
        ws_detail[f"G{row}"] = None

    for day, (send, auth) in daily_map.items():
        if not (1 <= day <= 31):
            continue
        row = 9 + int(day)  # 1일 -> 10행
        ws_detail[f"D{row}"] = int(send)
        ws_detail[f"G{row}"] = int(auth)


def _convert_xlsx_to_pdf(xlsx_path: Path, pdf_path: Path) -> None:
    """
    리브레오피스(soffice)가 깔려있는 환경이라면
    엑셀 파일을 PDF 로 변환해 준다.

    Streamlit Cloud 에서는 동작하지 않을 수 있으니,
    실패해도 에러를 죽이지 말고 조용히 무시한다.
    """
    try:
        # libreoffice / soffice 둘 중 하나 있는지 시도
        cmd_candidates = ["libreoffice", "soffice"]
        exe = None
        for c in cmd_candidates:
            if shutil.which(c):
                exe = c
                break
        if exe is None:
            return

        out_dir = str(pdf_path.parent)
        subprocess.run(
            [
                exe,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                out_dir,
                str(xlsx_path),
            ],
            check=True,
        )

        # 리브레오피스는 보통 같은 파일명을 .pdf 로 뱉는다.
        # 우리가 원하는 pdf_path 와 이름이 다를 수도 있으니 맞춰준다.
        default_pdf = xlsx_path.with_suffix(".pdf")
        if default_pdf.exists() and default_pdf != pdf_path:
            default_pdf.replace(pdf_path)

    except Exception:
        # 변환 실패는 조용히 무시
        return


# ======================================================================
#  공개 엔트리포인트
# ======================================================================

def generate_single_org_invoice(
    *,
    template_path: str,
    out_xlsx_path: str,
    org_name: str,
    kakao_daily_df: pd.DataFrame,
    channel_combo: ChannelCombo = "kakao_only",
    kakao_date_col: str = "일자",
    kakao_send_col: str = "발송건수",
    kakao_auth_col: str = "인증건수",
    kt_monthly: Optional[Dict] = None,
    naver_monthly: Optional[Dict] = None,
    make_pdf: bool = False,
    out_pdf_path: Optional[str] = None,
) -> Dict[str, Optional[str]]:
    """
    단일 기관에 대한 대금청구서(엑셀, 선택적으로 PDF)를 생성한다.

    Parameters
    ----------
    template_path : str
        (주)아이앤텍 2025년 전자고지 정산 시트 템플릿 경로.
    out_xlsx_path : str
        생성될 기관별 엑셀 파일 경로.
    org_name : str
        기관명 (예: '수원시 장안구청(주정차위반과태료 사전고지)').
    kakao_daily_df : pd.DataFrame
        카카오 일자별 통계 DataFrame.
        최소한 [일자, 발송건수, 인증건수] 정보가 있어야 함.
    channel_combo : ChannelCombo, optional
        'kakao_only', 'kakao_kt', 'kakao_kt_naver'
    kt_monthly : dict, optional
        KT 월간 합계 {'발송': int, '인증': int, ...}
    naver_monthly : dict, optional
        NAVER 월간 합계 {'발송': int, '인증': int, ...}
    make_pdf : bool, optional
        True 이고, 서버 환경에 리브레오피스가 있다면 PDF 도 생성 시도.
    out_pdf_path : str, optional
        PDF 를 저장할 경로. None 이면 out_xlsx_path 와 같은 이름으로 .pdf 사용.

    Returns
    -------
    Dict[str, Optional[str]]
        {"xlsx": 엑셀경로, "pdf": pdf경로(생성되지 않으면 None)}
    """
    template_path = str(template_path)
    out_xlsx = Path(out_xlsx_path)
    _ensure_dir(out_xlsx)

    wb = load_workbook(template_path, data_only=False)

    # 1) 카카오 일일 데이터 집계
    daily_map = _aggregate_kakao_daily(
        kakao_daily_df,
        date_col=kakao_date_col,
        send_col=kakao_send_col,
        auth_col=kakao_auth_col,
    )
    kakao_monthly = MonthlyCount(
        send=sum(v[0] for v in daily_map.values()),
        auth=sum(v[1] for v in daily_map.values()),
    )

    # 2) 템플릿 종류에 따라 시트 선택
    if channel_combo == "kakao_only":
        # -------------------------------------------------------------
        # 카카오 단독 템플릿
        #   - 대금청구서
        #   - 상세내역
        # -------------------------------------------------------------
        ws_bill = wb["대금청구서"]
        ws_detail = wb["상세내역"]

        # 기관명 세팅
        # B8 = '충남 당진시 세무과' 자리에 기관명
        ws_bill["B8"] = org_name

        # 카카오 일자별 건수 -> 상세내역 시트 (D열 / G열)
        _fill_kakao_daily_to_sheet(ws_detail, daily_map)

        # 카카오 월간 합계를 굳이 직접 넣을 필요는 없음.
        # (상세내역의 합계 셀이 대금청구서 C8, D8 으로 연결되어 있음)
        # 필요하면 아래 주석을 풀어 명시적으로 적어도 됨.
        # ws_bill["C8"] = kakao_monthly.send
        # ws_bill["D8"] = kakao_monthly.auth

    else:
        # -------------------------------------------------------------
        # 카카오 + (KT, NAVER) 다수 템플릿
        #   - 대금청구서(다수)
        #   - 상세내역(다수)
        # -------------------------------------------------------------
        ws_bill = wb["대금청구서(다수)"]
        ws_detail = wb["상세내역(다수)"]

        # 기관명 세팅 (A32 셀)
        ws_bill["A32"] = org_name

        # 카카오 일자별 건수 -> 상세내역(다수)
        _fill_kakao_daily_to_sheet(ws_detail, daily_map)

        # 카카오 월간 합계 -> 8행 (C8 / D8)
        ws_bill["C8"] = kakao_monthly.send
        ws_bill["D8"] = kakao_monthly.auth

        # KT / NAVER 월간 합계도 있으면 넣어준다.
        if channel_combo in ("kakao_kt", "kakao_kt_naver") and kt_monthly is not None:
            kt_cnt = MonthlyCount.from_any(kt_monthly)
            ws_bill["C9"] = kt_cnt.send
            ws_bill["D9"] = kt_cnt.auth

        if channel_combo == "kakao_kt_naver" and naver_monthly is not None:
            nv_cnt = MonthlyCount.from_any(naver_monthly)
            ws_bill["C10"] = nv_cnt.send
            ws_bill["D10"] = nv_cnt.auth

    # 3) 엑셀 저장
    wb.save(str(out_xlsx))

    # 4) 필요하면 PDF 변환
    pdf_path_str: Optional[str] = None
    if make_pdf:
        # out_pdf_path 가 없으면 같은 경로에서 확장자만 .pdf 로 바꾼다.
        pdf_path = Path(out_pdf_path) if out_pdf_path else out_xlsx.with_suffix(".pdf")
        _ensure_dir(pdf_path)
        _convert_xlsx_to_pdf(out_xlsx, pdf_path)
        if pdf_path.exists():
            pdf_path_str = str(pdf_path)

    return {
        "xlsx": str(out_xlsx),
        "pdf": pdf_path_str,
    }
