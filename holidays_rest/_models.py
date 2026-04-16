from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DayInfo:
    actual: str
    observed: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DayInfo:
        return cls(
            actual=data.get("actual", ""),
            observed=data.get("observed", ""),
        )


@dataclass
class Holiday:
    country_code: str
    country_name: str
    date: str
    name: dict[str, str]
    is_national: bool
    is_religious: bool
    is_local: bool
    is_estimate: bool
    day: DayInfo
    religion: str
    regions: list[str]
    extra: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Holiday:
        known = {
            "country_code", "country_name", "date", "name",
            "isNational", "isReligious", "isLocal", "isEstimate",
            "day", "religion", "regions",
        }
        raw_day = data.get("day", {})
        return cls(
            country_code=data.get("country_code", ""),
            country_name=data.get("country_name", ""),
            date=data.get("date", ""),
            name=data.get("name", {}),
            is_national=data.get("isNational", False),
            is_religious=data.get("isReligious", False),
            is_local=data.get("isLocal", False),
            is_estimate=data.get("isEstimate", False),
            day=DayInfo.from_dict(raw_day) if isinstance(raw_day, dict) else DayInfo("", ""),
            religion=data.get("religion", ""),
            regions=data.get("regions", []),
            extra={k: v for k, v in data.items() if k not in known},
        )


@dataclass
class Subdivision:
    code: str
    name: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Subdivision:
        return cls(code=data.get("code", ""), name=data.get("name", ""))


@dataclass
class Country:
    name: str
    alpha2: str
    subdivisions: list[Subdivision] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Country:
        known = {"name", "alpha2", "subdivisions"}
        return cls(
            name=data.get("name", ""),
            alpha2=data.get("alpha2", ""),
            subdivisions=[
                Subdivision.from_dict(s) for s in data.get("subdivisions", [])
            ],
            extra={k: v for k, v in data.items() if k not in known},
        )


@dataclass
class Language:
    code: str
    name: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Language:
        return cls(code=data.get("code", ""), name=data.get("name", ""))
