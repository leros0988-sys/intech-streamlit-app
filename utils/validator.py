# utils/validator.py

import pandas as pd

def validate_uploaded_files(kakao, kt, naver):
    """
    업로드된 3개 파일(카카오, KT, 네이버) 검증.
    """

    # 1) 파일 누락 여부
    if kakao is None or kt is None or naver is None:
        return {
            "status": "error",
            "message": "❌ 카카오 / KT / 네이버 파일을 모두 업로드해주세요."
        }

    # 2) 확장자 체크
    for f in [kakao, kt, naver]:
        if not f.name.endswith(".xlsx"):
            return {
                "status": "error",
                "message": f"❌ '{f.name}' 은 xlsx 파일이 아닙니다."
            }

    # 3) 엑셀 로드 테스트
    try:
        pd.read_excel(kakao)
        pd.read_excel(kt)
        pd.read_excel(naver)
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ 엑셀 파일을 읽는 중 오류 발생: {e}"
        }

    # 성공
    return {"status": "ok", "message": "3개 파일 정상 확인되었습니다."}
