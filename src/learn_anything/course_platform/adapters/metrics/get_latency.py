import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from learn_anything.course_platform.adapters.metrics import INTEGRATION_METHOD_DURATION


def measure_latency(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start_time
        INTEGRATION_METHOD_DURATION.observe(duration)
        return result

    return wrapper
