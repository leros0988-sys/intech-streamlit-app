import pandas as pd
from typing import Dict, List, Tuple


class SettlementSummary:
    """
    - kakao_df : 카카오 월별 정산 통계
    - rates_df : 2025년 발송료 시트
    - drafts_df: 기안자료 시트 (선택)
    를 기반으로 정산 요약(①~⑥)을 만들어주는 요약 엔진.
    """

    def __init__(
        self,
        kakao_df: pd.DataFrame,
        rates_df: pd.DataFrame,
        drafts_df: pd.DataFrame | None = None,
    ):
        self.kakao_df = kakao_df.copy()
        self.rates_df = rates_df.copy()
        self.drafts_df = drafts_df.copy() if drafts_df is not None else None

        self.kakao_id_col = "Settle ID"
        self.master_id_col = "카카오 settle id"

        self.kakao_amount_col = self._detect_kakao_amount_col()

    # ------------------------------------------------
    # 공통 유틸
    # ------------------------------------------------
    @staticmethod
    def _clean(v) -> str:
        if pd.isna(v):
            return ""
        return str(v).strip()

    def _detect_kakao_amount_col(self) -> str | None:
        """
        카카오 엑셀에서 금액 컬럼 자동 탐색
        (파일마다 '금액', '정산금액', '청구금액', '합계' 등 다를 수 있으므로)
        """
        candidates = ["금액", "정산금액", "청구금액", "합계", "총금액"]
        for c in candidates:
            if c in self.kakao_df.columns:
                return c
        return None

    # ------------------------------------------------
    # ① 총 매출
    # ------------------------------------------------
    def total_sales(self) -> Dict[str, int]:
        """
        카카오 총액, 다수기관 총액, 전체 총액
        """
        kakao_total = 0
        if self.kakao_amount_col:
            kakao_total = int(self.kakao_df[self.kakao_amount_col].fillna(0).sum())

        # 2025 발송료의 월별/합계 컬럼 기반
        month_cols = [
            "1월", "2월", "3월", "4월", "5월", "6월",
            "7월", "8월", "9월", "10월", "11월", "12월", "합 계"
        ]
        month_cols = [c for c in month_cols if c in self.rates_df.columns]

        multi_total = 0
        if month_cols:
            multi_total = int(self.rates_df[month_cols].fillna(0).astype(float).sum().sum())

        return {
            "카카오 총액": kakao_total,
            "다수기관 총액": multi_total,
            "전체 총액": kakao_total + multi_total,
        }

    # ------------------------------------------------
    # ② 대금청구서 발행 건수
    # ------------------------------------------------
    def bill_counts(self) -> Dict[str, int]:
        """
        - 카카오 발행 건수 : 카카오 엑셀에 등장한 고유 Settle ID 개수
        - 다수기관 발행 건수 : 2025 발송료에 등록된 고유 기관 수
        """
        kakao_cnt = 0
        if self.kakao_id_col in self.kakao_df.columns:
            kakao_cnt = (
                self.kakao_df[self.kakao_id_col]
                .dropna()
                .astype(str)
                .nunique()
            )

        if "기관명" in self.rates_df.columns:
            multi_cnt = (
                self.rates_df["기관명"]
                .dropna()
                .astype(str)
                .nunique()
            )
        else:
            multi_cnt = 0

        return {
            "카카오 발행 건수": kakao_cnt,
            "다수기관 발행 건수": multi_cnt,
            "전체 발행 건수": kakao_cnt + multi_cnt,
        }

    # ------------------------------------------------
    # ③ 부가세 포함 / 미포함
    # ------------------------------------------------
    def vat_summary(self) -> Dict[str, object]:
        """
        2025 발송료 시트의 '부가세' 컬럼 기준.
        - 부가세 > 0 : 부가세 별도 여야 하는 기관
        - 부가세 = 0 : VAT 포함(면세 또는 포함) 기관
        """
        if "부가세" not in self.rates_df.columns:
            return {
                "VAT 포함 총액": 0,
                "VAT 미포함 총액": 0,
                "VAT 포함 기관": [],
                "VAT 미포함 기관": [],
            }

        df = self.rates_df.copy()
        df["부가세"] = df["부가세"].fillna(0).astype(float)

        # 합계 컬럼이 있으면 그걸 기준으로, 없으면 월 합산
        if "합 계" in df.columns:
            df["총액"] = df["합 계"].fillna(0).astype(float)
        else:
            month_cols = [
                "1월", "2월", "3월", "4월", "5월", "6월",
                "7월", "8월", "9월", "10월", "11월", "12월"
            ]
            month_cols = [c for c in month_cols if c in df.columns]
            df["총액"] = df[month_cols].fillna(0).astype(float).sum(axis=1)

        vat_yes = df[df["부가세"] > 0]
        vat_no = df[df["부가세"] == 0]

        vat_yes_sum = int(vat_yes["총액"].sum())
        vat_no_sum = int(vat_no["총액"].sum())

        vat_yes_orgs = vat_yes["기관명"].dropna().astype(str).tolist() if "기관명" in vat_yes.columns else []
        vat_no_orgs = vat_no["기관명"].dropna().astype(str).tolist() if "기관명" in vat_no.columns else []

        return {
            "VAT 포함 총액": vat_no_sum,
            "VAT 미포함 총액": vat_yes_sum,
            "VAT 포함 기관": vat_no_orgs,
            "VAT 미포함 기관": vat_yes_orgs,
        }

    # ------------------------------------------------
    # ④ 지역별 총액
    # ------------------------------------------------
    def region_summary(self) -> pd.DataFrame:
        """
        기관명 → 지역 추출 후, 지역별 총액 집계.
        규칙: ○○시청 → ○○시, ○○군청 → ○○군, ○○구청 → ○○구
        그 외는 '기타'
        """
        if "기관명" not in self.rates_df.columns:
            return pd.DataFrame()

        df = self.rates_df.copy()

        def _region(org: str) -> str:
            if pd.isna(org):
                return "기타"
            org = str(org)
            if "시청" in org:
                return org.replace("시청", "시")
            if "군청" in org:
                return org.replace("군청", "군")
            if "구청" in org:
                return org.replace("구청", "구")
            return "기타"

        df["지역"] = df["기관명"].apply(_region)

        if "합 계" in df.columns:
            df["총액"] = df["합 계"].fillna(0).astype(float)
        else:
            month_cols = [
                "1월", "2월", "3월", "4월", "5월", "6월",
                "7월", "8월", "9월", "10월", "11월", "12월"
            ]
            month_cols = [c for c in month_cols if c in df.columns]
            df["총액"] = df[month_cols].fillna(0).astype(float).sum(axis=1)

        region_df = (
            df.groupby("지역")["총액"]
            .sum()
            .reset_index()
            .sort_values("총액", ascending=False)
        )
        region_df["총액"] = region_df["총액"].astype(int)
        return region_df

    # ------------------------------------------------
    # ⑤ 기관별 매출 TOP 3
    # ------------------------------------------------
    def top3_orgs(self) -> List[Tuple[str, int]]:
        if "기관명" not in self.rates_df.columns:
            return []

        df = self.rates_df.copy()

        if "합 계" in df.columns:
            df["총액"] = df["합 계"].fillna(0).astype(float)
        else:
            month_cols = [
                "1월", "2월", "3월", "4월", "5월", "6월",
                "7월", "8월", "9월", "10월", "11월", "12월"
            ]
            month_cols = [c for c in month_cols if c in df.columns]
            df["총액"] = df[month_cols].fillna(0).astype(float).sum(axis=1)

        grouped = (
            df.groupby("기관명")["총액"]
            .sum()
            .reset_index()
            .sort_values("총액", ascending=False)
        )

        top3 = grouped.head(3)
        return [(row["기관명"], int(row["총액"])) for _, row in top3.iterrows()]

    # ------------------------------------------------
    # ⑥ PDF 발행 유형별 집계
    # ------------------------------------------------
    def pdf_type_counts(self) -> Dict[str, int]:
        """
        - 카카오 PDF 대상: 카카오 통계에 존재하는 Settle ID 수
        - 다수기관 PDF 대상: 발송료 시트에는 있으나 카카오 통계에는 없는 Settle ID 수
        """

        if self.kakao_id_col in self.kakao_df.columns:
            kakao_ids = {
                self._clean(x)
                for x in self.kakao_df[self.kakao_id_col]
                if self._clean(x)
            }
        else:
            kakao_ids = set()

        if self.master_id_col in self.rates_df.columns:
            master_ids = {
                self._clean(x)
                for x in self.rates_df[self.master_id_col]
                if self._clean(x)
            }
        else:
            master_ids = set()

        # 카카오에만 있는 것 = 실제 카카오 PDF
        kakao_only = kakao_ids
        # 발송료에는 있으나 카카오에 없는 것 = 다수기관 PDF
        multi_only = master_ids - kakao_ids

        return {
            "카카오 PDF 대상": len(kakao_only),
            "다수기관 PDF 대상": len(multi_only),
            "전체 PDF": len(kakao_only) + len(multi_only),
        }

    # ------------------------------------------------
    # UI에서 한번에 쓰기 좋은 묶음 반환
    # ------------------------------------------------
    def build_summary_dict(self) -> Dict[str, object]:
        """
        Streamlit 화면에서 한 번에 쓰기 좋은 dict 패키지.
        """
        totals = self.total_sales()
        bills = self.bill_counts()
        vat = self.vat_summary()
        region_df = self.region_summary()
        top3 = self.top3_orgs()
        pdf_counts = self.pdf_type_counts()

        return {
            "총매출": totals,
            "발행건수": bills,
            "VAT요약": vat,
            "지역별": region_df,
            "TOP3": top3,
            "PDF집계": pdf_counts,
        }
