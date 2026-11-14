from datetime import UTC, datetime


def utcnow():
    """Huidige UTC-tijd als naive datetime (kolommen zijn timezone-naive)."""
    return datetime.now(UTC).replace(tzinfo=None)
