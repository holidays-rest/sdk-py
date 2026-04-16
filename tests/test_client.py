from __future__ import annotations

import json

import httpx
import pytest

from holidays_rest import Country, Holiday, HolidaysApiError, HolidaysClient, Language
from tests.conftest import (
    COUNTRY,
    LANGUAGE,
    LOCAL_HOLIDAY,
    NATIONAL_HOLIDAY,
    MockTransport,
)


def make_client(transport: MockTransport) -> HolidaysClient:
    return HolidaysClient(
        api_key="test-key",
        httpx_client=httpx.Client(transport=transport),
    )


class TestConstructor:
    def test_empty_api_key_raises(self):
        with pytest.raises(ValueError, match="api_key"):
            HolidaysClient(api_key="")


class TestHolidays:
    def test_returns_list_of_holidays(self):
        transport = MockTransport(body=[NATIONAL_HOLIDAY, LOCAL_HOLIDAY])
        client = make_client(transport)
        result = client.holidays(country="DE", year=2026)

        assert len(result) == 2
        assert all(isinstance(h, Holiday) for h in result)

    def test_holiday_fields_parsed_correctly(self):
        transport = MockTransport(body=[NATIONAL_HOLIDAY])
        client = make_client(transport)
        h = client.holidays(country="DE", year=2026)[0]

        assert h.country_code == "DE"
        assert h.date == "2026-01-01"
        assert h.name == {"en": "New Year's Day"}
        assert h.is_national is True
        assert h.regions == []

    def test_local_holiday_regions_parsed(self):
        transport = MockTransport(body=[LOCAL_HOLIDAY])
        client = make_client(transport)
        h = client.holidays(country="DE", year=2026)[0]

        assert h.regions == ["BW", "BY", "ST"]
        assert h.is_local is True
        assert h.religion == "Christianity"

    def test_sends_country_and_year_params(self):
        transport = MockTransport(body=[NATIONAL_HOLIDAY])
        client = make_client(transport)
        client.holidays(country="DE", year=2026)

        assert transport.last_request is not None
        params = dict(transport.last_request.url.params)
        assert params["country"] == "DE"
        assert params["year"] == "2026"

    def test_list_param_joined_with_comma(self):
        transport = MockTransport(body=[])
        client = make_client(transport)
        client.holidays(country="DE", year=2026, region=["BW", "BY"])

        params = dict(transport.last_request.url.params)
        assert params["region"] == "BW,BY"

    def test_none_params_omitted(self):
        transport = MockTransport(body=[])
        client = make_client(transport)
        client.holidays(country="DE", year=2026, month=None)

        params = dict(transport.last_request.url.params)
        assert "month" not in params

    def test_empty_country_raises(self):
        transport = MockTransport(body=[])
        client = make_client(transport)
        with pytest.raises(ValueError, match="country"):
            client.holidays(country="", year=2026)

    def test_empty_year_raises(self):
        transport = MockTransport(body=[])
        client = make_client(transport)
        with pytest.raises(ValueError, match="year"):
            client.holidays(country="DE", year="")

    def test_non_2xx_raises_holidays_api_error(self):
        transport = MockTransport(
            status_code=401,
            body={"message": "Unauthorized"},
        )
        client = make_client(transport)
        with pytest.raises(HolidaysApiError) as exc_info:
            client.holidays(country="DE", year=2026)

        assert exc_info.value.status_code == 401
        assert "Unauthorized" in str(exc_info.value)

    def test_error_falls_back_to_reason_phrase_when_no_message_key(self):
        transport = MockTransport(status_code=500, body={"error": "boom"})
        client = make_client(transport)
        with pytest.raises(HolidaysApiError) as exc_info:
            client.holidays(country="DE", year=2026)

        assert exc_info.value.status_code == 500


class TestCountries:
    def test_returns_list_of_countries(self):
        transport = MockTransport(body=[COUNTRY])
        client = make_client(transport)
        result = client.countries()

        assert len(result) == 1
        assert isinstance(result[0], Country)
        assert result[0].alpha2 == "DE"
        assert len(result[0].subdivisions) == 2


class TestCountry:
    def test_returns_country(self):
        transport = MockTransport(body=COUNTRY)
        client = make_client(transport)
        result = client.country("DE")

        assert isinstance(result, Country)
        assert result.name == "Germany"

    def test_empty_code_raises(self):
        transport = MockTransport(body=COUNTRY)
        client = make_client(transport)
        with pytest.raises(ValueError, match="country_code"):
            client.country("")


class TestLanguages:
    def test_returns_list_of_languages(self):
        transport = MockTransport(body=[LANGUAGE])
        client = make_client(transport)
        result = client.languages()

        assert len(result) == 1
        assert isinstance(result[0], Language)
        assert result[0].code == "en"
