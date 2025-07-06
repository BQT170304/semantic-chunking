from __future__ import annotations

import time
from functools import lru_cache
from functools import wraps

from shared.logging import get_logger
from shared.settings import Settings


@lru_cache
def get_settings():
    return Settings()  # type: ignore


def profile(func):
    """Decorator to profile execution time. Using default logger with info level\n
    Output: [module.function] executed in: 0.0s
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        logger = get_logger('profiler')
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        logger.info(
            f'[{func.__module__}.{func.__name__}] executed in: {end_time - start_time}s',
        )

        if hasattr(result, 'processing_time'):
            setattr(result, 'processing_time', end_time - start_time)

        return result

    return wrapper
