import datetime
import json

LOG_FILE = Path("login_logs.csv")


def log_login_event(username: str, status: str):
    """
    status: "success" / "failed"
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                dt.datetime.now().isoformat(timespec="seconds"),
                username,
                status,
            ]
        )


def log_logout_event(username: str, reason: str):
    """
    reason: "manual" / "auto_logout" / "system"
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                dt.datetime.now().isoformat(timespec="seconds"),
                username,
                f"logout:{reason}",
            ]
        )


def load_login_logs():
    if not LOG_FILE.exists():
        return pd.DataFrame(columns=["time", "username", "status"])
    try:
        df = pd.read_csv(
            LOG_FILE,
            header=None,
            names=["time", "username", "status"],
            encoding="utf-8",
        )
        return df
    except Exception:
        return pd.DataFrame(columns=["time", "username", "status"])
