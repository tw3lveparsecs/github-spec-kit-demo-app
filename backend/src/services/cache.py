"""
LRU cache decorator for scenario caching.

This module provides a caching mechanism to improve performance
by reducing file I/O operations for frequently accessed scenarios.
"""

from functools import lru_cache, wraps
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def cached_scenario(maxsize: int = 100) -> Callable[[F], F]:
    """
    Decorator that adds LRU caching to scenario-related functions.

    This decorator wraps Python's built-in lru_cache to provide
    consistent caching behavior across the application.

    Args:
        maxsize: Maximum number of cached items. Default is 100.

    Returns:
        Decorated function with caching enabled.

    Example:
        @cached_scenario(maxsize=50)
        def get_scenario(scenario_id: str) -> Dict[str, Any]:
            # Expensive operation here
            return load_from_file(scenario_id)
    """

    def decorator(func: F) -> F:
        cached_func = lru_cache(maxsize=maxsize)(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return cached_func(*args, **kwargs)

        # Expose cache info and clear methods
        wrapper.cache_info = cached_func.cache_info  # type: ignore
        wrapper.cache_clear = cached_func.cache_clear  # type: ignore

        return wrapper  # type: ignore

    return decorator


# Pre-configured cache decorator for scenarios (100 items)
scenario_cache = cached_scenario(maxsize=100)
