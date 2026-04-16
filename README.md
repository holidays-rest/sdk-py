# holidays.rest Python SDK

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/867a4c6a86084be4b71516103872c069)](https://app.codacy.com/gh/holidays-rest/sdk-py/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

Official Python SDK for the [holidays.rest](https://www.holidays.rest) API.

## Requirements

- Python 3.10+
- [`httpx`](https://www.python-httpx.org/) (only dependency)

## Installation

```bash
pip install holidays-rest
```

## Quick Start

```python
from holidays_rest import HolidaysClient

with HolidaysClient(api_key="YOUR_API_KEY") as client:
    holidays = client.holidays(country="US", year=2024)
    for h in holidays:
        print(h.date, h.name.get("en"))
```

Get an API key at [holidays.rest/dashboard](https://www.holidays.rest/dashboard).

---

## API

### `HolidaysClient` (sync)

```python
from holidays_rest import HolidaysClient

client = HolidaysClient(
    api_key="YOUR_API_KEY",   # required
    timeout=15.0,             # optional, default 15s
)
```

Supports use as a context manager (`with` statement) to close the underlying connection pool on exit.

---

### `AsyncHolidaysClient` (async)

```python
from holidays_rest import AsyncHolidaysClient

async with AsyncHolidaysClient(api_key="YOUR_API_KEY") as client:
    holidays = await client.holidays(country="US", year=2024)
```

Both clients expose identical methods — only the `async`/`await` syntax differs.

---

### `client.holidays(...)` → `list[Holiday]`

| Parameter  | Type                  | Required | Description                                      |
|------------|-----------------------|----------|--------------------------------------------------|
| `country`  | `str`                 | yes      | ISO 3166 alpha-2 code (e.g. `"US"`)              |
| `year`     | `int \| str`          | yes      | Four-digit year (e.g. `2024`)                    |
| `month`    | `int \| str`          | no       | Month filter (1–12)                              |
| `day`      | `int \| str`          | no       | Day filter (1–31)                                |
| `type`     | `str \| list[str]`    | no       | `"religious"`, `"national"`, `"local"`           |
| `religion` | `int \| list[int]`    | no       | Religion code(s) 1–11                            |
| `region`   | `str \| list[str]`    | no       | Subdivision code(s) — from `country()`           |
| `lang`     | `str \| list[str]`    | no       | Language code(s) — from `languages()`            |
| `response` | `str`                 | no       | `"json"` (default) \| `"xml"` \| `"yaml"` \| `"csv"` |

```python
# All US holidays in 2024
client.holidays(country="US", year=2024)

# National holidays only
client.holidays(country="DE", year=2024, type="national")

# Multiple types
client.holidays(country="TR", year=2024, type=["national", "religious"])

# Filter by month and day
client.holidays(country="GB", year=2024, month=12, day=25)

# Specific region
client.holidays(country="US", year=2024, region="US-CA")

# Multiple regions
client.holidays(country="US", year=2024, region=["US-CA", "US-NY"])
```

---

### `client.countries()` → `list[Country]`

```python
countries = client.countries()
for c in countries:
    print(c.alpha2, c.name)
```

---

### `client.country(country_code)` → `Country`

Returns country details including subdivision codes usable as `region` filters.

```python
us = client.country("US")
for s in us.subdivisions:
    print(s.code, s.name)
```

---

### `client.languages()` → `list[Language]`

```python
langs = client.languages()
```

---

## Models

All responses are deserialized into dataclasses.

```python
@dataclass
class Holiday:
    country_code: str          # e.g. "DE"
    country_name: str          # e.g. "Germany"
    date: str                  # "YYYY-MM-DD"
    name: dict[str, str]       # {"en": "New Year's Day", "de": "Neujahr", ...}
    is_national: bool
    is_religious: bool
    is_local: bool
    is_estimate: bool          # True when the date is algorithmically estimated
    day: DayInfo               # day-of-week, actual vs observed
    religion: str              # e.g. "Christianity", empty string if not applicable
    regions: list[str]         # subdivision codes, e.g. ["BW", "BY"]

@dataclass
class DayInfo:
    actual: str                # day the holiday falls on, e.g. "Thursday"
    observed: str              # day it is observed (may differ for weekend holidays)

@dataclass
class Country:
    name: str
    alpha2: str
    subdivisions: list[Subdivision]

@dataclass
class Subdivision:
    code: str
    name: str

@dataclass
class Language:
    code: str
    name: str
```

---

## Error Handling

Non-2xx responses raise `HolidaysApiError`:

```python
from holidays_rest import HolidaysClient, HolidaysApiError

with HolidaysClient(api_key="YOUR_API_KEY") as client:
    try:
        holidays = client.holidays(country="US", year=2024)
    except HolidaysApiError as e:
        print(e.status_code)  # HTTP status code
        print(str(e))         # Error message
        print(e.body)         # Raw response bytes
```

| Status | Meaning             |
|--------|---------------------|
| 400    | Bad request         |
| 401    | Invalid API key     |
| 404    | Not found           |
| 500    | Server error        |
| 503    | Service unavailable |

---

## License

MIT
