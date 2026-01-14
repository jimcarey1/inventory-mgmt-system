from datetime import datetime

def parse_iso_datetime(value: str) -> datetime|None:
    """
    Parse an ISO 8601 datetime string robustly.
    Accepts forms like "2026-01-12T10:00:00", "2026-01-12T10:00:00Z",
    and "2026-01-12T10:00:00+05:30".
    """
    if value is None:
        raise ValueError("Missing datetime")
    # allow trailing 'Z' (UTC)
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except Exception as exc:
        return None