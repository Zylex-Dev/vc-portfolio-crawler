from __future__ import annotations

import threading
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_USER_AGENT = "sequoia-companies-crawler/1.0 (research; +https://sequoiacap.com)"
DEFAULT_TIMEOUT = 30


def build_session(
    user_agent: str = DEFAULT_USER_AGENT,
    total_retries: int = 4,
    backoff_factor: float = 0.5,
) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    retry = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class PoliteClient:
    """Wraps a Session and enforces a minimum spacing between request starts.

    Thread-safe: the spacing gate is guarded by a lock so a shared client can be
    used from a thread pool while still rate-limiting overall request starts.
    """

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        delay: float = 0.2,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.session = session or build_session()
        self.delay = delay
        self.timeout = timeout
        self._lock = threading.Lock()
        self._next_allowed = 0.0

    def _throttle(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self._next_allowed - now
            if wait > 0:
                time.sleep(wait)
                now = time.monotonic()
            self._next_allowed = now + self.delay

    def get(self, url: str, **kwargs) -> requests.Response:
        if self.delay:
            self._throttle()
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.get(url, **kwargs)
        resp.raise_for_status()
        return resp
