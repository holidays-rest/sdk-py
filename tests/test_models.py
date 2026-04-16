from __future__ import annotations

import pytest

from holidays_rest import Country, DayInfo, Holiday, Language, Subdivision
from tests.conftest import LOCAL_HOLIDAY, NATIONAL_HOLIDAY


class TestDayInfo:
    def test_from_dict_full(self):
        day = DayInfo.from_dict({"actual": "Thursday", "observed": "Friday"})
        assert day.actual == "Thursday"
        assert day.observed == "Friday"

    def test_from_dict_missing_keys(self):
        day = DayInfo.from_dict({})
        assert day.actual == ""
        assert day.observed == ""

    def test_from_dict_partial(self):
        day = DayInfo.from_dict({"actual": "Monday"})
        assert day.actual == "Monday"
        assert day.observed == ""


class TestHoliday:
    def test_national_holiday(self):
        h = Holiday.from_dict(NATIONAL_HOLIDAY)

        assert h.country_code == "DE"
        assert h.country_name == "Germany"
        assert h.date == "2026-01-01"
        assert h.name == {"en": "New Year's Day"}
        assert h.is_national is True
        assert h.is_religious is False
        assert h.is_local is False
        assert h.is_estimate is False
        assert h.day.actual == "Thursday"
        assert h.day.observed == "Thursday"
        assert h.religion == ""
        assert h.regions == []

    def test_local_religious_holiday(self):
        h = Holiday.from_dict(LOCAL_HOLIDAY)

        assert h.country_code == "DE"
        assert h.name == {"en": "Epiphany"}
        assert h.is_national is False
        assert h.is_religious is True
        assert h.is_local is True
        assert h.religion == "Christianity"
        assert h.regions == ["BW", "BY", "ST"]
        assert h.day.actual == "Tuesday"

    def test_multilingual_name(self):
        data = {**NATIONAL_HOLIDAY, "name": {"en": "New Year's Day", "de": "Neujahr"}}
        h = Holiday.from_dict(data)
        assert h.name["en"] == "New Year's Day"
        assert h.name["de"] == "Neujahr"

    def test_is_estimate_flag(self):
        data = {**NATIONAL_HOLIDAY, "isEstimate": True}
        h = Holiday.from_dict(data)
        assert h.is_estimate is True

    def test_unknown_fields_go_to_extra(self):
        data = {**NATIONAL_HOLIDAY, "future_field": "some_value"}
        h = Holiday.from_dict(data)
        assert h.extra == {"future_field": "some_value"}

    def test_known_fields_not_in_extra(self):
        h = Holiday.from_dict(NATIONAL_HOLIDAY)
        assert h.extra == {}

    def test_missing_day_field(self):
        data = {k: v for k, v in NATIONAL_HOLIDAY.items() if k != "day"}
        h = Holiday.from_dict(data)
        assert h.day.actual == ""
        assert h.day.observed == ""

    def test_defaults_for_missing_fields(self):
        h = Holiday.from_dict({})
        assert h.country_code == ""
        assert h.country_name == ""
        assert h.date == ""
        assert h.name == {}
        assert h.is_national is False
        assert h.is_religious is False
        assert h.is_local is False
        assert h.is_estimate is False
        assert h.religion == ""
        assert h.regions == []


class TestSubdivision:
    def test_from_dict(self):
        s = Subdivision.from_dict({"code": "BW", "name": "Baden-Württemberg"})
        assert s.code == "BW"
        assert s.name == "Baden-Württemberg"

    def test_from_dict_missing_keys(self):
        s = Subdivision.from_dict({})
        assert s.code == ""
        assert s.name == ""


class TestCountry:
    def test_from_dict_with_subdivisions(self):
        data = {
            "name": "Germany",
            "alpha2": "DE",
            "subdivisions": [
                {"code": "BW", "name": "Baden-Württemberg"},
                {"code": "BY", "name": "Bavaria"},
            ],
        }
        c = Country.from_dict(data)
        assert c.name == "Germany"
        assert c.alpha2 == "DE"
        assert len(c.subdivisions) == 2
        assert c.subdivisions[0].code == "BW"
        assert c.subdivisions[1].code == "BY"

    def test_from_dict_no_subdivisions(self):
        c = Country.from_dict({"name": "Germany", "alpha2": "DE"})
        assert c.subdivisions == []

    def test_unknown_fields_go_to_extra(self):
        data = {"name": "Germany", "alpha2": "DE", "subdivisions": [], "future_field": 42}
        c = Country.from_dict(data)
        assert c.extra == {"future_field": 42}

    def test_known_fields_not_in_extra(self):
        c = Country.from_dict({"name": "Germany", "alpha2": "DE", "subdivisions": []})
        assert c.extra == {}


class TestLanguage:
    def test_from_dict(self):
        lang = Language.from_dict({"code": "en", "name": "English"})
        assert lang.code == "en"
        assert lang.name == "English"

    def test_from_dict_missing_keys(self):
        lang = Language.from_dict({})
        assert lang.code == ""
        assert lang.name == ""
