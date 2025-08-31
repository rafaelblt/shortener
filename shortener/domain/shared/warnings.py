import warnings
import functools


def deprecated_func(reason: str, category=UserWarning):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"The function {func.__name__}() is deprecated: {reason}",
                category=category,
                stacklevel=2,
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator
