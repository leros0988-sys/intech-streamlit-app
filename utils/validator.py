import pandas as pd

def validate_uploaded_files(uploaded_files):
    if not uploaded_files:
        raise ValueError("업로드된 파일이 없습니다.")
    
    valid_files = {}
    for up in uploaded_files:
        if up.name.endswith(".xlsx"):
            valid_files[up.name] = pd.read_excel(up)
        else:
            raise ValueError(f"지원하지 않는 파일 형식: {up.name}")

    return valid_files

