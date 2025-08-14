from __future__ import annotations
from datetime import datetime, timezone


def to_ms(dt: datetime) -> int:
    return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
