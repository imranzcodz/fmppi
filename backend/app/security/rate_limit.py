import time
from collections import defaultdict

from app.logging import get_logger

logger = get_logger("app.security.rate_limit")

# In-memory fixed-window counters: (key, window_start) -> count
_counters: dict[tuple[str, int], int] = defaultdict(int)


def _window() -> int:
    return int(time.time() // 60)


def check_rate_limit(key: str, limit: int) -> bool:
    now = _window()
    counter_key = (key, now)
    _counters[counter_key] += 1
    allowed = _counters[counter_key] <= limit
    if not allowed:
        logger.warning("Rate limit exceeded", extra={"request_id": "system", "key": key, "limit": limit})
    return allowed
