import pandas as pd

def read_any_file(file):
    if file.name.endswith(".csv"):
        return pd.read_csv(file)

    # 여러 시트 자동 병합
    excel = pd.ExcelFile(file)
    dfs = []

    for sheet in excel.sheet_names:
        try:
            df = excel.parse(sheet)
            df["__sheet__"] = sheet
            dfs.append(df)
        except:
            pass

    if not dfs:
        raise ValueError("시트에서 읽을 수 있는 데이터가 없음")

    return pd.concat(dfs, ignore_index=True)
