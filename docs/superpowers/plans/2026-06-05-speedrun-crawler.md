# a16z Speedrun Crawler — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `a16z-speedrun` as a new fund that crawls ~240 portfolio companies from all cohorts (SR001–SR006) via the public Speedrun REST API.

**Architecture:** A two-step crawl: (1) fetch `speedrun.a16z.com/companies/` and extract the cohort list from embedded `__NEXT_DATA__` JSON; (2) for each cohort paginate `speedrun-be.a16z.com/api/companies/companies/?cohort=SRxxx` until `next` is `null`. No detail-page requests needed — all data is in the list API response. Follows the existing `crawlers/{fund}/` pattern exactly.

**Tech Stack:** Python 3.10+, `requests` (via existing `PoliteClient`), `re` + `json` (stdlib). Testing: `pytest`, fixture files (HTML + JSON).

---

## File Map

**Create:**
- `vc_crawler/crawlers/a16z_speedrun/__init__.py` — empty package marker
- `vc_crawler/crawlers/a16z_speedrun/parser.py` — cohort discovery + API pagination
- `vc_crawler/crawlers/a16z_speedrun/normalizer.py` — raw API dict → `Company`
- `vc_crawler/crawlers/a16z_speedrun/crawler.py` — `SpeedrunCrawler(BaseCrawler)`
- `tests/fixtures/speedrun_portfolio.html` — HTML with `__NEXT_DATA__` (SR001, SR002)
- `tests/fixtures/speedrun_api_sr001.json` — SR001: 2 companies, `next=null`
- `tests/fixtures/speedrun_api_sr002_p1.json` — SR002 page 1: 1 company, `next=<url>`
- `tests/fixtures/speedrun_api_sr002_p2.json` — SR002 page 2: 1 company, `next=null`
- `tests/test_speedrun_parser.py`
- `tests/test_speedrun_normalizer.py`
- `tests/test_speedrun_crawler.py`

**Modify:**
- `vc_crawler/__main__.py` — add `"a16z-speedrun"` to `_FUND_REGISTRY`
- `tests/test_vc_main.py` — add CLI integration test for `a16z-speedrun`

---

## Task 1: Create test fixtures

**Files:**
- Create: `tests/fixtures/speedrun_portfolio.html`
- Create: `tests/fixtures/speedrun_api_sr001.json`
- Create: `tests/fixtures/speedrun_api_sr002_p1.json`
- Create: `tests/fixtures/speedrun_api_sr002_p2.json`

- [ ] **Step 1: Create `tests/fixtures/speedrun_portfolio.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head><title>Speedrun - Companies</title></head>
<body>
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "cohorts": [{"name": "SR001"}, {"name": "SR002"}],
      "defaultCohort": "SR002"
    }
  },
  "page": "/companies",
  "query": {}
}
</script>
</body>
</html>
```

- [ ] **Step 2: Create `tests/fixtures/speedrun_api_sr001.json`**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "aaaa-1111",
      "slug": "cantor",
      "name": "Cantor",
      "cover_image": null,
      "company_list_image": null,
      "logo": "https://cdn.example.com/cantor.png",
      "demo_day_video_url": null,
      "cohort": "SR001",
      "preamble": "AI for real estate (short pitch)",
      "description": "Cantor builds AI tools for commercial real estate.",
      "industries": ["AI", "Real Estate / Prop Tech"],
      "founded_year": 2023,
      "team_size": 3,
      "country": "United States of America",
      "region": "America/Canada",
      "state": "California",
      "city": "San Francisco",
      "website_url": "https://cantoreality.com",
      "github_url": "",
      "x_url": "",
      "linkedin_url": "",
      "founder_set": [
        {
          "id": "f1",
          "first_name": "Alice",
          "last_name": "Smith",
          "slug": "alice-smith",
          "title": "CEO",
          "introduction": "Experienced founder.",
          "linkedin_url": "https://linkedin.com/in/alice",
          "profile_pic": null
        }
      ],
      "galleryitem_set": [],
      "show_last": false
    },
    {
      "id": "bbbb-2222",
      "slug": "orbit",
      "name": "Orbit",
      "cover_image": null,
      "company_list_image": null,
      "logo": null,
      "demo_day_video_url": null,
      "cohort": "SR001",
      "preamble": "Community platform pitch",
      "description": "Community platform for developers.",
      "industries": ["Dev Tools & DevOps"],
      "founded_year": 2022,
      "team_size": 5,
      "country": "United States of America",
      "region": "America/Canada",
      "state": "New York",
      "city": "New York",
      "website_url": "https://orbit.love",
      "github_url": "",
      "x_url": "",
      "linkedin_url": "",
      "founder_set": [],
      "galleryitem_set": [],
      "show_last": false
    }
  ]
}
```

- [ ] **Step 3: Create `tests/fixtures/speedrun_api_sr002_p1.json`**

```json
{
  "count": 2,
  "next": "https://speedrun-be.a16z.com/api/companies/companies/?cohort=SR002&limit=50&offset=1&ordering=name",
  "previous": null,
  "results": [
    {
      "id": "cccc-3333",
      "slug": "apex",
      "name": "Apex",
      "cover_image": null,
      "company_list_image": null,
      "logo": "https://cdn.example.com/apex.png",
      "demo_day_video_url": null,
      "cohort": "SR002",
      "preamble": "Gaming analytics",
      "description": "Apex provides real-time analytics for game studios.",
      "industries": ["Gaming", "AI"],
      "founded_year": 2023,
      "team_size": 4,
      "country": "United States of America",
      "region": "America/Canada",
      "state": "California",
      "city": "Los Angeles",
      "website_url": "https://apex.gg",
      "github_url": "",
      "x_url": "",
      "linkedin_url": "",
      "founder_set": [
        {
          "id": "f2",
          "first_name": "Bob",
          "last_name": "Jones",
          "slug": "bob-jones",
          "title": "Founder",
          "introduction": "Game developer.",
          "linkedin_url": "",
          "profile_pic": null
        },
        {
          "id": "f3",
          "first_name": "Carol",
          "last_name": "Lee",
          "slug": "carol-lee",
          "title": "CTO",
          "introduction": "ML engineer.",
          "linkedin_url": "",
          "profile_pic": null
        }
      ],
      "galleryitem_set": [],
      "show_last": false
    }
  ]
}
```

- [ ] **Step 4: Create `tests/fixtures/speedrun_api_sr002_p2.json`**

```json
{
  "count": 2,
  "next": null,
  "previous": "https://speedrun-be.a16z.com/api/companies/companies/?cohort=SR002&limit=50&ordering=name",
  "results": [
    {
      "id": "dddd-4444",
      "slug": "bolt",
      "name": "Bolt",
      "cover_image": null,
      "company_list_image": null,
      "logo": null,
      "demo_day_video_url": null,
      "cohort": "SR002",
      "preamble": "Fintech for SMBs",
      "description": "Bolt simplifies payments for small businesses.",
      "industries": ["Fintech"],
      "founded_year": null,
      "team_size": 2,
      "country": "United States of America",
      "region": "America/Canada",
      "state": "Texas",
      "city": "Austin",
      "website_url": "",
      "github_url": "",
      "x_url": "",
      "linkedin_url": "",
      "founder_set": [],
      "galleryitem_set": [],
      "show_last": false
    }
  ]
}
```

- [ ] **Step 5: Verify fixtures are valid JSON / HTML**

```bash
python3 -c "
import json, pathlib
for name in ['speedrun_api_sr001.json','speedrun_api_sr002_p1.json','speedrun_api_sr002_p2.json']:
    d = json.loads(pathlib.Path(f'tests/fixtures/{name}').read_text())
    print(name, '->', d['count'], 'total,', len(d['results']), 'in page')
print('speedrun_portfolio.html ->', 'OK')
import re
html = pathlib.Path('tests/fixtures/speedrun_portfolio.html').read_text()
m = re.search(r'<script id=\"__NEXT_DATA__\" type=\"application/json\">(.*?)</script>', html, re.DOTALL)
d = json.loads(m.group(1))
print('cohorts:', [c['name'] for c in d['props']['pageProps']['cohorts']])
"
```

Expected output:
```
speedrun_api_sr001.json -> 2 total, 2 in page
speedrun_api_sr002_p1.json -> 2 total, 1 in page
speedrun_api_sr002_p2.json -> 2 total, 1 in page
speedrun_portfolio.html -> OK
cohorts: ['SR001', 'SR002']
```

---

## Task 2: `parser.py` — cohort discovery (`parse_portfolio_page`)

**Files:**
- Create: `vc_crawler/crawlers/a16z_speedrun/__init__.py`
- Create: `vc_crawler/crawlers/a16z_speedrun/parser.py`
- Create: `tests/test_speedrun_parser.py`

- [ ] **Step 1: Create empty `__init__.py`**

Create `vc_crawler/crawlers/a16z_speedrun/__init__.py` with empty content.

- [ ] **Step 2: Write failing tests for `parse_portfolio_page`**

Create `tests/test_speedrun_parser.py`:

```python
from pathlib import Path
import pytest
from vc_crawler.crawlers.a16z_speedrun.parser import (
    parse_portfolio_page,
    PORTFOLIO_URL,
)

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "speedrun_portfolio.html"


def test_returns_cohort_list():
    cohorts = parse_portfolio_page(FIXTURE_HTML.read_text(encoding="utf-8"))
    assert cohorts == ["SR001", "SR002"]


def test_returns_list_of_strings():
    cohorts = parse_portfolio_page(FIXTURE_HTML.read_text(encoding="utf-8"))
    assert all(isinstance(c, str) for c in cohorts)


def test_raises_on_missing_next_data():
    with pytest.raises(ValueError, match="__NEXT_DATA__"):
        parse_portfolio_page("<html><body>nothing</body></html>")


def test_raises_on_missing_cohorts_key():
    html = """<html><body>
    <script id="__NEXT_DATA__" type="application/json">
    {"props":{"pageProps":{}}}
    </script></body></html>"""
    with pytest.raises(ValueError, match="cohorts"):
        parse_portfolio_page(html)


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://speedrun.a16z.com/companies/"
```

- [ ] **Step 3: Run tests — verify they fail**

```bash
.venv/bin/python -m pytest tests/test_speedrun_parser.py -v 2>&1 | head -20
```

Expected: `ERROR` or `ModuleNotFoundError` — module does not exist yet.

- [ ] **Step 4: Implement `parse_portfolio_page` in `parser.py`**

Create `vc_crawler/crawlers/a16z_speedrun/parser.py`:

```python
from __future__ import annotations

import json
import re

PORTFOLIO_URL = "https://speedrun.a16z.com/companies/"
API_BASE = "https://speedrun-be.a16z.com/api/companies/companies/"

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def parse_portfolio_page(html: str) -> list[str]:
    """Return ordered list of cohort names from the portfolio page __NEXT_DATA__."""
    m = _NEXT_DATA_RE.search(html)
    if not m:
        raise ValueError(
            "Could not find __NEXT_DATA__ script tag in the speedrun portfolio page. "
            "The page structure may have changed."
        )
    data = json.loads(m.group(1))
    try:
        cohorts = data["props"]["pageProps"]["cohorts"]
    except KeyError as exc:
        raise ValueError(
            f"Expected props.pageProps.cohorts in __NEXT_DATA__ but key {exc} was missing."
        ) from exc
    return [c["name"] for c in cohorts]
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
.venv/bin/python -m pytest tests/test_speedrun_parser.py -v
```

Expected: all 5 tests `PASSED`.

---

## Task 3: `parser.py` — API pagination (`fetch_cohort_companies`)

**Files:**
- Modify: `vc_crawler/crawlers/a16z_speedrun/parser.py`
- Modify: `tests/test_speedrun_parser.py`

- [ ] **Step 1: Append pagination tests to `tests/test_speedrun_parser.py`**

Add `import json` at the top of the file (after existing imports), then append the following at the end of the file:

```python
# new fixture paths (append after existing FIXTURE_HTML)
import json

FIXTURE_SR001 = Path(__file__).parent / "fixtures" / "speedrun_api_sr001.json"
FIXTURE_SR002_P1 = Path(__file__).parent / "fixtures" / "speedrun_api_sr002_p1.json"
FIXTURE_SR002_P2 = Path(__file__).parent / "fixtures" / "speedrun_api_sr002_p2.json"


class _FakeResp:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class _FakeClient:
    def __init__(self, responses: dict):
        # keys are URL substrings; first match wins
        self._responses = responses
        self.calls: list[str] = []

    def get(self, url, **kw):
        self.calls.append(url)
        for key, val in self._responses.items():
            if key in url:
                return _FakeResp(val)
        raise KeyError(f"No fixture for URL: {url}")


# --- new test functions ---

def test_fetch_cohort_returns_all_records_single_page():
    from vc_crawler.crawlers.a16z_speedrun.parser import fetch_cohort_companies
    client = _FakeClient({"cohort=SR001": json.loads(FIXTURE_SR001.read_text())})
    results = fetch_cohort_companies(client, "SR001")
    assert len(results) == 2


def test_fetch_cohort_paginates_until_next_is_null():
    from vc_crawler.crawlers.a16z_speedrun.parser import fetch_cohort_companies
    client = _FakeClient({
        "offset=1": json.loads(FIXTURE_SR002_P2.read_text()),
        "cohort=SR002": json.loads(FIXTURE_SR002_P1.read_text()),
    })
    results = fetch_cohort_companies(client, "SR002")
    assert len(results) == 2


def test_fetch_cohort_returns_raw_dicts():
    from vc_crawler.crawlers.a16z_speedrun.parser import fetch_cohort_companies
    client = _FakeClient({"cohort=SR001": json.loads(FIXTURE_SR001.read_text())})
    results = fetch_cohort_companies(client, "SR001")
    assert isinstance(results[0], dict)
    assert "name" in results[0]


def test_fetch_cohort_makes_at_least_one_request():
    from vc_crawler.crawlers.a16z_speedrun.parser import fetch_cohort_companies
    client = _FakeClient({"cohort=SR001": json.loads(FIXTURE_SR001.read_text())})
    fetch_cohort_companies(client, "SR001")
    assert len(client.calls) >= 1


def test_fetch_cohort_first_url_contains_cohort_param():
    from vc_crawler.crawlers.a16z_speedrun.parser import fetch_cohort_companies
    client = _FakeClient({"cohort=SR001": json.loads(FIXTURE_SR001.read_text())})
    fetch_cohort_companies(client, "SR001")
    assert "cohort=SR001" in client.calls[0]
```

**Important:** The `_FakeClient` and `_FakeResp` classes defined here replace the original test-only imports at the top of the file. Add the new imports and classes/tests below the existing tests (do not rewrite the entire file).

- [ ] **Step 2: Run new tests — verify they fail**

```bash
.venv/bin/python -m pytest tests/test_speedrun_parser.py::test_fetch_cohort_returns_all_records_single_page -v
```

Expected: `ImportError` — `fetch_cohort_companies` not defined yet.

- [ ] **Step 3: Append `fetch_cohort_companies` to `parser.py`**

Add to the bottom of `vc_crawler/crawlers/a16z_speedrun/parser.py`:

```python
def fetch_cohort_companies(client, cohort: str) -> list[dict]:
    """Fetch all companies for a cohort, following pagination until next is null."""
    results: list[dict] = []
    url: str | None = f"{API_BASE}?cohort={cohort}&limit=50&ordering=name"
    while url:
        resp = client.get(url)
        page = resp.json()
        results.extend(page["results"])
        url = page.get("next")
    return results
```

- [ ] **Step 4: Run all parser tests — verify they pass**

```bash
.venv/bin/python -m pytest tests/test_speedrun_parser.py -v
```

Expected: all tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/a16z_speedrun/__init__.py \
        vc_crawler/crawlers/a16z_speedrun/parser.py \
        tests/fixtures/speedrun_portfolio.html \
        tests/fixtures/speedrun_api_sr001.json \
        tests/fixtures/speedrun_api_sr002_p1.json \
        tests/fixtures/speedrun_api_sr002_p2.json \
        tests/test_speedrun_parser.py
git commit -m "feat(speedrun): add parser — cohort discovery and API pagination"
```

---

## Task 4: `normalizer.py` — raw dict → `Company`

**Files:**
- Create: `vc_crawler/crawlers/a16z_speedrun/normalizer.py`
- Create: `tests/test_speedrun_normalizer.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_speedrun_normalizer.py`:

```python
import pytest
from vc_crawler.crawlers.a16z_speedrun.normalizer import normalize
from vc_crawler.models import Company


def _cantor():
    return {
        "id": "aaaa-1111",
        "slug": "cantor",
        "name": "Cantor",
        "logo": "https://cdn.example.com/cantor.png",
        "cohort": "SR001",
        "preamble": "AI for real estate (short pitch)",
        "description": "Cantor builds AI tools for commercial real estate.",
        "industries": ["AI", "Real Estate / Prop Tech"],
        "founded_year": 2023,
        "website_url": "https://cantoreality.com",
        "founder_set": [
            {"first_name": "Alice", "last_name": "Smith",
             "slug": "alice-smith", "title": "CEO",
             "introduction": "", "linkedin_url": "", "profile_pic": None},
        ],
    }


def _orbit():
    return {
        "id": "bbbb-2222",
        "slug": "orbit",
        "name": "Orbit",
        "logo": None,
        "cohort": "SR001",
        "preamble": "",
        "description": "Community platform for developers.",
        "industries": ["Dev Tools & DevOps"],
        "founded_year": None,
        "website_url": "",
        "founder_set": [],
    }


def _bolt():
    return {
        "id": "dddd-4444",
        "slug": "bolt",
        "name": "Bolt",
        "logo": None,
        "cohort": "SR002",
        "preamble": "Fintech",
        "description": None,
        "industries": [],
        "founded_year": None,
        "website_url": None,
        "founder_set": [],
    }


def test_returns_company_instance():
    assert isinstance(normalize(_cantor(), 1), Company)


def test_fund_is_a16z_speedrun():
    assert normalize(_cantor(), 1).fund == "a16z-speedrun"


def test_id_assigned():
    assert normalize(_cantor(), 42).id == 42


def test_name():
    assert normalize(_cantor(), 1).name == "Cantor"


def test_slug_from_api():
    assert normalize(_cantor(), 1).slug == "cantor"


def test_fund_url():
    assert normalize(_cantor(), 1).fund_url == "https://speedrun.a16z.com/companies/cantor"


def test_sectors():
    c = normalize(_cantor(), 1)
    assert c.sectors == ["AI", "Real Estate / Prop Tech"]


def test_sectors_empty_list_when_no_industries():
    assert normalize(_bolt(), 1).sectors == []


def test_website():
    assert normalize(_cantor(), 1).website == "https://cantoreality.com"


def test_website_none_when_empty_string():
    assert normalize(_orbit(), 1).website is None


def test_website_none_when_null():
    assert normalize(_bolt(), 1).website is None


def test_description():
    assert normalize(_cantor(), 1).description == "Cantor builds AI tools for commercial real estate."


def test_description_none_when_null():
    assert normalize(_bolt(), 1).description is None


def test_stage_is_cohort():
    assert normalize(_cantor(), 1).stage == "SR001"


def test_stage_is_cohort_sr002():
    assert normalize(_bolt(), 1).stage == "SR002"


def test_stage_year_is_none():
    assert normalize(_cantor(), 1).stage_year is None


def test_founded_year():
    assert normalize(_cantor(), 1).founded_year == 2023


def test_founded_year_none():
    assert normalize(_orbit(), 1).founded_year is None


def test_invested_year_is_none():
    assert normalize(_cantor(), 1).invested_year is None


def test_logo_url():
    assert normalize(_cantor(), 1).logo_url == "https://cdn.example.com/cantor.png"


def test_logo_url_none():
    assert normalize(_orbit(), 1).logo_url is None


def test_ticker_symbol_none():
    assert normalize(_cantor(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_cantor(), 1).acquirer is None


def test_founders_joined():
    assert normalize(_cantor(), 1).founders == ["Alice Smith"]


def test_founders_multiple():
    raw = _cantor()
    raw["founder_set"] = [
        {"first_name": "Bob", "last_name": "Jones", "slug": "", "title": "", "introduction": "", "linkedin_url": "", "profile_pic": None},
        {"first_name": "Carol", "last_name": "Lee", "slug": "", "title": "", "introduction": "", "linkedin_url": "", "profile_pic": None},
    ]
    assert normalize(raw, 1).founders == ["Bob Jones", "Carol Lee"]


def test_founders_empty_becomes_none():
    assert normalize(_orbit(), 1).founders is None
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
.venv/bin/python -m pytest tests/test_speedrun_normalizer.py -v 2>&1 | head -10
```

Expected: `ImportError` — module not found.

- [ ] **Step 3: Implement `normalizer.py`**

Create `vc_crawler/crawlers/a16z_speedrun/normalizer.py`:

```python
from __future__ import annotations

from typing import Optional

from vc_crawler.models import Company

FUND_URL_BASE = "https://speedrun.a16z.com/companies/"


def _founders(founder_set: list[dict]) -> Optional[list[str]]:
    names = [
        f"{f['first_name']} {f['last_name']}".strip()
        for f in founder_set
    ]
    return names if names else None


def normalize(raw: dict, company_id: int) -> Company:
    slug = raw["slug"]
    return Company(
        id=company_id,
        fund="a16z-speedrun",
        name=raw["name"],
        slug=slug,
        fund_url=f"{FUND_URL_BASE}{slug}",
        sectors=raw.get("industries") or [],
        website=raw.get("website_url") or None,
        description=raw.get("description") or None,
        stage=raw.get("cohort") or None,
        stage_year=None,
        founded_year=raw.get("founded_year"),
        invested_year=None,
        logo_url=raw.get("logo") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=_founders(raw.get("founder_set") or []),
    )
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
.venv/bin/python -m pytest tests/test_speedrun_normalizer.py -v
```

Expected: all tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/a16z_speedrun/normalizer.py \
        tests/test_speedrun_normalizer.py
git commit -m "feat(speedrun): add normalizer — map API dict to Company"
```

---

## Task 5: `crawler.py` — `SpeedrunCrawler`

**Files:**
- Create: `vc_crawler/crawlers/a16z_speedrun/crawler.py`
- Create: `tests/test_speedrun_crawler.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_speedrun_crawler.py`:

```python
import json
from pathlib import Path
from vc_crawler.crawlers.a16z_speedrun.crawler import SpeedrunCrawler
from vc_crawler.models import Company

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "speedrun_portfolio.html"
FIXTURE_SR001 = Path(__file__).parent / "fixtures" / "speedrun_api_sr001.json"
FIXTURE_SR002_P1 = Path(__file__).parent / "fixtures" / "speedrun_api_sr002_p1.json"
FIXTURE_SR002_P2 = Path(__file__).parent / "fixtures" / "speedrun_api_sr002_p2.json"


class _FakeResp:
    def __init__(self, data):
        self._data = data

    @property
    def text(self):
        return self._data if isinstance(self._data, str) else json.dumps(self._data)

    def json(self):
        return self._data if isinstance(self._data, dict) else json.loads(self._data)


class _FakeClient:
    def __init__(self, responses: dict):
        self._responses = responses
        self.calls: list[str] = []

    def get(self, url, **kw):
        self.calls.append(url)
        for key, val in self._responses.items():
            if key in url:
                return _FakeResp(val)
        raise KeyError(f"No fixture for URL: {url}")


def _make_client():
    return _FakeClient({
        "speedrun.a16z.com/companies": FIXTURE_HTML.read_text(encoding="utf-8"),
        "offset=1": json.loads(FIXTURE_SR002_P2.read_text()),
        "cohort=SR001": json.loads(FIXTURE_SR001.read_text()),
        "cohort=SR002": json.loads(FIXTURE_SR002_P1.read_text()),
    })


def test_returns_list_of_companies():
    companies = SpeedrunCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    companies = SpeedrunCrawler(_make_client()).run()
    assert len(companies) == 4


def test_sequential_ids():
    companies = SpeedrunCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3, 4]


def test_all_have_fund_a16z_speedrun():
    companies = SpeedrunCrawler(_make_client()).run()
    assert all(c.fund == "a16z-speedrun" for c in companies)


def test_limit_truncates():
    companies = SpeedrunCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = SpeedrunCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    SpeedrunCrawler(client).run()
    assert any("speedrun.a16z.com/companies" in u for u in client.calls)


def test_fetches_all_cohorts():
    client = _make_client()
    SpeedrunCrawler(client).run()
    assert any("cohort=SR001" in u for u in client.calls)
    assert any("cohort=SR002" in u for u in client.calls)


def test_stage_contains_cohort():
    companies = SpeedrunCrawler(_make_client()).run()
    stages = {c.stage for c in companies}
    assert "SR001" in stages
    assert "SR002" in stages


def test_enrich_false_accepted():
    companies = SpeedrunCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 4


def test_workers_param_accepted():
    companies = SpeedrunCrawler(_make_client()).run(workers=10)
    assert len(companies) == 4
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
.venv/bin/python -m pytest tests/test_speedrun_crawler.py -v 2>&1 | head -10
```

Expected: `ImportError` — `SpeedrunCrawler` not defined.

- [ ] **Step 3: Implement `crawler.py`**

Create `vc_crawler/crawlers/a16z_speedrun/crawler.py`:

```python
from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company
from .parser import PORTFOLIO_URL, parse_portfolio_page, fetch_cohort_companies
from .normalizer import normalize

log = logging.getLogger(__name__)


class SpeedrunCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching speedrun portfolio page to discover cohorts ...")
        resp = self.client.get(PORTFOLIO_URL)
        cohorts = parse_portfolio_page(resp.text)
        log.info("Found cohorts: %s", cohorts)

        raw_records: list[dict] = []
        for cohort in cohorts:
            records = fetch_cohort_companies(self.client, cohort)
            log.info("Cohort %s: %d companies", cohort, len(records))
            raw_records.extend(records)

        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]
        log.info("Total: %d companies", len(companies))

        if limit:
            companies = companies[:limit]
        return companies
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
.venv/bin/python -m pytest tests/test_speedrun_crawler.py -v
```

Expected: all tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/a16z_speedrun/crawler.py \
        tests/test_speedrun_crawler.py
git commit -m "feat(speedrun): add SpeedrunCrawler"
```

---

## Task 6: Register in `__main__.py` + CLI integration test

**Files:**
- Modify: `vc_crawler/__main__.py`
- Modify: `tests/test_vc_main.py`

- [ ] **Step 1: Write failing CLI test**

Append to `tests/test_vc_main.py`:

```python
def test_main_writes_speedrun_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.a16z_speedrun.crawler as sr_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="a16z-speedrun", name="Cantor", slug="cantor",
                            fund_url="https://speedrun.a16z.com/companies/cantor")]
    monkeypatch.setattr(sr_mod, "SpeedrunCrawler", Fake)
    rc = cli.main(["--fund", "a16z-speedrun", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "a16z-speedrun_companies.json").exists()
    assert (tmp_path / "a16z-speedrun_companies.csv").exists()
```

- [ ] **Step 2: Run the new test — verify it fails**

```bash
.venv/bin/python -m pytest tests/test_vc_main.py::test_main_writes_speedrun_outputs -v
```

Expected: `SystemExit` or `error: argument --fund: invalid choice` — fund not registered yet.

- [ ] **Step 3: Add `a16z-speedrun` to `_FUND_REGISTRY` in `__main__.py`**

In `vc_crawler/__main__.py`, change:

```python
_FUND_REGISTRY = {
    "sequoia": "vc_crawler.crawlers.sequoia.crawler.SequoiaCrawler",
    "a16z": "vc_crawler.crawlers.a16z.crawler.A16ZCrawler",
}
```

to:

```python
_FUND_REGISTRY = {
    "sequoia": "vc_crawler.crawlers.sequoia.crawler.SequoiaCrawler",
    "a16z": "vc_crawler.crawlers.a16z.crawler.A16ZCrawler",
    "a16z-speedrun": "vc_crawler.crawlers.a16z_speedrun.crawler.SpeedrunCrawler",
}
```

- [ ] **Step 4: Run all tests — verify the full suite passes**

```bash
.venv/bin/python -m pytest -v
```

Expected: all tests `PASSED` (no failures, no errors).

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/__main__.py tests/test_vc_main.py
git commit -m "feat(speedrun): register a16z-speedrun in fund registry"
```

---

## Task 7: Smoke test against the live site

**Files:** none (read-only verification)

- [ ] **Step 1: Run a quick live crawl with `--limit 5`**

```bash
.venv/bin/python -m vc_crawler --fund a16z-speedrun --limit 5 --format json --verbose
```

Expected output (last lines):
```
INFO vc_crawler: Done: 5 companies from a16z-speedrun
INFO vc_crawler: Wrote output/a16z-speedrun_companies.json
```

- [ ] **Step 2: Inspect the output JSON**

```bash
python3 -c "
import json
data = json.load(open('output/a16z-speedrun_companies.json'))
for c in data:
    print(c['id'], c['fund'], c['name'], c['stage'], c['sectors'])
"
```

Expected: 5 entries, `fund == 'a16z-speedrun'`, `stage` in `{SR001..SR006}`, non-empty `sectors` for most.

- [ ] **Step 3: Run full crawl (all cohorts)**

```bash
.venv/bin/python -m vc_crawler --fund a16z-speedrun --verbose
```

Expected: `Done: ~240 companies from a16z-speedrun`, both JSON and CSV written to `output/`.

- [ ] **Step 4: Final commit with output in .gitignore-protected dir**

```bash
git status  # output/ should not appear (it's gitignored)
```

No commit needed — the smoke test is purely verification.
