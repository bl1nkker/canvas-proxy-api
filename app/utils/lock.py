import functools
from threading import RLock

default_lock = RLock()


def with_lock(_func=None, *, lock: RLock = None):
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            _lock = lock or default_lock
            with _lock:
                return func(*args, **kwargs)

        return _wrapper

    if _func is None:
        return _decorator
    else:
        return _decorator(_func)
