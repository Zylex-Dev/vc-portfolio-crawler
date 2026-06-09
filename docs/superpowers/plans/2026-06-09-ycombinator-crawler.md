# Y Combinator Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `y-combinator` fund crawler that fetches all ~125 EdTech portfolio companies from YC's public Algolia search index and exports them to JSON/CSV.

**Architecture:** Single-stage pipeline — one Algolia REST POST request returns all Education-filtered companies in one page (no pagination needed at current scale). Data is parsed from the JSON response and normalized to the shared `Company` model. No detail-page enrichment required.

**Tech Stack:** Python 3.10, `requests` (via existing `PoliteClient.post`), `re` for batch-year extraction. No new dependencies.

---

## File Structure

| Path | Action | Responsibility |
|------|--------|----------------|
| `vc_crawler/crawlers/y_combinator/__init__.py` | Create | Package marker |
| `vc_crawler/crawlers/y_combinator/parser.py` | Create | POST to Algolia, return raw hit list |
| `vc_crawler/crawlers/y_combinator/normalizer.py` | Create | Map raw Algolia hit → `Company` |
| `vc_crawler/crawlers/y_combinator/crawler.py` | Create | Orchestrate parser + normalizer, apply limit |
| `tests/fixtures/yc_algolia_response.json` | Create | 3-record Algolia fixture for unit tests |
| `tests/test_yc_parser.py` | Create | Tests for `fetch_education_companies` |
| `tests/test_yc_normalizer.py` | Create | Tests for `normalize` |
| `tests/test_yc_crawler.py` | Create | Tests for `YCCrawler.run` |
| `vc_crawler/__main__.py` | Modify | Add `"y-combinator"` to `_FUND_REGISTRY` |
| `tests/test_vc_main.py` | Modify | Add CLI integration test for y-combinator |
| `README.md` | Modify | Add YC entry to fund table, usage examples, schema, How It Works |

---

## Task 1: Create Algolia fixture file

**Files:**
- Create: `tests/fixtures/yc_algolia_response.json`

- [ ] **Step 1: Write fixture JSON**

Create `tests/fixtures/yc_algolia_response.json`:

```json
{
  "hits": [
    {
      "id": 86,
      "name": "Codecademy",
      "slug": "codecademy",
      "small_logo_thumb_url": "https://bookface-images.s3.amazonaws.com/small_logos/codecademy.png",
      "website": "http://codecademy.com",
      "all_locations": "New York, NY, USA",
      "long_description": "Codecademy is the leading online learning platform for technical skills.",
      "one_liner": "The leading online learning platform for technical skills.",
      "team_size": 225,
      "industry": "Education",
      "subindustry": "Education",
      "batch": "Summer 2011",
      "status": "Acquired",
      "stage": "Growth",
      "industries": ["Education"],
      "objectID": "86"
    },
    {
      "id": 999,
      "name": "Outschool",
      "slug": "outschool",
      "small_logo_thumb_url": "https://bookface-images.s3.amazonaws.com/small_logos/outschool.png",
      "website": "https://outschool.com",
      "all_locations": "San Francisco, CA, USA",
      "long_description": null,
      "one_liner": "A live online learning platform that empowers kids ages 3-18.",
      "team_size": 50,
      "industry": "Education",
      "subindustry": "Education",
      "batch": "Winter 2016",
      "status": "Active",
      "stage": "Growth",
      "industries": ["Education"],
      "objectID": "999"
    },
    {
      "id": 777,
      "name": "DropSchool",
      "slug": "dropschool",
      "small_logo_thumb_url": null,
      "website": null,
      "all_locations": "",
      "long_description": null,
      "one_liner": null,
      "team_size": 0,
      "industry": "Education",
      "subindustry": "Education",
      "batch": "Summer 2020",
      "status": "Inactive",
      "stage": null,
      "industries": ["Education"],
      "objectID": "777"
    }
  ],
  "nbHits": 3,
  "page": 0,
  "nbPages": 1,
  "hitsPerPage": 1000
}
```

- [ ] **Step 2: Commit**

```bash
git add tests/fixtures/yc_algolia_response.json
git commit -m "test: add YC Algolia fixture with 3 Education companies"
```

---

## Task 2: Implement `parser.py`

**Files:**
- Create: `vc_crawler/crawlers/y_combinator/__init__.py`
- Create: `vc_crawler/crawlers/y_combinator/parser.py`
- Test: `tests/test_yc_parser.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_yc_parser.py`:

```python
import json
from pathlib import Path
import pytest
from vc_crawler.crawlers.y_combinator.parser import (
    fetch_education_companies,
    ALGOLIA_URL,
    ALGOLIA_APP_ID,
    ALGOLIA_API_KEY,
)

FIXTURE = Path(__file__).parent / "fixtures" / "yc_algolia_response.json"


class _FakeResp:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class _FakeClient:
    def __init__(self, response):
        self._response = response
        self.calls: list[tuple] = []  # (url, kwargs)

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _FakeResp(self._response)


def _make_client():
    return _FakeClient(json.loads(FIXTURE.read_text()))


def test_returns_list_of_dicts():
    result = fetch_education_companies(_make_client())
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_all_hits():
    result = fetch_education_companies(_make_client())
    assert len(result) == 3


def test_hits_have_name_field():
    result = fetch_education_companies(_make_client())
    assert all("name" in r for r in result)


def test_makes_one_post_request():
    client = _make_client()
    fetch_education_companies(client)
    assert len(client.calls) == 1


def test_posts_to_algolia_url():
    client = _make_client()
    fetch_education_companies(client)
    url, _ = client.calls[0]
    assert url == ALGOLIA_URL


def test_request_includes_algolia_headers():
    client = _make_client()
    fetch_education_companies(client)
    _, kwargs = client.calls[0]
    headers = kwargs.get("headers", {})
    assert headers.get("x-algolia-application-id") == ALGOLIA_APP_ID
    assert headers.get("x-algolia-api-key") == ALGOLIA_API_KEY


def test_request_filters_education():
    client = _make_client()
    fetch_education_companies(client)
    _, kwargs = client.calls[0]
    body = kwargs.get("json", {})
    assert body.get("filters") == "industries:Education"


def test_constants_non_empty():
    assert ALGOLIA_URL
    assert ALGOLIA_APP_ID
    assert ALGOLIA_API_KEY
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler
.venv/bin/python -m pytest tests/test_yc_parser.py -v 2>&1 | head -30
```

Expected: `ModuleNotFoundError` or `ImportError` — `parser.py` does not exist yet.

- [ ] **Step 3: Create package marker**

Create `vc_crawler/crawlers/y_combinator/__init__.py` (empty):

```python
```

- [ ] **Step 4: Implement `parser.py`**

Create `vc_crawler/crawlers/y_combinator/parser.py`:

```python
from __future__ import annotations

ALGOLIA_URL = "https://45bwzj1sgc-dsn.algolia.net/1/indexes/YCCompany_production/query"
ALGOLIA_APP_ID = "45BWZJ1SGC"
ALGOLIA_API_KEY = (
    "NzllNTY5MzJiZGM2OTY2ZTQwMDEzOTNhYWZiZGRjODlhYzVkNjBmOGRjNzJiMWM4ZTU0ZDlhYT"
    "ZjOTJiMjlhMWFuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3By"
    "b2R1Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZX"
    "JzPSU1QiUyMnljZGNfcHVibGljJTIyJTVE"
)


def fetch_education_companies(client) -> list[dict]:
    """POST to Algolia and return raw hit dicts for all Education companies."""
    resp = client.post(
        ALGOLIA_URL,
        headers={
            "x-algolia-application-id": ALGOLIA_APP_ID,
            "x-algolia-api-key": ALGOLIA_API_KEY,
        },
        json={
            "query": "",
            "hitsPerPage": 1000,
            "filters": "industries:Education",
        },
    )
    data = resp.json()
    return data["hits"]
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
.venv/bin/python -m pytest tests/test_yc_parser.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add vc_crawler/crawlers/y_combinator/__init__.py \
        vc_crawler/crawlers/y_combinator/parser.py \
        tests/test_yc_parser.py
git commit -m "feat: add YC Algolia parser — single POST returns all Education hits"
```

---

## Task 3: Implement `normalizer.py`

**Files:**
- Create: `vc_crawler/crawlers/y_combinator/normalizer.py`
- Test: `tests/test_yc_normalizer.py`

**Field mapping:**

| Company field | Source | Notes |
|---|---|---|
| `id` | sequential arg | |
| `fund` | `"ycombinator"` | hardcoded |
| `name` | `raw["name"]` | |
| `slug` | `raw["slug"]` | |
| `fund_url` | `"https://www.ycombinator.com/companies/" + slug` | |
| `sectors` | `raw["industries"]` | list, default `[]` |
| `website` | `raw["website"]` | `None` if falsy |
| `description` | `raw["long_description"] or raw["one_liner"]` | `None` if both falsy |
| `stage` | see below | |
| `stage_year` | `None` | not in data |
| `founded_year` | `None` | not in data |
| `invested_year` | year from `raw["batch"]` via regex | e.g. `"Summer 2011"` → `2011` |
| `logo_url` | `raw["small_logo_thumb_url"]` | `None` if falsy |
| `ticker_symbol` | `None` | not in data |
| `acquirer` | `None` | not in data |
| `founders` | `None` | not in data |

**Stage logic:**
- If `status == "Acquired"` → `stage = "Acquired"`
- If `status == "Inactive"` → `stage = "Inactive"`
- Otherwise → `raw.get("stage")` (e.g. `"Growth"`, `"Early"`, or `None`)

- [ ] **Step 1: Write failing tests**

Create `tests/test_yc_normalizer.py`:

```python
import pytest
from vc_crawler.crawlers.y_combinator.normalizer import normalize
from vc_crawler.models import Company


def _codecademy():
    return {
        "id": 86,
        "name": "Codecademy",
        "slug": "codecademy",
        "small_logo_thumb_url": "https://example.com/logo.png",
        "website": "http://codecademy.com",
        "long_description": "Codecademy is the leading online learning platform.",
        "one_liner": "The leading online learning platform.",
        "batch": "Summer 2011",
        "status": "Acquired",
        "stage": "Growth",
        "industries": ["Education"],
    }


def _outschool():
    return {
        "id": 999,
        "name": "Outschool",
        "slug": "outschool",
        "small_logo_thumb_url": "https://example.com/outschool.png",
        "website": "https://outschool.com",
        "long_description": None,
        "one_liner": "A live online learning platform for kids.",
        "batch": "Winter 2016",
        "status": "Active",
        "stage": "Growth",
        "industries": ["Education"],
    }


def _dropschool():
    return {
        "id": 777,
        "name": "DropSchool",
        "slug": "dropschool",
        "small_logo_thumb_url": None,
        "website": None,
        "long_description": None,
        "one_liner": None,
        "batch": "Summer 2020",
        "status": "Inactive",
        "stage": None,
        "industries": [],
    }


def test_returns_company_instance():
    assert isinstance(normalize(_codecademy(), 1), Company)


def test_fund_is_ycombinator():
    assert normalize(_codecademy(), 1).fund == "ycombinator"


def test_id_assigned():
    assert normalize(_codecademy(), 42).id == 42


def test_name():
    assert normalize(_codecademy(), 1).name == "Codecademy"


def test_slug():
    assert normalize(_codecademy(), 1).slug == "codecademy"


def test_fund_url():
    assert normalize(_codecademy(), 1).fund_url == "https://www.ycombinator.com/companies/codecademy"


def test_sectors():
    assert normalize(_codecademy(), 1).sectors == ["Education"]


def test_sectors_empty_list():
    assert normalize(_dropschool(), 1).sectors == []


def test_website():
    assert normalize(_codecademy(), 1).website == "http://codecademy.com"


def test_website_none_when_null():
    assert normalize(_dropschool(), 1).website is None


def test_description_uses_long_description():
    assert normalize(_codecademy(), 1).description == "Codecademy is the leading online learning platform."


def test_description_falls_back_to_one_liner():
    assert normalize(_outschool(), 1).description == "A live online learning platform for kids."


def test_description_none_when_both_missing():
    assert normalize(_dropschool(), 1).description is None


def test_stage_acquired():
    assert normalize(_codecademy(), 1).stage == "Acquired"


def test_stage_inactive():
    assert normalize(_dropschool(), 1).stage == "Inactive"


def test_stage_active_uses_stage_field():
    assert normalize(_outschool(), 1).stage == "Growth"


def test_stage_active_none_when_stage_field_none():
    raw = _outschool()
    raw["stage"] = None
    assert normalize(raw, 1).stage is None


def test_stage_year_none():
    assert normalize(_codecademy(), 1).stage_year is None


def test_founded_year_none():
    assert normalize(_codecademy(), 1).founded_year is None


def test_invested_year_from_batch():
    assert normalize(_codecademy(), 1).invested_year == 2011


def test_invested_year_winter_batch():
    assert normalize(_outschool(), 1).invested_year == 2016


def test_invested_year_summer_2020():
    assert normalize(_dropschool(), 1).invested_year == 2020


def test_logo_url():
    assert normalize(_codecademy(), 1).logo_url == "https://example.com/logo.png"


def test_logo_url_none():
    assert normalize(_dropschool(), 1).logo_url is None


def test_ticker_symbol_none():
    assert normalize(_codecademy(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_codecademy(), 1).acquirer is None


def test_founders_none():
    assert normalize(_codecademy(), 1).founders is None


def test_source_modified_none():
    assert normalize(_codecademy(), 1).source_modified is None
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
.venv/bin/python -m pytest tests/test_yc_normalizer.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError` — `normalizer.py` does not exist yet.

- [ ] **Step 3: Implement `normalizer.py`**

Create `vc_crawler/crawlers/y_combinator/normalizer.py`:

```python
from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

FUND_URL_BASE = "https://www.ycombinator.com/companies"
_YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')


def normalize(raw: dict, company_id: int) -> Company:
    slug = raw.get("slug", "")
    status = raw.get("status", "")

    if status == "Acquired":
        stage = "Acquired"
    elif status == "Inactive":
        stage = "Inactive"
    else:
        stage = raw.get("stage") or None

    return Company(
        id=company_id,
        fund="ycombinator",
        name=raw.get("name", ""),
        slug=slug,
        fund_url=f"{FUND_URL_BASE}/{slug}",
        sectors=raw.get("industries") or [],
        website=raw.get("website") or None,
        description=raw.get("long_description") or raw.get("one_liner") or None,
        stage=stage,
        stage_year=None,
        founded_year=None,
        invested_year=_parse_batch_year(raw.get("batch")),
        logo_url=raw.get("small_logo_thumb_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=None,
    )


def _parse_batch_year(batch: Optional[str]) -> Optional[int]:
    if not batch:
        return None
    m = _YEAR_RE.search(batch)
    return int(m.group()) if m else None
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
.venv/bin/python -m pytest tests/test_yc_normalizer.py -v
```

Expected: all 28 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/y_combinator/normalizer.py \
        tests/test_yc_normalizer.py
git commit -m "feat: add YC normalizer — maps Algolia hits to Company model"
```

---

## Task 4: Implement `crawler.py`

**Files:**
- Create: `vc_crawler/crawlers/y_combinator/crawler.py`
- Test: `tests/test_yc_crawler.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_yc_crawler.py`:

```python
import json
from pathlib import Path
from vc_crawler.crawlers.y_combinator.crawler import YCCrawler
from vc_crawler.models import Company

FIXTURE = Path(__file__).parent / "fixtures" / "yc_algolia_response.json"


class _FakeResp:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class _FakeClient:
    def __init__(self, response):
        self._response = response
        self.calls: list[tuple] = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _FakeResp(self._response)


def _make_client():
    return _FakeClient(json.loads(FIXTURE.read_text()))


def test_returns_list_of_companies():
    companies = YCCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    companies = YCCrawler(_make_client()).run()
    assert len(companies) == 3


def test_sequential_ids():
    companies = YCCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3]


def test_all_have_fund_ycombinator():
    companies = YCCrawler(_make_client()).run()
    assert all(c.fund == "ycombinator" for c in companies)


def test_limit_truncates():
    companies = YCCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = YCCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_makes_one_post_request():
    client = _make_client()
    YCCrawler(client).run()
    assert len(client.calls) == 1


def test_enrich_false_accepted():
    companies = YCCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 3


def test_workers_param_accepted():
    companies = YCCrawler(_make_client()).run(workers=10)
    assert len(companies) == 3


def test_first_company_name():
    companies = YCCrawler(_make_client()).run()
    assert companies[0].name == "Codecademy"


def test_acquired_stage():
    companies = YCCrawler(_make_client()).run()
    codecademy = next(c for c in companies if c.slug == "codecademy")
    assert codecademy.stage == "Acquired"


def test_invested_year_from_batch():
    companies = YCCrawler(_make_client()).run()
    codecademy = next(c for c in companies if c.slug == "codecademy")
    assert codecademy.invested_year == 2011
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
.venv/bin/python -m pytest tests/test_yc_crawler.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError` — `crawler.py` does not exist yet.

- [ ] **Step 3: Implement `crawler.py`**

Create `vc_crawler/crawlers/y_combinator/crawler.py`:

```python
from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company
from .parser import fetch_education_companies
from .normalizer import normalize

log = logging.getLogger(__name__)


class YCCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching Y Combinator Education portfolio via Algolia ...")
        raw_records = fetch_education_companies(self.client)
        log.info("Parsed %d companies", len(raw_records))

        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]

        if limit:
            companies = companies[:limit]
        return companies
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
.venv/bin/python -m pytest tests/test_yc_crawler.py -v
```

Expected: all 12 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/y_combinator/crawler.py \
        tests/test_yc_crawler.py
git commit -m "feat: add YCCrawler — orchestrates Algolia fetch + normalization"
```

---

## Task 5: Register in CLI and add integration test

**Files:**
- Modify: `vc_crawler/__main__.py`
- Modify: `tests/test_vc_main.py`

- [ ] **Step 1: Write failing integration test**

Append to `tests/test_vc_main.py`:

```python
def test_fund_registry_contains_y_combinator():
    from vc_crawler.__main__ import _FUND_REGISTRY
    assert "y-combinator" in _FUND_REGISTRY


def test_main_writes_y_combinator_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.y_combinator.crawler as yc_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="ycombinator", name="Codecademy",
                            slug="codecademy",
                            fund_url="https://www.ycombinator.com/companies/codecademy")]
    monkeypatch.setattr(yc_mod, "YCCrawler", Fake)
    rc = cli.main(["--fund", "y-combinator", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "y-combinator" / "companies.json").exists()
    assert (tmp_path / "y-combinator" / "companies.csv").exists()
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
.venv/bin/python -m pytest tests/test_vc_main.py::test_fund_registry_contains_y_combinator \
                           tests/test_vc_main.py::test_main_writes_y_combinator_outputs -v
```

Expected: FAIL — `y-combinator` not in registry.

- [ ] **Step 3: Register the crawler in `__main__.py`**

In `vc_crawler/__main__.py`, add one line to `_FUND_REGISTRY`:

```python
_FUND_REGISTRY = {
    "sequoia": "vc_crawler.crawlers.sequoia.crawler.SequoiaCrawler",
    "a16z": "vc_crawler.crawlers.a16z.crawler.A16ZCrawler",
    "a16z-speedrun": "vc_crawler.crawlers.a16z_speedrun.crawler.SpeedrunCrawler",
    "owl-ventures": "vc_crawler.crawlers.owl_ventures.crawler.OwlCrawler",
    "reach-capital": "vc_crawler.crawlers.reach_capital.crawler.ReachCrawler",
    "gsv-ventures": "vc_crawler.crawlers.gsv_ventures.crawler.GSVCrawler",
    "learn-capital": "vc_crawler.crawlers.learn_capital.crawler.LearnCrawler",
    "brighteye": "vc_crawler.crawlers.brighteye.crawler.BrighteyeCrawler",
    "edu-capital": "vc_crawler.crawlers.edu_capital.crawler.EduCapitalCrawler",
    "new-schools": "vc_crawler.crawlers.new_schools.crawler.NewSchoolsCrawler",
    "y-combinator": "vc_crawler.crawlers.y_combinator.crawler.YCCrawler",
}
```

- [ ] **Step 4: Run all new tests**

```bash
.venv/bin/python -m pytest tests/test_vc_main.py::test_fund_registry_contains_y_combinator \
                           tests/test_vc_main.py::test_main_writes_y_combinator_outputs -v
```

Expected: both PASS.

- [ ] **Step 5: Run full test suite to check for regressions**

```bash
.venv/bin/python -m pytest -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add vc_crawler/__main__.py tests/test_vc_main.py
git commit -m "feat: register y-combinator in fund registry and CLI"
```

---

## Task 6: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add YC row to the fund table**

In `README.md`, add to the Supported funds table:

```markdown
| [Y Combinator](https://www.ycombinator.com/companies?industry=Education) | Algolia REST API (public, single request) | ~125 |
```

- [ ] **Step 2: Add CLI usage example**

In the Usage section, add:

```bash
# Crawl Y Combinator Education portfolio (~125 companies, single Algolia API request)
.venv/bin/python -m vc_crawler --fund y-combinator
```

- [ ] **Step 3: Add output path**

In the Output files list, add:

```
- `data/y-combinator/companies.json` / `data/y-combinator/companies.csv`
```

- [ ] **Step 4: Add `--fund` choices**

In the All Options table, add `y-combinator` to the fund choices list.

- [ ] **Step 5: Update Output Schema fund field**

In the schema table, add `"ycombinator"` to the `fund` field description.

- [ ] **Step 6: Add How It Works section**

Add at the end of the How It Works section:

```markdown
### Y Combinator
Single HTTP POST to the Algolia REST API (`https://45bwzj1sgc-dsn.algolia.net/1/indexes/YCCompany_production/query`) with filter `industries:Education` and `hitsPerPage=1000`. The public Algolia key is embedded in the YC companies page HTML (`window.AlgoliaOpts`). All ~125 EdTech company records are returned inline — no pagination or detail-page requests needed.
```

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -m "docs: add Y Combinator to README fund list and How It Works"
```

---

## Task 7: Smoke test against live API

- [ ] **Step 1: Run the crawler against the live site**

```bash
.venv/bin/python -m vc_crawler --fund y-combinator --limit 5 --format json --verbose
```

Expected output:
```
INFO vc_crawler.crawlers.y_combinator.crawler: Fetching Y Combinator Education portfolio via Algolia ...
INFO vc_crawler.crawlers.y_combinator.crawler: Parsed 125 companies
INFO vc_crawler: Done: 5 companies from y-combinator
INFO vc_crawler: Wrote data/y-combinator/companies.json
```

- [ ] **Step 2: Inspect the output**

```bash
python3 -c "import json; d=json.load(open('data/y-combinator/companies.json')); [print(c['name'], '|', c['stage'], '|', c['invested_year']) for c in d]"
```

Expected: 5 rows with names, stage values, and 4-digit invested years.

- [ ] **Step 3: Run full crawl and verify count**

```bash
.venv/bin/python -m vc_crawler --fund y-combinator --format json
python3 -c "import json; d=json.load(open('data/y-combinator/companies.json')); print(f'{len(d)} companies')"
```

Expected: `125 companies` (or close — count may drift as YC adds new companies).
