"""
Custom decorators.
"""
from functools import lru_cache, wraps
import json


def hashable_lru(func):
    """
    Cache 64 most recent calls to a function.

    Based on functools.lru_cache but with dict arguments allowed.

    Stack Overflow: https://stackoverflow.com/a/46590069
    """
    cache = lru_cache(maxsize=64)

    def deserialise(value):
        try:
            return json.loads(value)
        except Exception:
            return value

    def func_with_serialized_params(*args, **kwargs):
        _args = tuple([deserialise(arg) for arg in args])
        _kwargs = {k: deserialise(v) for k, v in kwargs.items()}

        return func(*_args, **_kwargs)

    cached_function = cache(func_with_serialized_params)

    @wraps(func)
    def lru_decorator(*args, **kwargs):
        _args = tuple(
            [
                json.dumps(arg, sort_keys=True) if type(arg) in (list, dict) else arg
                for arg in args
            ]
        )
        _kwargs = {
            k: json.dumps(v, sort_keys=True) if type(v) in (list, dict) else v
            for k, v in kwargs.items()
        }

        return cached_function(*_args, **_kwargs)

    lru_decorator.cache_info = cached_function.cache_info
    lru_decorator.cache_clear = cached_function.cache_clear

    return lru_decorator
