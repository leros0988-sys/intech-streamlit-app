import pandas as pd

def read_any_file(file):
    import pandas as pd

    try:
        # 스타일 무시하고 읽기 (오류 방지)
        return pd.read_excel(file, engine="openpyxl", dtype=str)
    except Exception:
        # 스타일 깨진 파일 강제 복구 모드
        return pd.read_excel(file, engine="calamine")


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
