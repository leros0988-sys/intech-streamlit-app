import pandas as pd
from typing import List


class MissingFinder:
    """
    카카오 월별통계(kakao_df)와
    2025 발송료/기안자료 master_df(= rates_df or drafts_df)
    사이에서 '카카오 settle id' 누락 여부를 비교하여
    정산 대상에서 빠진 기관을 자동 추출하는 클래스.
    """

    def __init__(
        self,
        kakao_df: pd.DataFrame,
        master_settle_df: pd.DataFrame,
        kakao_key: str = "Settle ID",
        master_key: str = "카카오 settle id",
    ):
        """
        kakao_df: 카카오 월별 정산 엑셀
        master_settle_df: 2025 발송료 또는 기안자료 (둘 중 카카오 settle id가 있는 시트)
        """
        self.kakao_df = kakao_df.copy()
        self.master_df = master_settle_df.copy()
        self.kakao_key = kakao_key
        self.master_key = master_key

    @staticmethod
    def _clean(value):
        """공백, NaN, 타입 정리."""
        if pd.isna(value):
            return ""
        return str(value).strip()

    def extract_unique_ids(self, df: pd.DataFrame, col: str) -> List[str]:
        """컬럼에서 고유한 ID 목록 추출"""
        return sorted(
            list(
                {
                    self._clean(x)
                    for x in df.get(col, [])
                    if self._clean(x) != ""
                }
            )
        )

    def find_missing(self) -> List[str]:
        """
        카카오 통계에는 있는데,
        마스터(발송료/기안자료)에는 없는 settle id 추출.
        """
        kakao_ids = self.extract_unique_ids(self.kakao_df, self.kakao_key)
        master_ids = self.extract_unique_ids(self.master_df, self.master_key)

        missing = sorted(list(set(kakao_ids) - set(master_ids)))
        return missing

    def to_dataframe(self) -> pd.DataFrame:
        """
        누락기관을 DataFrame 형태로 반환
        """
        missing = self.find_missing()
        df = pd.DataFrame({"누락된 Settle ID": missing})
        return df
