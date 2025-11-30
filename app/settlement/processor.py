import re
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple

import pandas as pd


# -----------------------------
#  데이터 구조 정의
# -----------------------------
@dataclass
class OrgSummary:
    org_name: str
    charge_name: str          # 청구명 (구분에서 괄호 안)
    region: str               # 지역명 (수원시, 평택시 등)
    total_amount: int         # 정산금액 (당월)
    vat_amount: int           # 부가세
    is_kakao_only: bool       # 카카오 단일 여부
    has_vat: bool             # 부가세 별도 여부
    pdf_type: Literal["kakao", "multi"]  # PDF 템플릿 유형


@dataclass
class OverviewResult:
    # ① 총 매출
    total_amount: int
    kakao_amount: int
    multi_amount: int

    # ② 대금청구서 발행 건수
    invoice_count_total: int
    invoice_count_kakao: int
    invoice_count_multi: int

    # ③ VAT
    vat_included_amount: int
    vat_excluded_amount: int
    vat_included_orgs: List[str]
    vat_excluded_orgs: List[str]

    # ④ 지역
    region_amounts: Dict[str, int]

    # ⑤ TOP 3
    top3: List[Tuple[str, int]]

    # ⑥ PDF 유형별 집계
    pdf_kakao_count: int
    pdf_multi_count: int


class SettlementProcessor:
    """
    2025 발송료 + 기안자료 + 카카오 통계 3개 DataFrame을 기반으로
    - 기관별 정산 요약
    - 전체 합계
    - VAT 집계
    - 지역별 집계
    - TOP3
    - PDF 유형 집계
    - 누락기관 추출(Settle ID 기준)
    을 수행하는 엔진.
    """

    def __init__(
        self,
        rates_df: pd.DataFrame,
        drafts_df: pd.DataFrame,
        kakao_df: pd.DataFrame,
    ):
        self.rates_df = rates_df.copy()
        self.drafts_df = drafts_df.copy()
        self.kakao_df = kakao_df.copy()

        # 내부 캐시
        self.org_rows: List[OrgSummary] = []
        self.missing_settle_ids: List[str] = []

    # -----------------------------
    #  유틸: 문자열 정리 & 지역 추출
    # -----------------------------
    @staticmethod
    def _clean_str(x) -> str:
        if pd.isna(x):
            return ""
        return str(x).strip()

    @staticmethod
    def _parse_org_and_charge(from_gubun: str) -> Tuple[str, str]:
        """
        구분 예시: '수원시 영통구청(영통3동 주민등록증 재발급 안내문)'
        → ('수원시 영통구청', '영통3동 주민등록증 재발급 안내문')
        """
        txt = from_gubun.strip()
        m = re.match(r"^(.*)\((.*)\)$", txt)
        if m:
            return m.group(1).strip(), m.group(2).strip()
        return txt, ""  # 괄호 없으면 전체를 기관명으로

    @staticmethod
    def _extract_region(org_name: str) -> str:
        """
        기관명에서 지역명 추출.
        예: '수원시 영통구청' → '수원시'
            '평택시종합관제사업소' → '평택시'
            그 외 → '전국'
        """
        # ○○시, ○○군, ○○구 패턴
        m = re.search(r"([가-힣]+시)", org_name)
        if m:
            return m.group(1)

        m = re.search(r"([가-힣]+군)", org_name)
        if m:
            return m.group(1)

        m = re.search(r"([가-힣]+구)", org_name)
        if m:
            return m.group(1)

        return "전국"

    @staticmethod
    def _normalize_yes(value) -> bool:
        """부가세 여부 등 '예/과세/O/Y' 계열을 True 로 취급."""
        s = str(value).strip().upper()
        return s in {"Y", "O", "YES", "예", "과세", "별도"}

    # -----------------------------
    #  1) 카카오 단일 / 다수기관 판별용 맵 생성
    # -----------------------------
    def _build_org_type_map(self) -> Dict[str, bool]:
        """
        rates_df(2025 발송료) 기준으로
        - 카카오만 사용하는 기관 → True
        - 카카오+KT 등 다중 중계자 → False
        """
        org_type: Dict[str, bool] = {}

        for _, row in self.rates_df.iterrows():
            기관명 = self._clean_str(row.get("기관명", ""))

            if not 기관명:
                continue

            carrier1 = self._clean_str(row.get("중계자(1)", ""))
            carrier2 = self._clean_str(row.get("중계자(2)", ""))
            carrier3 = self._clean_str(row.get("중계자(3)", ""))

            carriers = {c for c in [carrier1, carrier2, carrier3] if c}

            if not carriers:
                # 중계자 정보 없으면 일단 다수기관으로 보지 않고 False
                org_type[기관명] = False
                continue

            # 카카오만 있으면 True, 그 외는 False
            if carriers == {"카카오"}:
                org_type[기관명] = True
            else:
                org_type[기관명] = False

        return org_type

    # -----------------------------
    #  2) VAT 여부 맵 생성
    # -----------------------------
    def _build_vat_map(self) -> Dict[str, bool]:
        """
        rates_df 기준으로 기관별 VAT 여부를 판단.
        - '부가세' 컬럼 값이 예/과세/Y 이면 True (부가세 별도)
        """
        vat_map: Dict[str, bool] = {}

        for _, row in self.rates_df.iterrows():
            기관명 = self._clean_str(row.get("기관명", ""))
            if not 기관명:
                continue

            vat_flag = self._normalize_yes(row.get("부가세", ""))
            vat_map[기관명] = vat_flag

        return vat_map

    # -----------------------------
    #  3) 기안자료 → OrgSummary 리스트 구축
    # -----------------------------
    def build_org_rows(self):
        """
        기안자료에서 한 줄 = 기관+청구명 1건으로 보고,
        OrgSummary 리스트를 채운다.
        """
        org_type_map = self._build_org_type_map()
        vat_map = self._build_vat_map()

        rows: List[OrgSummary] = []

        df = self.drafts_df.copy()
        # 칼럼명은 실제 기안자료 기준으로 맞추어야 함
        # 예: 순번, 구분, 발송료, 인증료, 부가세, 금액, 정산금액 등
        for _, row in df.iterrows():
            gubun = self._clean_str(row.get("구분", ""))
            if not gubun:
                continue

            org_name, charge_name = self._parse_org_and_charge(gubun)

            # 정산금액이 없으면 '금액' 컬럼을 사용 (파일 구조에 따라 조정)
            amount = row.get("정산금액", None)
            if pd.isna(amount):
                amount = row.get("금액", 0)
            try:
                amount_int = int(round(float(amount)))
            except Exception:
                amount_int = 0

            vat_value = row.get("부가세", 0)
            try:
                vat_int = int(round(float(vat_value)))
            except Exception:
                vat_int = 0

            is_kakao_only = org_type_map.get(org_name, False)
            has_vat = vat_map.get(org_name, vat_int > 0)
            pdf_type: Literal["kakao", "multi"] = "kakao" if is_kakao_only else "multi"

            region = self._extract_region(org_name)

            rows.append(
                OrgSummary(
                    org_name=org_name,
                    charge_name=charge_name,
                    region=region,
                    total_amount=amount_int,
                    vat_amount=vat_int,
                    is_kakao_only=is_kakao_only,
                    has_vat=has_vat,
                    pdf_type=pdf_type,
                )
            )

        self.org_rows = rows

    # -----------------------------
    #  4) 누락기관(Settle ID 기준) 추출
    # -----------------------------
    def build_missing_settle_ids(self):
        """
        카카오 통계에는 있는데, 2025 발송료(또는 기안자료)에 없는
        Settle ID 목록을 찾는다.
        """
        kakao_ids = set(
            self._clean_str(x) for x in self.kakao_df.get("Settle ID", []) if self._clean_str(x)
        )

        master_ids = set(
            self._clean_str(x)
            for x in self.rates_df.get("카카오 settle id", [])
            if self._clean_str(x)
        )

        missing = sorted(list(kakao_ids - master_ids))
        self.missing_settle_ids = missing

    # -----------------------------
    #  5) 전체 요약 계산
    # -----------------------------
    def calc_overview(self) -> OverviewResult:
        """
        self.org_rows 를 기반으로 ①~⑥까지 집계 값을 리턴.
        """
        if not self.org_rows:
            self.build_org_rows()

        total_amount = sum(r.total_amount for r in self.org_rows)
        kakao_amount = sum(r.total_amount for r in self.org_rows if r.is_kakao_only)
        multi_amount = sum(r.total_amount for r in self.org_rows if not r.is_kakao_only)

        invoice_count_total = len(self.org_rows)
        invoice_count_kakao = len([r for r in self.org_rows if r.is_kakao_only])
        invoice_count_multi = len([r for r in self.org_rows if not r.is_kakao_only])

        vat_included_amount = sum(r.total_amount for r in self.org_rows if not r.has_vat)
        vat_excluded_amount = sum(r.total_amount for r in self.org_rows if r.has_vat)

        vat_included_orgs = sorted({r.org_name for r in self.org_rows if not r.has_vat})
        vat_excluded_orgs = sorted({r.org_name for r in self.org_rows if r.has_vat})

        region_amounts: Dict[str, int] = {}
        for r in self.org_rows:
            region_amounts.setdefault(r.region, 0)
            region_amounts[r.region] += r.total_amount

        # 기관별 TOP 3
        org_amounts: Dict[str, int] = {}
        for r in self.org_rows:
            org_amounts.setdefault(r.org_name, 0)
            org_amounts[r.org_name] += r.total_amount

        top3 = sorted(org_amounts.items(), key=lambda x: x[1], reverse=True)[:3]

        pdf_kakao_count = len([r for r in self.org_rows if r.pdf_type == "kakao"])
        pdf_multi_count = len([r for r in self.org_rows if r.pdf_type == "multi"])

        return OverviewResult(
            total_amount=total_amount,
            kakao_amount=kakao_amount,
            multi_amount=multi_amount,
            invoice_count_total=invoice_count_total,
            invoice_count_kakao=invoice_count_kakao,
            invoice_count_multi=invoice_count_multi,
            vat_included_amount=vat_included_amount,
            vat_excluded_amount=vat_excluded_amount,
            vat_included_orgs=vat_included_orgs,
            vat_excluded_orgs=vat_excluded_orgs,
            region_amounts=region_amounts,
            top3=top3,
            pdf_kakao_count=pdf_kakao_count,
            pdf_multi_count=pdf_multi_count,
        )

    # -----------------------------
    #  6) PDF/엑셀용 상세 DF 반환
    # -----------------------------
    def to_detail_dataframe(self) -> pd.DataFrame:
        """
        OrgSummary 리스트를 DataFrame으로 변환.
        PDF/엑셀 상세내역 생성의 베이스가 된다.
        """
        if not self.org_rows:
            self.build_org_rows()

        data = []
        for r in self.org_rows:
            data.append(
                {
                    "기관명": r.org_name,
                    "청구명": r.charge_name,
                    "지역": r.region,
                    "정산금액": r.total_amount,
                    "부가세": r.vat_amount,
                    "카카오전용": "Y" if r.is_kakao_only else "N",
                    "VAT별도": "Y" if r.has_vat else "N",
                    "PDF유형": r.pdf_type,
                }
            )
        return pd.DataFrame(data)

    def get_missing_settle_ids(self) -> List[str]:
        if not self.missing_settle_ids:
            self.build_missing_settle_ids()
        return self.missing_settle_ids
