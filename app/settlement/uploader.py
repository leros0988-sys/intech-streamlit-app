import pandas as pd
from typing import NamedTuple, BinaryIO, Optional


class MasterData(NamedTuple):
    """2025 전자고지 정산 마스터에서 필요한 시트들."""
    rates: pd.DataFrame      # 2025년 발송료
    drafts: pd.DataFrame     # 기안자료


def _find_sheet(excel: pd.ExcelFile, candidates: list[str]) -> str:
    """
    파일명이 아니라 '시트명'을 기준으로 찾는다.
    - 완전 일치 먼저
    - 없으면 공백 제거 + 부분 일치로 한 번 더 시도
    """
    norm = lambda s: s.replace(" ", "").strip().lower()

    sheet_map = {sheet: norm(sheet) for sheet in excel.sheet_names}

    # 1차: 완전 일치
    for cand in candidates:
        nc = norm(cand)
        for sheet, ns in sheet_map.items():
            if ns == nc:
                return sheet

    # 2차: 부분 포함
    for cand in candidates:
        nc = norm(cand)
        for sheet, ns in sheet_map.items():
            if nc in ns:
                return sheet

    raise ValueError(
        f"필수 시트를 찾을 수 없습니다. 후보: {candidates}, "
        f"실제 시트: {excel.sheet_names}"
    )


def load_master_workbook(file_obj: BinaryIO) -> MasterData:
    """
    아이앤텍 '2025 전자고지 정산 시트' 마스터에서
    - 2025년 발송료 시트
    - 기안자료 시트
    두 개만 읽어온다.
    파일명은 전혀 사용하지 않는다.
    """
    xls = pd.ExcelFile(file_obj, engine="openpyxl")

    rate_sheet_name = _find_sheet(xls, ["2025년 발송료", "2025 발송료"])
    draft_sheet_name = _find_sheet(xls, ["기안자료"])

    rates = pd.read_excel(xls, sheet_name=rate_sheet_name)
    drafts = pd.read_excel(xls, sheet_name=draft_sheet_name)

    # 완전 빈 행, 전부 NaN인 행은 미리 정리
    rates = rates.dropna(how="all")
    drafts = drafts.dropna(how="all")

    return MasterData(rates=rates, drafts=drafts)


def load_kakao_stats(file_obj: BinaryIO, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    카카오 월별 정산 엑셀을 읽는다.
    - 기본: 첫 번째 시트
    - 필요하면 sheet_name으로 명시 가능
    - 여기서는 구조를 깨지 않고 그대로 넘긴 뒤,
      나중 processor에서 컬럼(일자, 기관명, Settle ID 등)을 사용해 가공한다.
    """
    xls = pd.ExcelFile(file_obj, engine="openpyxl")

    if sheet_name is None:
        target_sheet = xls.sheet_names[0]
    else:
        # 시트명을 정확히 입력하지 않아도 되도록 느슨하게 매칭
        target_sheet = _find_sheet(xls, [sheet_name])

    df = pd.read_excel(xls, sheet_name=target_sheet)
    df = df.dropna(how="all")

    return df
