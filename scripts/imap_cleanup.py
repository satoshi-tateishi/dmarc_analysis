import imaplib
import os
import ssl
import time
from datetime import datetime, timedelta, timezone


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw.strip())


def log(message: str) -> None:
    print(f"[imap-cleanup] {message}", flush=True)


def connect() -> imaplib.IMAP4:
    host = env("IMAP_HOST")
    port = env_int("IMAP_PORT", 993)
    username = env("IMAP_USERNAME")
    password = env("IMAP_PASSWORD")
    use_ssl = env_bool("IMAP_USE_SSL", True)

    if not host or not username or not password:
        raise RuntimeError("IMAP_HOST, IMAP_USERNAME, IMAP_PASSWORD are required")

    if use_ssl:
        client = imaplib.IMAP4_SSL(host, port, ssl_context=ssl.create_default_context())
    else:
        client = imaplib.IMAP4(host, port)

    client.login(username, password)
    return client


def purge_folder(client: imaplib.IMAP4, folder: str, retention_days: int) -> int:
    if retention_days <= 0:
        log(f"skip folder={folder}: retention_days must be > 0")
        return 0

    status, _ = client.select(f'"{folder}"')
    if status != "OK":
        log(f"skip folder={folder}: cannot select")
        return 0

    before_date = (datetime.now(timezone.utc) - timedelta(days=retention_days)).strftime("%d-%b-%Y")
    status, data = client.search(None, "BEFORE", before_date)
    if status != "OK":
        log(f"skip folder={folder}: search failed")
        return 0

    message_ids = [msg_id for msg_id in data[0].split() if msg_id]
    if not message_ids:
        log(f"folder={folder}: nothing to delete")
        return 0

    deleted = 0
    for message_id in message_ids:
        status, _ = client.store(message_id, "+FLAGS", r"(\Deleted)")
        if status == "OK":
            deleted += 1

    if deleted > 0:
        client.expunge()

    log(f"folder={folder}: deleted={deleted} retention_days={retention_days}")
    return deleted


def run_once() -> None:
    archive_root = env("IMAP_ARCHIVE_FOLDER", "DMARC/Archive")
    retention_map = {
        f"{archive_root}/Aggregate": env_int("IMAP_CLEANUP_AGGREGATE_RETENTION_DAYS", 30),
        f"{archive_root}/Forensic": env_int("IMAP_CLEANUP_FORENSIC_RETENTION_DAYS", 30),
        f"{archive_root}/SMTP-TLS": env_int("IMAP_CLEANUP_SMTP_TLS_RETENTION_DAYS", 30),
        f"{archive_root}/Invalid": env_int("IMAP_CLEANUP_INVALID_RETENTION_DAYS", 90),
    }

    client = connect()
    try:
        for folder, retention_days in retention_map.items():
            purge_folder(client, folder, retention_days)
    finally:
        try:
            client.close()
        except Exception:
            pass
        client.logout()


def main() -> None:
    enabled = env_bool("IMAP_CLEANUP_ENABLED", True)
    interval_hours = env_int("IMAP_CLEANUP_INTERVAL_HOURS", 24)

    if not enabled:
        log("cleanup disabled; sleeping")
        while True:
            time.sleep(3600)

    if interval_hours <= 0:
        raise RuntimeError("IMAP_CLEANUP_INTERVAL_HOURS must be > 0")

    interval_seconds = interval_hours * 3600
    while True:
        started_at = datetime.now(timezone.utc).isoformat()
        log(f"cleanup cycle started at {started_at}")
        try:
            run_once()
        except Exception as exc:
            log(f"cleanup failed: {exc}")
        log(f"sleeping {interval_hours} hours")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
