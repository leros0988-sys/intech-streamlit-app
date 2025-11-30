import pandas as pd
from typing import List, Dict


class MissingFinder:
    """
    카카오 월별통계(kakao_df)와
    2025 발송료/기안자료 master_df(= rates_df 또는 drafts_df)의
    Settle ID 불일치(누락기관)를 자동 탐지하는 클래스.
    """

    def __init__(
        self,
        kakao_df: pd.DataFrame,
        master_settle_df: pd.DataFrame,
        kakao_key: str = "Settle ID",
        master_key: str = "카카오 settle id",
    ):
        self.kakao_df = kakao_df.copy()
        self.master_df = master_settle_df.copy()
        self.kakao_key = kakao_key
        self.master_key = master_key

    @staticmethod
    def _clean(value):
        """공백/NaN 제거 후 문자열화"""
        if pd.isna(value):
            return ""
        return str(value).strip()

    def extract_unique_ids(self, df: pd.DataFrame, col: str) -> List[str]:
        """특정 컬럼에서 고유한 ID 추출"""
        return sorted(
            list(
                {
                    self._clean(x)
                    for x in df.get(col, [])
                    if self._clean(x) != ""
                }
            )
        )

    # -------------------------------------------------------
    # 🔥 settlement_page.py에서 요구하는 메서드들 추가
    # -------------------------------------------------------

    def get_missing_settle_ids(self) -> List[str]:
        """
        카카오에는 있는데 발송료/기안자료에는 없는 Settle ID
        """
        kakao_ids = self.extract_unique_ids(self.kakao_df, self.kakao_key)
        master_ids = self.extract_unique_ids(self.master_df, self.master_key)
        return sorted(list(set(kakao_ids) - set(master_ids)))

    def get_extra_settle_ids(self) -> List[str]:
        """
        발송료/기안자료에는 있는데 카카오 통계에는 없는 Settle ID
        """
        kakao_ids = self.extract_unique_ids(self.kakao_df, self.kakao_key)
        master_ids = self.extract_unique_ids(self.master_df, self.master_key)
        return sorted(list(set(master_ids) - set(kakao_ids)))

    def get_missing_orgs(self) -> pd.DataFrame:
        """
        누락된 Settle ID + 기관명 정보까지 DataFrame으로 반환
        """
        missing_ids = self.get_missing_settle_ids()

        df = self.master_df.copy()
        df[self.master_key] = df[self.master_key].astype(str).str.strip()

        return df[df[self.master_key].isin(missing_ids)]

    def summary(self) -> Dict[str, int]:
        """
        누락/초과 수량 요약
        """
        return {
            "카카오 총 ID": len(self.extract_unique_ids(self.kakao_df, self.kakao_key)),
            "마스터 총 ID": len(self.extract_unique_ids(self.master_df, self.master_key)),
            "누락 ID 수": len(self.get_missing_settle_ids()),
            "초과 ID 수": len(self.get_extra_settle_ids()),
        }

    # 기존 방식 지원
    def find_missing(self) -> List[str]:
        return self.get_missing_settle_ids()

    def to_dataframe(self) -> pd.DataFrame:
        missing = self.get_missing_settle_ids()
        return pd.DataFrame({"누락된 Settle ID": missing})
