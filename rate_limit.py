"""
rate_limit.py — Per-user sliding window rate limiter.
"""

import time
from collections import defaultdict, deque
from config import RATE_LIMIT_MESSAGES, RATE_LIMIT_WINDOW

_windows: dict = defaultdict(deque)


def is_allowed(user_id: int) -> bool:
    now = time.time()
    dq = _windows[user_id]
    # Remove timestamps outside the window
    while dq and now - dq[0] > RATE_LIMIT_WINDOW:
        dq.popleft()
    if len(dq) >= RATE_LIMIT_MESSAGES:
        return False
    dq.append(now)
    return True
