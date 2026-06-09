# NewSchools Venture Fund Crawler — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `new-schools` fund to the vc-portfolio-crawler CLI, collecting ~300 ventures from 15 paginated HTML listing pages with concurrent detail-page enrichment for description and website.

**Architecture:** Standard 3-file crawler pattern — `parser.py` (HTML parsing for listing + detail pages, taxonomy JSON), `normalizer.py` (raw dict → Company), `crawler.py` (pagination loop + ThreadPoolExecutor enrichment). Year maps fetched up-front from the public WP REST API (`/wp-json/wp/v2/investment-year` and `/wp-json/wp/v2/initial-investment-year`).

**Tech Stack:** Python 3.10, BeautifulSoup4/lxml, concurrent.futures.ThreadPoolExecutor, pytest

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `vc_crawler/crawlers/new_schools/__init__.py` | Empty package marker |
| Create | `vc_crawler/crawlers/new_schools/parser.py` | `parse_term_map`, `parse_listing_page`, `parse_detail_page` |
| Create | `vc_crawler/crawlers/new_schools/normalizer.py` | `normalize` → `Company` |
| Create | `vc_crawler/crawlers/new_schools/crawler.py` | `NewSchoolsCrawler(BaseCrawler)` |
| Create | `tests/fixtures/newschools_listing.html` | 2-card listing fixture, max_page=1 |
| Create | `tests/fixtures/newschools_detail.html` | 1 detail page fixture with description + website |
| Create | `tests/test_new_schools_parser.py` | Tests for all parser functions |
| Create | `tests/test_new_schools_normalizer.py` | Tests for `normalize` |
| Create | `tests/test_new_schools_crawler.py` | Tests for `NewSchoolsCrawler` |
| Modify | `vc_crawler/__main__.py` | Add `"new-schools"` to `_FUND_REGISTRY` |
| Modify | `README.md` | Add NewSchools row to fund table + usage examples |

---

### Task 1: Fixtures and package scaffold

**Files:**
- Create: `vc_crawler/crawlers/new_schools/__init__.py`
- Create: `tests/fixtures/newschools_listing.html`
- Create: `tests/fixtures/newschools_detail.html`

- [ ] **Step 1: Create the empty package init**

```bash
mkdir -p vc_crawler/crawlers/new_schools
touch vc_crawler/crawlers/new_schools/__init__.py
```

- [ ] **Step 2: Create the listing fixture**

Create `tests/fixtures/newschools_listing.html` with this content — two companies, one past/one current, one with logo/one without, max_page=1:

```html
<!DOCTYPE html>
<html>
<body>
<div class="e-loop-item initial-investment-year-714 investment-year-709 investment_area-learning-solutions financial_model-for-profit status-past-venture">
  <a href="https://www.newschools.org/venture/acme-edu/">
    <img src="https://www.newschools.org/wp-content/uploads/acme-logo.png"/>
    <h2 class="elementor-heading-title elementor-size-default">Acme Edu</h2>
    <ul class="elementor-post-info">
      <li><span class="elementor-post-info__item">Learning Solutions</span></li>
    </ul>
  </a>
</div>
<div class="e-loop-item initial-investment-year-720 investment-year-574 investment_area-diverse-leaders financial_model-nonprofit status-current-venture">
  <a href="https://www.newschools.org/venture/beta-learn/">
    <h2 class="elementor-heading-title elementor-size-default">Beta Learn</h2>
    <ul class="elementor-post-info">
      <li><span class="elementor-post-info__item">Diverse Leaders</span></li>
    </ul>
  </a>
</div>
<div class="e-load-more-anchor" data-max-page="1" data-page="1"></div>
</body>
</html>
```

- [ ] **Step 3: Create the detail fixture**

Create `tests/fixtures/newschools_detail.html` — first text block is short (nav, skipped), second is the description (≥50 chars), then a Website link:

```html
<!DOCTYPE html>
<html>
<body>
<div class="elementor-widget-text-editor"><p>Our Vision</p></div>
<div class="elementor-widget-text-editor">
  <p>Acme Edu designs engaging, hands-on learning projects for grades K-8, transforming the classroom into a space for connection and growth.</p>
</div>
<a href="https://acmeedu.com">Website &#x2192;</a>
<a href="https://twitter.com/nsvf">Twitter</a>
</body>
</html>
```

- [ ] **Step 4: Commit**

```bash
git add vc_crawler/crawlers/new_schools/__init__.py \
        tests/fixtures/newschools_listing.html \
        tests/fixtures/newschools_detail.html
git commit -m "test: add NewSchools fixtures and package scaffold"
```

---

### Task 2: `parse_term_map` — TDD

**Files:**
- Create: `vc_crawler/crawlers/new_schools/parser.py`
- Create: `tests/test_new_schools_parser.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_new_schools_parser.py`:

```python
from pathlib import Path
import pytest

from vc_crawler.crawlers.new_schools.parser import (
    PORTFOLIO_URL,
    INV_YEAR_API,
    INIT_YEAR_API,
    parse_term_map,
    parse_listing_page,
    parse_detail_page,
)

LISTING_FIXTURE = (Path(__file__).parent / "fixtures" / "newschools_listing.html").read_text(encoding="utf-8")
DETAIL_FIXTURE  = (Path(__file__).parent / "fixtures" / "newschools_detail.html").read_text(encoding="utf-8")


# ── constants ────────────────────────────────────────────────────────────────

def test_portfolio_url():
    assert PORTFOLIO_URL == "https://www.newschools.org/ventures/"

def test_inv_year_api():
    assert "investment-year" in INV_YEAR_API
    assert "wp-json/wp/v2" in INV_YEAR_API

def test_init_year_api():
    assert "initial-investment-year" in INIT_YEAR_API
    assert "wp-json/wp/v2" in INIT_YEAR_API


# ── parse_term_map ────────────────────────────────────────────────────────────

def test_term_map_basic():
    json_text = '[{"id": 709, "name": "2024"}, {"id": 574, "name": "2023"}]'
    result = parse_term_map(json_text)
    assert result == {709: 2024, 574: 2023}

def test_term_map_returns_int_keys_and_values():
    json_text = '[{"id": 711, "name": "2022"}]'
    m = parse_term_map(json_text)
    key, val = list(m.items())[0]
    assert isinstance(key, int)
    assert isinstance(val, int)

def test_term_map_empty_list():
    assert parse_term_map("[]") == {}
```

- [ ] **Step 2: Run tests — expect ImportError / fail**

```bash
.venv/bin/python -m pytest tests/test_new_schools_parser.py::test_term_map_basic -v
```

Expected: `ImportError: cannot import name 'parse_term_map'` (module does not exist yet).

- [ ] **Step 3: Implement `parse_term_map` in `parser.py`**

Create `vc_crawler/crawlers/new_schools/parser.py`:

```python
from __future__ import annotations

import json
from urllib.parse import urlparse

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.newschools.org/ventures/"
INV_YEAR_API  = "https://www.newschools.org/wp-json/wp/v2/investment-year?per_page=100"
INIT_YEAR_API = "https://www.newschools.org/wp-json/wp/v2/initial-investment-year?per_page=100"


def parse_term_map(json_text: str) -> dict[int, int]:
    return {t["id"]: int(t["name"]) for t in json.loads(json_text)}


def parse_listing_page(html: str) -> tuple[list[dict], int]:
    raise NotImplementedError


def parse_detail_page(html: str) -> dict:
    raise NotImplementedError
```

- [ ] **Step 4: Run tests — expect pass**

```bash
.venv/bin/python -m pytest tests/test_new_schools_parser.py::test_term_map_basic \
    tests/test_new_schools_parser.py::test_term_map_returns_int_keys_and_values \
    tests/test_new_schools_parser.py::test_term_map_empty_list \
    tests/test_new_schools_parser.py::test_portfolio_url \
    tests/test_new_schools_parser.py::test_inv_year_api \
    tests/test_new_schools_parser.py::test_init_year_api -v
```

Expected: 6 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/new_schools/parser.py tests/test_new_schools_parser.py
git commit -m "feat: parse_term_map + parser skeleton"
```

---

### Task 3: `parse_listing_page` — TDD

**Files:**
- Modify: `vc_crawler/crawlers/new_schools/parser.py`
- Modify: `tests/test_new_schools_parser.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_new_schools_parser.py`:

```python
# ── parse_listing_page ────────────────────────────────────────────────────────

def test_listing_returns_tuple():
    result = parse_listing_page(LISTING_FIXTURE)
    assert isinstance(result, tuple) and len(result) == 2

def test_listing_returns_two_records():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert len(records) == 2

def test_listing_max_page():
    _, max_page = parse_listing_page(LISTING_FIXTURE)
    assert max_page == 1

def test_listing_max_page_default_when_no_anchor():
    _, max_page = parse_listing_page("<html><body></body></html>")
    assert max_page == 1

def test_listing_empty_page():
    records, _ = parse_listing_page("<html><body></body></html>")
    assert records == []

def test_listing_card1_name():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["name"] == "Acme Edu"

def test_listing_card1_fund_url():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["fund_url"] == "https://www.newschools.org/venture/acme-edu/"

def test_listing_card1_slug():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["slug"] == "acme-edu"

def test_listing_card1_logo_url():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["logo_url"] == "https://www.newschools.org/wp-content/uploads/acme-logo.png"

def test_listing_card1_sectors():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["sectors"] == ["Learning Solutions"]

def test_listing_card1_init_year_ids():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["init_year_ids"] == [714]

def test_listing_card1_inv_year_ids():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["inv_year_ids"] == [709]

def test_listing_card1_is_past_true():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["is_past"] is True

def test_listing_card2_name():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["name"] == "Beta Learn"

def test_listing_card2_slug():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["slug"] == "beta-learn"

def test_listing_card2_logo_url_none():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["logo_url"] is None

def test_listing_card2_sectors():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["sectors"] == ["Diverse Leaders"]

def test_listing_card2_init_year_ids():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["init_year_ids"] == [720]

def test_listing_card2_is_past_false():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["is_past"] is False

def test_listing_init_ids_do_not_bleed_into_inv_ids():
    """initial-investment-year-714 must NOT appear in inv_year_ids."""
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert 714 not in records[0]["inv_year_ids"]
```

- [ ] **Step 2: Run tests — expect failures**

```bash
.venv/bin/python -m pytest tests/test_new_schools_parser.py -k "listing" -v
```

Expected: all listing tests FAIL with `NotImplementedError`.

- [ ] **Step 3: Implement `parse_listing_page` in `parser.py`**

Replace the `parse_listing_page` stub with:

```python
def parse_listing_page(html: str) -> tuple[list[dict], int]:
    soup = BeautifulSoup(html, "lxml")
    anchor = soup.select_one(".e-load-more-anchor")
    max_page = int(anchor["data-max-page"]) if anchor else 1
    records = [_parse_card(card) for card in soup.select(".e-loop-item")]
    return records, max_page


def _parse_card(card) -> dict:
    classes = card.get("class", [])

    link = card.select_one("a[href]")
    fund_url = link["href"] if link else ""
    slug = urlparse(fund_url).path.strip("/").split("/")[-1] if fund_url else ""

    img = card.select_one("img")
    logo_url = img.get("src") or None if img else None

    title = card.select_one(".elementor-heading-title")
    name = title.get_text(strip=True) if title else ""

    sectors = [el.get_text(strip=True) for el in card.select(".elementor-post-info__item")]

    init_year_ids = [
        int(c.replace("initial-investment-year-", ""))
        for c in classes if c.startswith("initial-investment-year-")
    ]
    inv_year_ids = [
        int(c.replace("investment-year-", ""))
        for c in classes if c.startswith("investment-year-")
    ]

    return {
        "name": name,
        "fund_url": fund_url,
        "slug": slug,
        "logo_url": logo_url,
        "sectors": sectors,
        "inv_year_ids": inv_year_ids,
        "init_year_ids": init_year_ids,
        "is_past": "status-past-venture" in classes,
    }
```

- [ ] **Step 4: Run tests — expect pass**

```bash
.venv/bin/python -m pytest tests/test_new_schools_parser.py -k "listing or constant or term_map" -v
```

Expected: all tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/new_schools/parser.py tests/test_new_schools_parser.py
git commit -m "feat: parse_listing_page + card parsing"
```

---

### Task 4: `parse_detail_page` — TDD

**Files:**
- Modify: `vc_crawler/crawlers/new_schools/parser.py`
- Modify: `tests/test_new_schools_parser.py`

- [ ] **Step 1: Add failing tests**

Append to `tests/test_new_schools_parser.py`:

```python
# ── parse_detail_page ─────────────────────────────────────────────────────────

def test_detail_returns_dict():
    assert isinstance(parse_detail_page(DETAIL_FIXTURE), dict)

def test_detail_description():
    result = parse_detail_page(DETAIL_FIXTURE)
    assert result["description"] == (
        "Acme Edu designs engaging, hands-on learning projects for grades K-8, "
        "transforming the classroom into a space for connection and growth."
    )

def test_detail_skips_short_blocks():
    """'Our Vision' (9 chars) must not be the description."""
    result = parse_detail_page(DETAIL_FIXTURE)
    assert result["description"] != "Our Vision"

def test_detail_website():
    result = parse_detail_page(DETAIL_FIXTURE)
    assert result["website"] == "https://acmeedu.com"

def test_detail_no_description():
    html = "<html><body><div class='elementor-widget-text-editor'><p>Hi</p></div></body></html>"
    assert parse_detail_page(html)["description"] is None

def test_detail_no_website():
    html = "<html><body><p>Some text about the company and its work in education.</p></body></html>"
    assert parse_detail_page(html)["website"] is None

def test_detail_ignores_non_website_links():
    html = """<html><body>
    <div class="elementor-widget-text-editor">
      <p>Company description that is longer than fifty characters for sure.</p>
    </div>
    <a href="https://twitter.com/foo">Twitter</a>
    </body></html>"""
    assert parse_detail_page(html)["website"] is None
```

- [ ] **Step 2: Run tests — expect failures**

```bash
.venv/bin/python -m pytest tests/test_new_schools_parser.py -k "detail" -v
```

Expected: all detail tests FAIL with `NotImplementedError`.

- [ ] **Step 3: Implement `parse_detail_page` in `parser.py`**

Replace the `parse_detail_page` stub with:

```python
def parse_detail_page(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    description = None
    for block in soup.select(".elementor-widget-text-editor"):
        text = block.get_text(strip=True)
        if len(text) >= 50:
            description = text
            break

    website = None
    for a in soup.select("a[href]"):
        if "website" in a.get_text(strip=True).lower():
            href = a.get("href", "")
            if href.startswith("http"):
                website = href
                break

    return {"description": description, "website": website}
```

- [ ] **Step 4: Run all parser tests**

```bash
.venv/bin/python -m pytest tests/test_new_schools_parser.py -v
```

Expected: all tests PASSED (no failures, no errors).

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/new_schools/parser.py tests/test_new_schools_parser.py
git commit -m "feat: parse_detail_page"
```

---

### Task 5: `normalizer.py` — TDD

**Files:**
- Create: `vc_crawler/crawlers/new_schools/normalizer.py`
- Create: `tests/test_new_schools_normalizer.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_new_schools_normalizer.py`:

```python
from vc_crawler.crawlers.new_schools.normalizer import normalize
from vc_crawler.models import Company

_INV_MAP  = {709: 2024, 574: 2023}
_INIT_MAP = {714: 2024, 720: 2023}


def _acme_listing():
    return {
        "name": "Acme Edu",
        "fund_url": "https://www.newschools.org/venture/acme-edu/",
        "slug": "acme-edu",
        "logo_url": "https://www.newschools.org/wp-content/uploads/acme-logo.png",
        "sectors": ["Learning Solutions"],
        "inv_year_ids": [709],
        "init_year_ids": [714],
        "is_past": True,
    }


def _acme_detail():
    return {
        "description": "Acme Edu designs engaging projects for students.",
        "website": "https://acmeedu.com",
    }


def _beta_listing():
    return {
        "name": "Beta Learn",
        "fund_url": "https://www.newschools.org/venture/beta-learn/",
        "slug": "beta-learn",
        "logo_url": None,
        "sectors": ["Diverse Leaders"],
        "inv_year_ids": [574],
        "init_year_ids": [720],
        "is_past": False,
    }


# ── shape ─────────────────────────────────────────────────────────────────────

def test_returns_company():
    assert isinstance(normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1), Company)

def test_id():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 42).id == 42

def test_fund():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).fund == "new-schools"

# ── name / slug / fund_url ────────────────────────────────────────────────────

def test_name():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).name == "Acme Edu"

def test_slug():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).slug == "acme-edu"

def test_fund_url():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).fund_url == \
        "https://www.newschools.org/venture/acme-edu/"

# ── sectors / logo ────────────────────────────────────────────────────────────

def test_sectors():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).sectors == ["Learning Solutions"]

def test_logo_url():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).logo_url == \
        "https://www.newschools.org/wp-content/uploads/acme-logo.png"

def test_logo_url_none():
    assert normalize(_beta_listing(), {}, _INV_MAP, _INIT_MAP, 1).logo_url is None

# ── invested_year ─────────────────────────────────────────────────────────────

def test_invested_year_from_init_map():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).invested_year == 2024

def test_invested_year_beta():
    assert normalize(_beta_listing(), {}, _INV_MAP, _INIT_MAP, 1).invested_year == 2023

def test_invested_year_none_when_no_init_ids():
    listing = _acme_listing()
    listing["init_year_ids"] = []
    assert normalize(listing, {}, _INV_MAP, _INIT_MAP, 1).invested_year is None

def test_invested_year_none_when_id_not_in_map():
    listing = _acme_listing()
    listing["init_year_ids"] = [9999]
    assert normalize(listing, {}, _INV_MAP, _INIT_MAP, 1).invested_year is None

# ── stage ─────────────────────────────────────────────────────────────────────

def test_stage_past():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).stage == "Past"

def test_stage_none_when_current():
    assert normalize(_beta_listing(), {}, _INV_MAP, _INIT_MAP, 1).stage is None

# ── description / website ─────────────────────────────────────────────────────

def test_description_from_detail():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).description == \
        "Acme Edu designs engaging projects for students."

def test_description_none_when_no_detail():
    assert normalize(_acme_listing(), {}, _INV_MAP, _INIT_MAP, 1).description is None

def test_website_from_detail():
    assert normalize(_acme_listing(), _acme_detail(), _INV_MAP, _INIT_MAP, 1).website == "https://acmeedu.com"

def test_website_none_when_no_detail():
    assert normalize(_acme_listing(), {}, _INV_MAP, _INIT_MAP, 1).website is None

# ── always-None fields ────────────────────────────────────────────────────────

def test_stage_year_none():
    assert normalize(_acme_listing(), {}, _INV_MAP, _INIT_MAP, 1).stage_year is None

def test_founded_year_none():
    assert normalize(_acme_listing(), {}, _INV_MAP, _INIT_MAP, 1).founded_year is None

def test_ticker_symbol_none():
    assert normalize(_acme_listing(), {}, _INV_MAP, _INIT_MAP, 1).ticker_symbol is None

def test_acquirer_none():
    assert normalize(_acme_listing(), {}, _INV_MAP, _INIT_MAP, 1).acquirer is None

def test_founders_none():
    assert normalize(_acme_listing(), {}, _INV_MAP, _INIT_MAP, 1).founders is None

def test_source_modified_none():
    assert normalize(_acme_listing(), {}, _INV_MAP, _INIT_MAP, 1).source_modified is None
```

- [ ] **Step 2: Run tests — expect ImportError**

```bash
.venv/bin/python -m pytest tests/test_new_schools_normalizer.py -v
```

Expected: `ImportError: cannot import name 'normalize'`.

- [ ] **Step 3: Implement `normalizer.py`**

Create `vc_crawler/crawlers/new_schools/normalizer.py`:

```python
from __future__ import annotations

from vc_crawler.models import Company


def normalize(
    listing: dict,
    detail: dict,
    inv_map: dict[int, int],
    init_map: dict[int, int],
    company_id: int,
) -> Company:
    init_ids = listing.get("init_year_ids", [])
    invested_year = init_map.get(init_ids[0]) if init_ids else None

    return Company(
        id=company_id,
        fund="new-schools",
        name=listing["name"],
        slug=listing.get("slug", ""),
        fund_url=listing.get("fund_url", ""),
        sectors=listing.get("sectors") or [],
        website=detail.get("website"),
        description=detail.get("description"),
        stage="Past" if listing.get("is_past") else None,
        stage_year=None,
        founded_year=None,
        invested_year=invested_year,
        logo_url=listing.get("logo_url"),
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=None,
    )
```

- [ ] **Step 4: Run tests — expect pass**

```bash
.venv/bin/python -m pytest tests/test_new_schools_normalizer.py -v
```

Expected: all tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/new_schools/normalizer.py tests/test_new_schools_normalizer.py
git commit -m "feat: NewSchools normalizer"
```

---

### Task 6: `crawler.py` — TDD

**Files:**
- Create: `vc_crawler/crawlers/new_schools/crawler.py`
- Create: `tests/test_new_schools_crawler.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_new_schools_crawler.py`:

```python
from pathlib import Path

from vc_crawler.crawlers.new_schools.crawler import NewSchoolsCrawler
from vc_crawler.crawlers.new_schools.parser import (
    PORTFOLIO_URL, INV_YEAR_API, INIT_YEAR_API,
)
from vc_crawler.models import Company

LISTING_HTML = (Path(__file__).parent / "fixtures" / "newschools_listing.html").read_text(encoding="utf-8")
DETAIL_HTML  = (Path(__file__).parent / "fixtures" / "newschools_detail.html").read_text(encoding="utf-8")

INV_YEAR_JSON  = '[{"id": 709, "name": "2024"}, {"id": 574, "name": "2023"}]'
INIT_YEAR_JSON = '[{"id": 714, "name": "2024"}, {"id": 720, "name": "2023"}]'


class _FakeResp:
    def __init__(self, text: str):
        self.text = text


class _FakeClient:
    def __init__(self, responses: dict[str, str]):
        self._responses = responses
        self.calls: list[str] = []

    def get(self, url, **kw):
        self.calls.append(url)
        return _FakeResp(self._responses.get(url, "<html></html>"))


def _make_client(extra_listing: dict[str, str] | None = None) -> _FakeClient:
    responses = {
        INV_YEAR_API:  INV_YEAR_JSON,
        INIT_YEAR_API: INIT_YEAR_JSON,
        PORTFOLIO_URL: LISTING_HTML,
        "https://www.newschools.org/venture/acme-edu/":   DETAIL_HTML,
        "https://www.newschools.org/venture/beta-learn/": DETAIL_HTML,
    }
    if extra_listing:
        responses.update(extra_listing)
    return _FakeClient(responses)


# ── basic shape ───────────────────────────────────────────────────────────────

def test_returns_list_of_companies():
    companies = NewSchoolsCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)

def test_returns_two_companies():
    assert len(NewSchoolsCrawler(_make_client()).run()) == 2

def test_sequential_ids():
    ids = [c.id for c in NewSchoolsCrawler(_make_client()).run()]
    assert ids == [1, 2]

def test_all_fund_new_schools():
    companies = NewSchoolsCrawler(_make_client()).run()
    assert all(c.fund == "new-schools" for c in companies)

# ── limit ─────────────────────────────────────────────────────────────────────

def test_limit_truncates():
    assert len(NewSchoolsCrawler(_make_client()).run(limit=1)) == 1

def test_limit_preserves_sequential_ids():
    ids = [c.id for c in NewSchoolsCrawler(_make_client()).run(limit=1)]
    assert ids == [1]

# ── URL calls ─────────────────────────────────────────────────────────────────

def test_fetches_inv_year_api():
    client = _make_client()
    NewSchoolsCrawler(client).run()
    assert INV_YEAR_API in client.calls

def test_fetches_init_year_api():
    client = _make_client()
    NewSchoolsCrawler(client).run()
    assert INIT_YEAR_API in client.calls

def test_fetches_portfolio_page():
    client = _make_client()
    NewSchoolsCrawler(client).run()
    assert PORTFOLIO_URL in client.calls

def test_fetches_detail_pages_when_enrich_true():
    client = _make_client()
    NewSchoolsCrawler(client).run(enrich=True)
    assert "https://www.newschools.org/venture/acme-edu/" in client.calls
    assert "https://www.newschools.org/venture/beta-learn/" in client.calls

def test_skips_detail_pages_when_enrich_false():
    client = _make_client()
    NewSchoolsCrawler(client).run(enrich=False)
    assert "https://www.newschools.org/venture/acme-edu/" not in client.calls

# ── enrichment content ────────────────────────────────────────────────────────

def test_website_populated_after_enrich():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=True)
    assert all(c.website is not None for c in companies)

def test_description_populated_after_enrich():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=True)
    assert all(c.description is not None for c in companies)

def test_website_none_without_enrich():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert all(c.website is None for c in companies)

# ── pagination ────────────────────────────────────────────────────────────────

def test_pagination_fetches_page_2():
    """Listing with max_page=2 → crawler must fetch PORTFOLIO_URL + '2/'."""
    two_page_listing = LISTING_HTML.replace('data-max-page="1"', 'data-max-page="2"')
    page2_url = PORTFOLIO_URL + "2/"
    client = _make_client(extra_listing={
        PORTFOLIO_URL: two_page_listing,
        page2_url: LISTING_HTML,
    })
    NewSchoolsCrawler(client).run(enrich=False)
    assert page2_url in client.calls

def test_pagination_accumulates_companies():
    """Two pages of 2 each → 4 companies total."""
    two_page_listing = LISTING_HTML.replace('data-max-page="1"', 'data-max-page="2"')
    page2_url = PORTFOLIO_URL + "2/"
    client = _make_client(extra_listing={
        PORTFOLIO_URL: two_page_listing,
        page2_url: LISTING_HTML,
    })
    companies = NewSchoolsCrawler(client).run(enrich=False)
    assert len(companies) == 4

# ── normalizer integration ────────────────────────────────────────────────────

def test_invested_year_resolved():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert companies[0].invested_year == 2024   # acme-edu: init_year_ids=[714] → 2024
    assert companies[1].invested_year == 2023   # beta-learn: init_year_ids=[720] → 2023

def test_stage_past_for_first_company():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert companies[0].stage == "Past"

def test_stage_none_for_second_company():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert companies[1].stage is None

# ── param acceptance ──────────────────────────────────────────────────────────

def test_enrich_false_accepted():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 2

def test_workers_param_accepted():
    companies = NewSchoolsCrawler(_make_client()).run(workers=10)
    assert len(companies) == 2
```

- [ ] **Step 2: Run tests — expect ImportError**

```bash
.venv/bin/python -m pytest tests/test_new_schools_crawler.py -v
```

Expected: `ImportError: cannot import name 'NewSchoolsCrawler'`.

- [ ] **Step 3: Implement `crawler.py`**

Create `vc_crawler/crawlers/new_schools/crawler.py`:

```python
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company

from .normalizer import normalize
from .parser import (
    INIT_YEAR_API,
    INV_YEAR_API,
    PORTFOLIO_URL,
    parse_detail_page,
    parse_listing_page,
    parse_term_map,
)

log = logging.getLogger(__name__)


class NewSchoolsCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        inv_map  = parse_term_map(self.client.get(INV_YEAR_API).text)
        init_map = parse_term_map(self.client.get(INIT_YEAR_API).text)
        log.info("Loaded year maps: %d inv, %d init terms", len(inv_map), len(init_map))

        records, max_page = parse_listing_page(self.client.get(PORTFOLIO_URL).text)
        log.info("Page 1/%d: %d companies", max_page, len(records))

        for page in range(2, max_page + 1):
            url = f"{PORTFOLIO_URL}{page}/"
            page_records, _ = parse_listing_page(self.client.get(url).text)
            records.extend(page_records)
            log.info("Page %d/%d: %d companies", page, max_page, len(page_records))

        log.info("Total from listings: %d companies", len(records))

        if limit:
            records = records[:limit]

        detail_list = self._enrich_all(records, workers) if enrich else [{} for _ in records]

        return [
            normalize(rec, det, inv_map, init_map, i)
            for i, (rec, det) in enumerate(zip(records, detail_list), 1)
        ]

    def _enrich_all(self, records: list[dict], workers: int) -> list[dict]:
        def fetch(record: dict) -> dict:
            try:
                resp = self.client.get(record["fund_url"])
                return parse_detail_page(resp.text)
            except Exception as exc:
                log.warning("enrich failed for %s: %s", record.get("slug"), exc)
                return {}

        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(fetch, records))
```

- [ ] **Step 4: Run all crawler tests**

```bash
.venv/bin/python -m pytest tests/test_new_schools_crawler.py -v
```

Expected: all tests PASSED.

- [ ] **Step 5: Run the full test suite to check for regressions**

```bash
.venv/bin/python -m pytest -v
```

Expected: all pre-existing tests still pass; new tests pass.

- [ ] **Step 6: Commit**

```bash
git add vc_crawler/crawlers/new_schools/crawler.py tests/test_new_schools_crawler.py
git commit -m "feat: NewSchoolsCrawler with pagination and enrichment"
```

---

### Task 7: Register in CLI and update README

**Files:**
- Modify: `vc_crawler/__main__.py`
- Modify: `README.md`

- [ ] **Step 1: Add `new-schools` to `_FUND_REGISTRY` in `vc_crawler/__main__.py`**

In `vc_crawler/__main__.py`, find the `_FUND_REGISTRY` dict and add one entry:

```python
_FUND_REGISTRY = {
    "sequoia":       "vc_crawler.crawlers.sequoia.crawler.SequoiaCrawler",
    "a16z":          "vc_crawler.crawlers.a16z.crawler.A16ZCrawler",
    "a16z-speedrun": "vc_crawler.crawlers.a16z_speedrun.crawler.SpeedrunCrawler",
    "owl-ventures":  "vc_crawler.crawlers.owl_ventures.crawler.OwlCrawler",
    "reach-capital": "vc_crawler.crawlers.reach_capital.crawler.ReachCrawler",
    "gsv-ventures":  "vc_crawler.crawlers.gsv_ventures.crawler.GSVCrawler",
    "learn-capital": "vc_crawler.crawlers.learn_capital.crawler.LearnCrawler",
    "brighteye":     "vc_crawler.crawlers.brighteye.crawler.BrighteyeCrawler",
    "edu-capital":   "vc_crawler.crawlers.edu_capital.crawler.EduCapitalCrawler",
    "new-schools":   "vc_crawler.crawlers.new_schools.crawler.NewSchoolsCrawler",
}
```

- [ ] **Step 2: Verify CLI recognises the new fund**

```bash
.venv/bin/python -m vc_crawler --help
```

Expected: `new-schools` appears in the `--fund` choices list.

- [ ] **Step 3: Update README.md**

In the **Supported funds** table, add a new row:

```markdown
| [NewSchools Venture Fund](https://www.newschools.org/ventures/) | WordPress + Elementor paginated HTML + detail pages | ~300 |
```

In the **Usage** section, add a new example:

```markdown
# Crawl NewSchools Venture Fund portfolio (~300 companies, paginated HTML + detail enrichment)
.venv/bin/python -m vc_crawler --fund new-schools
```

In the **Output files** section, add:

```markdown
- `data/new-schools/companies.json` / `data/new-schools/companies.csv`
```

In the **All Options** table, add `new-schools` to the `--fund` choices.

In the **How It Works** section, add a new subsection:

```markdown
### NewSchools Venture Fund
Two-stage pipeline:
1. Fetch taxonomy year maps from the public WP REST API (`/wp-json/wp/v2/investment-year` and `/wp-json/wp/v2/initial-investment-year`) — maps WordPress term IDs to calendar years
2. Paginate 15 listing pages at `/ventures/`, `/ventures/2/`, …, `/ventures/15/` — each page is static HTML with 20 `.e-loop-item` cards containing company name, logo, investment area, and investment/initial-year term IDs in CSS classes
3. Concurrently fetch each venture's detail page (`/venture/{slug}/`) for description and website URL (skipped with `--no-enrich`)
```

- [ ] **Step 4: Run the full test suite one final time**

```bash
.venv/bin/python -m pytest -v
```

Expected: all tests PASSED. Zero failures.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/__main__.py README.md
git commit -m "feat: register new-schools in CLI and update README"
```
