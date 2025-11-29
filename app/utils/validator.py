import pandas as pd


def read_excel_anywhere(file):
    try:
        return pd.read_excel(file)
    except Exception as e:
        raise RuntimeError(f"{file.name} 파일을 읽을 수 없습니다: {e}")


def validate_uploaded_files(uploaded_files):
    validated = {}
    for f in uploaded_files:
        df = read_excel_anywhere(f)
        validated[f.name] = df
    return validated
