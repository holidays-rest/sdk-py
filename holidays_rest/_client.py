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


class HolidaysClient:
    """Synchronous client for the holidays.rest API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = BASE_URL,
        timeout: float = 15.0,
        httpx_client: httpx.Client | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must not be empty")

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = httpx_client or httpx.Client(
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    # ── context manager ────────────────────────────────────────────────────

    def __enter__(self) -> HolidaysClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    # ── internal ───────────────────────────────────────────────────────────

    def _get(self, path: str, params: dict[str, str]) -> Any:
        url = self._base_url + path
        response = self._client.get(url, params=params)

        if not response.is_success:
            body = response.content
            try:
                message = response.json().get("message", response.reason_phrase)
            except Exception:
                message = response.reason_phrase
            raise HolidaysApiError(message, response.status_code, body)

        return response.json()

    # ── public API ─────────────────────────────────────────────────────────

    def holidays(
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
        """Fetch public holidays.

        Args:
            country: ISO 3166 alpha-2 code (e.g. ``"US"``).
            year: Four-digit year (e.g. ``2024``).
            month: Optional month filter (1–12).
            day: Optional day filter (1–31).
            type: ``"religious"``, ``"national"``, or ``"local"``. Accepts a list.
            religion: Religion code(s) 1–11.
            region: Region/subdivision code(s) — see :meth:`country`.
            lang: Language code(s) — see :meth:`languages`.
            response: ``"json"`` (default) | ``"xml"`` | ``"yaml"`` | ``"csv"``.
        """
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
        data = self._get("/holidays", params)
        return [Holiday.from_dict(h) for h in data]

    def countries(self) -> list[Country]:
        """Return all supported countries."""
        data = self._get("/countries", {})
        return [Country.from_dict(c) for c in data]

    def country(self, country_code: str) -> Country:
        """Return details for one country, including subdivision codes.

        Args:
            country_code: ISO 3166 alpha-2 code (e.g. ``"US"``).
        """
        if not country_code:
            raise ValueError("country_code is required")
        data = self._get(f"/country/{country_code}", {})
        return Country.from_dict(data)

    def languages(self) -> list[Language]:
        """Return all supported language codes."""
        data = self._get("/languages", {})
        return [Language.from_dict(lang) for lang in data]
