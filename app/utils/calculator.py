import pandas as pd


def combine_uploaded(uploaded_files):
    dfs = []
    for f in uploaded_files:
        try:
            df = pd.read_excel(f)
            df["__source_file"] = f.name
            dfs.append(df)
        except Exception as e:
            raise RuntimeError(f"{f.name} 읽기 오류: {e}")

    if not dfs:
        raise RuntimeError("업로드된 파일에서 데이터를 읽지 못했습니다.")

    return pd.concat(dfs, ignore_index=True)


def summarize_settle(df: pd.DataFrame):
    # 통계자료에 반드시 있는 컬럼들 기반
    required = ["SETTLE_ID", "기관명", "발송건수", "인증건수", "금액"]
    missing = [c for c in required if c not in df.columns]

    if missing:
        raise RuntimeError(f"필수 컬럼 누락: {missing}")

    return (
        df.groupby(["SETTLE_ID", "기관명"], as_index=False)
        .agg({
            "발송건수": "sum",
            "인증건수": "sum",
            "금액": "sum"
        })
    )
