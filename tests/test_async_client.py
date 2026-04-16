from __future__ import annotations

import httpx
import pytest

from holidays_rest import (
    AsyncHolidaysClient,
    Country,
    Holiday,
    HolidaysApiError,
    Language,
)
from tests.conftest import (
    COUNTRY,
    LANGUAGE,
    LOCAL_HOLIDAY,
    NATIONAL_HOLIDAY,
    AsyncMockTransport,
)


def make_client(transport: AsyncMockTransport) -> AsyncHolidaysClient:
    return AsyncHolidaysClient(
        api_key="test-key",
        httpx_client=httpx.AsyncClient(transport=transport),
    )


class TestConstructor:
    def test_empty_api_key_raises(self):
        with pytest.raises(ValueError, match="api_key"):
            AsyncHolidaysClient(api_key="")


class TestHolidays:
    async def test_returns_list_of_holidays(self):
        transport = AsyncMockTransport(body=[NATIONAL_HOLIDAY, LOCAL_HOLIDAY])
        client = make_client(transport)
        result = await client.holidays(country="DE", year=2026)

        assert len(result) == 2
        assert all(isinstance(h, Holiday) for h in result)

    async def test_holiday_fields_parsed_correctly(self):
        transport = AsyncMockTransport(body=[NATIONAL_HOLIDAY])
        client = make_client(transport)
        h = (await client.holidays(country="DE", year=2026))[0]

        assert h.country_code == "DE"
        assert h.date == "2026-01-01"
        assert h.name == {"en": "New Year's Day"}
        assert h.is_national is True
        assert h.regions == []

    async def test_local_holiday_regions_parsed(self):
        transport = AsyncMockTransport(body=[LOCAL_HOLIDAY])
        client = make_client(transport)
        h = (await client.holidays(country="DE", year=2026))[0]

        assert h.regions == ["BW", "BY", "ST"]
        assert h.is_local is True
        assert h.religion == "Christianity"

    async def test_sends_country_and_year_params(self):
        transport = AsyncMockTransport(body=[NATIONAL_HOLIDAY])
        client = make_client(transport)
        await client.holidays(country="DE", year=2026)

        assert transport.last_request is not None
        params = dict(transport.last_request.url.params)
        assert params["country"] == "DE"
        assert params["year"] == "2026"

    async def test_list_param_joined_with_comma(self):
        transport = AsyncMockTransport(body=[])
        client = make_client(transport)
        await client.holidays(country="DE", year=2026, region=["BW", "BY"])

        params = dict(transport.last_request.url.params)
        assert params["region"] == "BW,BY"

    async def test_empty_country_raises(self):
        transport = AsyncMockTransport(body=[])
        client = make_client(transport)
        with pytest.raises(ValueError, match="country"):
            await client.holidays(country="", year=2026)

    async def test_empty_year_raises(self):
        transport = AsyncMockTransport(body=[])
        client = make_client(transport)
        with pytest.raises(ValueError, match="year"):
            await client.holidays(country="DE", year="")

    async def test_non_2xx_raises_holidays_api_error(self):
        transport = AsyncMockTransport(status_code=401, body={"message": "Unauthorized"})
        client = make_client(transport)
        with pytest.raises(HolidaysApiError) as exc_info:
            await client.holidays(country="DE", year=2026)

        assert exc_info.value.status_code == 401
        assert "Unauthorized" in str(exc_info.value)


class TestCountries:
    async def test_returns_list_of_countries(self):
        transport = AsyncMockTransport(body=[COUNTRY])
        client = make_client(transport)
        result = await client.countries()

        assert len(result) == 1
        assert isinstance(result[0], Country)
        assert result[0].alpha2 == "DE"


class TestCountry:
    async def test_returns_country(self):
        transport = AsyncMockTransport(body=COUNTRY)
        client = make_client(transport)
        result = await client.country("DE")

        assert isinstance(result, Country)
        assert result.name == "Germany"

    async def test_empty_code_raises(self):
        transport = AsyncMockTransport(body=COUNTRY)
        client = make_client(transport)
        with pytest.raises(ValueError, match="country_code"):
            await client.country("")


class TestLanguages:
    async def test_returns_list_of_languages(self):
        transport = AsyncMockTransport(body=[LANGUAGE])
        client = make_client(transport)
        result = await client.languages()

        assert len(result) == 1
        assert isinstance(result[0], Language)
        assert result[0].code == "en"
