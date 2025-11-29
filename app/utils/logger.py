def load_login_logs(path="login_logs.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except:
        return []
