from __future__ import annotations

import json

import httpx
import pytest


# ── sample API payloads ────────────────────────────────────────────────────

NATIONAL_HOLIDAY = {
    "country_code": "DE",
    "country_name": "Germany",
    "date": "2026-01-01",
    "name": {"en": "New Year's Day"},
    "isNational": True,
    "isReligious": False,
    "isLocal": False,
    "isEstimate": False,
    "day": {"actual": "Thursday", "observed": "Thursday"},
    "religion": "",
    "regions": [],
}

LOCAL_HOLIDAY = {
    "country_code": "DE",
    "country_name": "Germany",
    "date": "2026-01-06",
    "name": {"en": "Epiphany"},
    "isNational": False,
    "isReligious": True,
    "isLocal": True,
    "isEstimate": False,
    "day": {"actual": "Tuesday", "observed": "Tuesday"},
    "religion": "Christianity",
    "regions": ["BW", "BY", "ST"],
}

COUNTRY = {
    "name": "Germany",
    "alpha2": "DE",
    "subdivisions": [
        {"code": "BW", "name": "Baden-Württemberg"},
        {"code": "BY", "name": "Bavaria"},
    ],
}

LANGUAGE = {"code": "en", "name": "English"}


# ── mock transports ────────────────────────────────────────────────────────

class MockTransport(httpx.BaseTransport):
    """Synchronous mock transport. Records the last request made."""

    def __init__(self, *, status_code: int = 200, body: object) -> None:
        self.last_request: httpx.Request | None = None
        self._status_code = status_code
        self._body = body

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.last_request = request
        content = json.dumps(self._body).encode()
        return httpx.Response(
            self._status_code,
            content=content,
            headers={"content-type": "application/json"},
        )


class AsyncMockTransport(httpx.AsyncBaseTransport):
    """Async mock transport. Records the last request made."""

    def __init__(self, *, status_code: int = 200, body: object) -> None:
        self.last_request: httpx.Request | None = None
        self._status_code = status_code
        self._body = body

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        self.last_request = request
        content = json.dumps(self._body).encode()
        return httpx.Response(
            self._status_code,
            content=content,
            headers={"content-type": "application/json"},
        )
