from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Holiday:
    name: str
    date: str
    type: str
    country: str
    region: str = ""
    religion: str = ""
    language: str = ""
    extra: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Holiday:
        known = {"name", "date", "type", "country", "region", "religion", "language"}
        return cls(
            name=data.get("name", ""),
            date=data.get("date", ""),
            type=data.get("type", ""),
            country=data.get("country", ""),
            region=data.get("region", ""),
            religion=data.get("religion", ""),
            language=data.get("language", ""),
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
