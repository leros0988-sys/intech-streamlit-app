import os
from datetime import datetime


LOG_FILE = "app/utils/login_logs.txt"


# --------------------------------------------
# 로그인 기록 저장
# --------------------------------------------
def write_log(user: str, status: str):
    """
    user: 로그인 시도한 ID
    status: SUCCESS / FAIL 등 상태
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {user} - {status}\n"

        # log 파일 폴더 없으면 만들기
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

        # append
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)

    except Exception as e:
        print("write_log error:", e)



# --------------------------------------------
# 로그인 기록 읽기
# --------------------------------------------
def load_login_logs():
    """
    login_logs.txt 전체 반환
    """
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return f.read().splitlines()
        return []
    except:
        return []
