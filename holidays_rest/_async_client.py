from __future__ import annotations

from typing import Any

import httpx

from ._errors import HolidaysApiError
from ._models import Country, Holiday, Language

BASE_URL = "https://api.holidays.rest/v1"


def _build_params(**kwargs: Any) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in kwargs.items():
        if value is None:
            continue
        if isinstance(value, list):
            out[key] = ",".join(str(v) for v in value)
        else:
            out[key] = str(value)
    return out


class AsyncHolidaysClient:
    """Async client for the holidays.rest API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: float = 15.0,
        httpx_client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must not be empty")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx_client or httpx.AsyncClient(
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    # ── context manager ────────────────────────────────────────────────────

    async def __aenter__(self) -> AsyncHolidaysClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    # ── internal ───────────────────────────────────────────────────────────

    async def _get(self, path: str, params: dict[str, str]) -> Any:
        url = self._base_url + path
        response = await self._client.get(url, params=params)

        if not response.is_success:
            body = response.content
            try:
                message = response.json().get("message", response.reason_phrase)
            except Exception:
                message = response.reason_phrase
            raise HolidaysApiError(message, response.status_code, body)

        return response.json()

    # ── public API ─────────────────────────────────────────────────────────

    async def holidays(
        self,
        *,
        country: str,
        year: int | str,
        month: int | str | None = None,
        day: int | str | None = None,
        type: str | list[str] | None = None,
        religion: int | list[int] | None = None,
        region: str | list[str] | None = None,
        lang: str | list[str] | None = None,
        response: str | None = None,
    ) -> list[Holiday]:
        """Fetch public holidays. See :class:`HolidaysClient` for parameter docs."""
        if not country:
            raise ValueError("country is required")
        if not year:
            raise ValueError("year is required")

        params = _build_params(
            country=country,
            year=year,
            month=month,
            day=day,
            type=type,
            religion=religion,
            region=region,
            lang=lang,
            response=response,
        )
        data = await self._get("/holidays", params)
        return [Holiday.from_dict(h) for h in data]

    async def countries(self) -> list[Country]:
        """Return all supported countries."""
        data = await self._get("/countries", {})
        return [Country.from_dict(c) for c in data]

    async def country(self, country_code: str) -> Country:
        """Return details for one country, including subdivision codes."""
        if not country_code:
            raise ValueError("country_code is required")
        data = await self._get(f"/country/{country_code}", {})
        return Country.from_dict(data)

    async def languages(self) -> list[Language]:
        """Return all supported language codes."""
        data = await self._get("/languages", {})
        return [Language.from_dict(lang) for lang in data]
