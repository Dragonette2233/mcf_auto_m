"""Common HTTP utilities for API modules.

Provides a shared requests Session with retries and a reusable
retry decorator for transient network errors.
"""

from __future__ import annotations

import time
from typing import Callable, Iterable, Type, Any

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


_SESSION: Session | None = None


def get_session(total_retries: int = 3, backoff: float = 0.3) -> Session:
    global _SESSION
    if _SESSION is None:
        session = requests.Session()
        retry = Retry(
            total=total_retries,
            backoff_factor=backoff,
            status_forcelist=(429, 500, 502, 503, 504),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        _SESSION = session
    return _SESSION


def retry_on_network(
    attempts: int = 3,
    backoff: float = 0.3,
    exceptions: Iterable[Type[BaseException]] = (
        requests.exceptions.ConnectTimeout,
        requests.exceptions.ConnectionError,
        requests.exceptions.ReadTimeout,
    ),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs):
            last_exc: BaseException | None = None
            for i in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as ex:  # type: ignore[arg-type]
                    last_exc = ex
                    # backoff with simple linear factor
                    time.sleep(backoff * i)
                except Exception:
                    # do not retry on unexpected exceptions
                    raise
            # Exhausted attempts: re-raise last network exception or return None
            if last_exc is not None:
                return None
            return None
        return wrapper
    return decorator

