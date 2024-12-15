import time
from functools import wraps

from learn_anything.course_platform.adapters.metrics import INTEGRATION_METHOD_DURATION


def measure_latency(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - start_time
        INTEGRATION_METHOD_DURATION.observe(duration)
        return result

    return wrapper
