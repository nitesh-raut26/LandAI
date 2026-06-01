"""
Rate-limited, retrying async HTTP client for the ingestion layer.

Production concerns handled here so adapters don't have to:
  - **Per-host throttle**: enforces a minimum interval between requests to the
    same host (politeness / upstream usage-policy compliance).
  - **Retries**: exponential backoff with jitter on 429 / 5xx and transport
    errors, up to a configurable cap.
  - **Retry-After**: honoured when the server sends it.
  - **Identifying User-Agent**: sent on every request (mandatory for Nominatim).
"""
from __future__ import annotations

import asyncio
import random
import time
from urllib.parse import urlsplit

import httpx

from . import config
from ..metrics import METRICS

_RETRY_STATUS = {429, 500, 502, 503, 504}


class RateLimiter:
    """Per-host minimum-interval limiter (async-safe)."""

    def __init__(self) -> None:
        self._last: dict[str, float] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._guard = asyncio.Lock()

    async def _lock_for(self, host: str) -> asyncio.Lock:
        async with self._guard:
            lock = self._locks.get(host)
            if lock is None:
                lock = self._locks[host] = asyncio.Lock()
            return lock

    async def acquire(self, host: str, min_interval: float) -> None:
        lock = await self._lock_for(host)
        async with lock:
            wait = min_interval - (time.monotonic() - self._last.get(host, 0.0))
            if wait > 0:
                await asyncio.sleep(wait)
            self._last[host] = time.monotonic()


class HttpClient:
    """Thin async wrapper over httpx with throttle + retry. Usable as an async
    context manager or as a long-lived shared client."""

    def __init__(
        self,
        user_agent: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        self._ua = user_agent or config.USER_AGENT
        self._timeout = timeout if timeout is not None else config.HTTP_TIMEOUT
        self._max_retries = max_retries if max_retries is not None else config.HTTP_MAX_RETRIES
        self._limiter = RateLimiter()
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "HttpClient":
        await self._ensure()
        return self

    async def __aexit__(self, *exc) -> None:
        await self.aclose()

    async def _ensure(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self._timeout,
                headers={"User-Agent": self._ua},
                follow_redirects=True,
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _backoff_delay(self, attempt: int) -> float:
        return min((2 ** attempt) + random.random(), 30.0)

    @staticmethod
    def _retry_after(resp: httpx.Response) -> float | None:
        raw = resp.headers.get("Retry-After")
        if not raw:
            return None
        try:
            return max(0.0, float(raw))
        except ValueError:
            return None

    async def request(
        self,
        method: str,
        url: str,
        *,
        min_interval: float = 1.0,
        **kwargs,
    ) -> httpx.Response:
        client = await self._ensure()
        host = urlsplit(url).netloc
        attempt = 0
        while True:
            await self._limiter.acquire(host, min_interval)
            try:
                resp = await client.request(method, url, **kwargs)
            except (httpx.TransportError, httpx.TimeoutException):
                if attempt >= self._max_retries:
                    raise
                METRICS.incr("ingestion_http_retry")
                await asyncio.sleep(self._backoff_delay(attempt))
                attempt += 1
                continue

            if resp.status_code in _RETRY_STATUS and attempt < self._max_retries:
                METRICS.incr("ingestion_http_retry")
                delay = self._retry_after(resp)
                await asyncio.sleep(delay if delay is not None else self._backoff_delay(attempt))
                attempt += 1
                continue

            return resp

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)
