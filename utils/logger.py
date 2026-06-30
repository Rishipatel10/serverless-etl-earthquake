import json
from datetime import datetime


def log_info(message):
    """
    Log informational messages.
    """

    print(f"[INFO] {datetime.utcnow().isoformat()} | {message}")


def log_warning(message):
    """
    Log warning messages.
    """

    print(f"[WARNING] {datetime.utcnow().isoformat()} | {message}")


def log_error(message):
    """
    Log error messages.
    """

    print(f"[ERROR] {datetime.utcnow().isoformat()} | {message}")


def log_audit(summary):
    """
    Print ETL audit summary for CloudWatch Logs.
    """

    print("\n" + "=" * 60)
    print("               ETL AUDIT SUMMARY")
    print("=" * 60)

    print(json.dumps(summary, indent=4))

    print("=" * 60)
    print(f"Audit Completed : {datetime.utcnow().isoformat()}")
    print("=" * 60 + "\n")