# BrightEye Ventures Crawler — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a BrightEye Ventures portfolio crawler that parses `https://www.brighteyevc.com/portfolio` and outputs 51 companies to JSON/CSV.

**Architecture:** Single-page Webflow CMS site — one GET, no pagination, no JS needed. Featured companies (4) have rich modal data (name, description, categories); the remaining 47 use slug-derived names. Parser merges featured data into the main card list by website URL. Normalizer derives a clean name from the slug when no featured name is available.

**Tech Stack:** Python 3.10, requests, BeautifulSoup (lxml), pytest

---

## File Map

| Action | Path |
|--------|------|
| Create | `tests/fixtures/brighteye_portfolio.html` |
| Create | `vc_crawler/crawlers/brighteye/__init__.py` |
| Create | `vc_crawler/crawlers/brighteye/parser.py` |
| Create | `vc_crawler/crawlers/brighteye/normalizer.py` |
| Create | `vc_crawler/crawlers/brighteye/crawler.py` |
| Create | `tests/test_brighteye_parser.py` |
| Create | `tests/test_brighteye_normalizer.py` |
| Create | `tests/test_brighteye_crawler.py` |
| Modify | `vc_crawler/__main__.py` |

---

## Task 1: HTML Test Fixture

**Files:**
- Create: `tests/fixtures/brighteye_portfolio.html`

- [ ] **Step 1: Create the fixture file**

```html
<!DOCTYPE html>
<html>
<body>

<!-- ===== FEATURED SECTION (4 highlighted companies with modal data) ===== -->
<div class="featured-companies-collection-list">

  <!-- Featured: Zen Educate -->
  <div class="featured-companies-collection-item w-dyn-item">
    <div class="featured-portfolio-company-item">
      <div class="featued-portfolio-content-wrap">
        <div class="chip-wrap">
          <div class="dark-chip"><div class="sub-head-small">Work</div></div>
          <div class="dark-chip is-outline"><div class="sub-head-small">UK</div></div>
        </div>
        <h4 class="heading-style-h5">Zen Educate</h4>
        <div class="featured-portfolio-description">Leading UK/US supply teacher marketplace.</div>
      </div>
      <div class="fs_modal-1_component">
        <div class="fs_modal-1_popup">
          <div class="featued-modal-exit-wrap">
            <div class="chip-wrap">
              <div class="dark-chip"><div class="sub-head-small">Work</div></div>
              <div class="dark-chip is-outline"><div class="sub-head-small">UK</div></div>
            </div>
          </div>
          <div class="featued-modal-content-wrap">
            <div class="modal-text-wrap">
              <div class="heading-style-h4" id="fs-modal-1-heading">Zen Educate</div>
              <a class="button is-icon is-tertiary w-inline-block" href="https://www.zeneducate.com/">visit website</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

</div>

<!-- ===== PORTFOLIO GRID (all 51 companies, including the 4 featured) ===== -->
<div class="portfolio-companies-collection-list">

  <!-- Card 1: zen-educate — matches featured, not exited -->
  <div class="portfolio-companies-collection-item w-dyn-item">
    <div class="portfolio-item-card-wrap">
      <div class="chip-wrap is-center-aligned">
        <a class="hide w-inline-block" href="/portfolio-companies/zen-educate"></a>
        <div class="dark-chip is-outline"><div class="sub-head-small">UK</div></div>
      </div>
      <div class="exit-tag-wrap">
        <img class="portfolio-card-logo" src="https://cdn.prod.website-files.com/zen_logo.avif" alt=""/>
        <div class="exit-tag-spacer">
          <div class="dark-chip exit-tag w-condition-invisible">
            <div class="sub-head-small">Exited</div>
          </div>
        </div>
      </div>
      <a class="button is-icon is-tertiary w-inline-block" href="https://www.zeneducate.com/">Visit Website</a>
    </div>
  </div>

  <!-- Card 2: uphill — plain card, not exited, has website -->
  <div class="portfolio-companies-collection-item w-dyn-item">
    <div class="portfolio-item-card-wrap">
      <div class="chip-wrap is-center-aligned">
        <a class="hide w-inline-block" href="/portfolio-companies/uphill"></a>
        <div class="dark-chip is-outline"><div class="sub-head-small">Portugal</div></div>
      </div>
      <div class="exit-tag-wrap">
        <img class="portfolio-card-logo" src="https://cdn.prod.website-files.com/uphill_logo.avif" alt=""/>
        <div class="exit-tag-spacer">
          <div class="dark-chip exit-tag w-condition-invisible">
            <div class="sub-head-small">Exited</div>
          </div>
        </div>
      </div>
      <a class="button is-icon is-tertiary w-inline-block" href="https://uphillhealth.com/">Visit Website</a>
    </div>
  </div>

  <!-- Card 3: hack-the-box-copy — slug with -copy suffix, no website link -->
  <div class="portfolio-companies-collection-item w-dyn-item">
    <div class="portfolio-item-card-wrap">
      <div class="chip-wrap is-center-aligned">
        <a class="hide w-inline-block" href="/portfolio-companies/hack-the-box-copy"></a>
        <div class="dark-chip is-outline"><div class="sub-head-small">Greece / UK</div></div>
      </div>
      <div class="exit-tag-wrap">
        <img class="portfolio-card-logo" src="https://cdn.prod.website-files.com/htb_logo.avif" alt=""/>
        <div class="exit-tag-spacer">
          <div class="dark-chip exit-tag w-condition-invisible">
            <div class="sub-head-small">Exited</div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Card 4: gosu — exited, no website -->
  <div class="portfolio-companies-collection-item w-dyn-item">
    <div class="portfolio-item-card-wrap">
      <div class="chip-wrap is-center-aligned">
        <a class="hide w-inline-block" href="/portfolio-companies/gosu"></a>
        <div class="dark-chip is-outline"><div class="sub-head-small">France</div></div>
      </div>
      <div class="exit-tag-wrap">
        <img class="portfolio-card-logo" src="https://cdn.prod.website-files.com/gosu_logo.avif" alt=""/>
        <div class="exit-tag-spacer">
          <div class="dark-chip exit-tag">
            <div class="sub-head-small">Exited</div>
          </div>
        </div>
      </div>
    </div>
  </div>

</div>

</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add tests/fixtures/brighteye_portfolio.html
git commit -m "test: add brighteye portfolio HTML fixture"
```

---

## Task 2: Parser — tests then implementation

**Files:**
- Create: `tests/test_brighteye_parser.py`
- Create: `vc_crawler/crawlers/brighteye/__init__.py`
- Create: `vc_crawler/crawlers/brighteye/parser.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_brighteye_parser.py`:

```python
from pathlib import Path
from vc_crawler.crawlers.brighteye.parser import (
    PORTFOLIO_URL,
    parse_portfolio_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "brighteye_portfolio.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://www.brighteyevc.com/portfolio"


def test_returns_list_of_dicts():
    result = parse_portfolio_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_four_companies():
    assert len(parse_portfolio_page(FIXTURE)) == 4


def test_empty_page_returns_empty_list():
    assert parse_portfolio_page("<html><body></body></html>") == []


# --- Card 1: zen-educate (matched to featured) ---

def test_card1_slug():
    assert parse_portfolio_page(FIXTURE)[0]["slug"] == "zen-educate"


def test_card1_location():
    assert parse_portfolio_page(FIXTURE)[0]["location"] == "UK"


def test_card1_logo_url():
    assert parse_portfolio_page(FIXTURE)[0]["logo_url"] == "https://cdn.prod.website-files.com/zen_logo.avif"


def test_card1_website():
    assert parse_portfolio_page(FIXTURE)[0]["website"] == "https://www.zeneducate.com/"


def test_card1_is_exited_false():
    assert parse_portfolio_page(FIXTURE)[0]["is_exited"] is False


def test_card1_name_from_featured():
    assert parse_portfolio_page(FIXTURE)[0]["name"] == "Zen Educate"


def test_card1_description_from_featured():
    assert parse_portfolio_page(FIXTURE)[0]["description"] == "Leading UK/US supply teacher marketplace."


def test_card1_categories_from_featured():
    assert parse_portfolio_page(FIXTURE)[0]["categories"] == ["Work"]


# --- Card 2: uphill (plain, not in featured) ---

def test_card2_slug():
    assert parse_portfolio_page(FIXTURE)[1]["slug"] == "uphill"


def test_card2_location():
    assert parse_portfolio_page(FIXTURE)[1]["location"] == "Portugal"


def test_card2_website():
    assert parse_portfolio_page(FIXTURE)[1]["website"] == "https://uphillhealth.com/"


def test_card2_is_exited_false():
    assert parse_portfolio_page(FIXTURE)[1]["is_exited"] is False


def test_card2_name_none():
    assert parse_portfolio_page(FIXTURE)[1]["name"] is None


def test_card2_description_none():
    assert parse_portfolio_page(FIXTURE)[1]["description"] is None


def test_card2_categories_empty():
    assert parse_portfolio_page(FIXTURE)[1]["categories"] == []


# --- Card 3: hack-the-box-copy (slug with -copy, no website) ---

def test_card3_slug():
    assert parse_portfolio_page(FIXTURE)[2]["slug"] == "hack-the-box-copy"


def test_card3_website_none():
    assert parse_portfolio_page(FIXTURE)[2]["website"] is None


def test_card3_location():
    assert parse_portfolio_page(FIXTURE)[2]["location"] == "Greece / UK"


# --- Card 4: gosu (exited) ---

def test_card4_slug():
    assert parse_portfolio_page(FIXTURE)[3]["slug"] == "gosu"


def test_card4_is_exited_true():
    assert parse_portfolio_page(FIXTURE)[3]["is_exited"] is True


def test_card4_website_none():
    assert parse_portfolio_page(FIXTURE)[3]["website"] is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && .venv/bin/pytest tests/test_brighteye_parser.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError: No module named 'vc_crawler.crawlers.brighteye'`

- [ ] **Step 3: Create package init**

Create `vc_crawler/crawlers/brighteye/__init__.py` (empty file):

```python
```

- [ ] **Step 4: Implement the parser**

Create `vc_crawler/crawlers/brighteye/parser.py`:

```python
from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.brighteyevc.com/portfolio"


def parse_portfolio_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    featured = _parse_featured(soup)
    cards = soup.select(".portfolio-companies-collection-item")
    return [_parse_card(card, featured) for card in cards]


def _parse_featured(soup) -> dict[str, dict]:
    """Returns dict keyed by website URL with enriched data from featured modals."""
    result = {}
    for item in soup.select(".featured-companies-collection-item"):
        website_el = item.select_one("a.is-tertiary.is-icon")
        if not website_el:
            continue
        website = website_el.get("href") or None
        if not website:
            continue

        name_el = item.select_one(".heading-style-h4")
        name = name_el.get_text(strip=True) if name_el else None

        desc_el = item.select_one(".featured-portfolio-description")
        description = desc_el.get_text(strip=True) if desc_el else None

        # Deduplicate categories — the same chip appears in content area and modal
        cats = list(dict.fromkeys(
            el.get_text(strip=True)
            for el in item.select(".dark-chip:not(.is-outline) .sub-head-small")
        ))

        result[website] = {
            "name": name,
            "description": description,
            "categories": cats,
        }
    return result


def _parse_card(card, featured: dict[str, dict]) -> dict:
    link = card.select_one("a[href*='/portfolio-companies/']")
    slug = link["href"].split("/portfolio-companies/")[-1] if link else ""

    loc_el = card.select_one(".dark-chip.is-outline .sub-head-small")
    location = loc_el.get_text(strip=True) if loc_el else None

    logo = card.select_one("img.portfolio-card-logo")
    logo_url = logo.get("src") or None if logo else None

    website_link = card.select_one("a.is-tertiary.is-icon")
    website = website_link.get("href") or None if website_link else None

    exit_tag = card.select_one(".exit-tag")
    is_exited = bool(
        exit_tag and "w-condition-invisible" not in exit_tag.get("class", [])
    )

    enriched = featured.get(website, {})
    return {
        "slug": slug,
        "location": location,
        "logo_url": logo_url,
        "website": website,
        "is_exited": is_exited,
        "name": enriched.get("name"),
        "description": enriched.get("description"),
        "categories": enriched.get("categories", []),
    }
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && .venv/bin/pytest tests/test_brighteye_parser.py -v
```

Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add vc_crawler/crawlers/brighteye/__init__.py vc_crawler/crawlers/brighteye/parser.py tests/test_brighteye_parser.py
git commit -m "feat: add brighteye parser"
```

---

## Task 3: Normalizer — tests then implementation

**Files:**
- Create: `tests/test_brighteye_normalizer.py`
- Create: `vc_crawler/crawlers/brighteye/normalizer.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_brighteye_normalizer.py`:

```python
from vc_crawler.crawlers.brighteye.normalizer import normalize, PORTFOLIO_URL
from vc_crawler.models import Company


def _zen():
    return {
        "slug": "zen-educate",
        "location": "UK",
        "logo_url": "https://cdn.prod.website-files.com/zen_logo.avif",
        "website": "https://www.zeneducate.com/",
        "is_exited": False,
        "name": "Zen Educate",
        "description": "Leading UK/US supply teacher marketplace.",
        "categories": ["Work"],
    }


def _uphill():
    return {
        "slug": "uphill",
        "location": "Portugal",
        "logo_url": "https://cdn.prod.website-files.com/uphill_logo.avif",
        "website": "https://uphillhealth.com/",
        "is_exited": False,
        "name": None,
        "description": None,
        "categories": [],
    }


def _htb():
    """Slug with -copy suffix, no name, no website."""
    return {
        "slug": "hack-the-box-copy",
        "location": "Greece / UK",
        "logo_url": "https://cdn.prod.website-files.com/htb_logo.avif",
        "website": None,
        "is_exited": False,
        "name": None,
        "description": None,
        "categories": [],
    }


def _gosu():
    return {
        "slug": "gosu",
        "location": "France",
        "logo_url": "https://cdn.prod.website-files.com/gosu_logo.avif",
        "website": None,
        "is_exited": True,
        "name": None,
        "description": None,
        "categories": [],
    }


# --- Basic shape ---

def test_returns_company_instance():
    assert isinstance(normalize(_zen(), 1), Company)


def test_fund_is_brighteye():
    assert normalize(_zen(), 1).fund == "brighteye"


def test_id_assigned():
    assert normalize(_zen(), 42).id == 42


def test_fund_url_constant():
    assert normalize(_zen(), 1).fund_url == PORTFOLIO_URL


def test_fund_url_value():
    assert normalize(_zen(), 1).fund_url == "https://www.brighteyevc.com/portfolio"


# --- Name ---

def test_name_from_featured():
    assert normalize(_zen(), 1).name == "Zen Educate"


def test_name_derived_from_slug_when_no_featured_name():
    assert normalize(_uphill(), 1).name == "Uphill"


def test_name_derived_multiword():
    raw = _uphill()
    raw["slug"] = "iron-hack"
    assert normalize(raw, 1).name == "Iron Hack"


def test_name_strips_copy_suffix():
    assert normalize(_htb(), 1).name == "Hack The Box"


def test_name_strips_copy_suffix_multiword():
    raw = _uphill()
    raw["slug"] = "some-company-copy"
    assert normalize(raw, 1).name == "Some Company"


# --- Slug ---

def test_slug_unchanged_for_clean_slug():
    assert normalize(_zen(), 1).slug == "zen-educate"


def test_slug_copy_suffix_removed():
    assert normalize(_htb(), 1).slug == "hack-the-box"


# --- Sectors ---

def test_sectors_from_featured():
    assert normalize(_zen(), 1).sectors == ["Work"]


def test_sectors_empty_when_no_featured():
    assert normalize(_uphill(), 1).sectors == []


# --- Website ---

def test_website():
    assert normalize(_zen(), 1).website == "https://www.zeneducate.com/"


def test_website_none_when_missing():
    assert normalize(_gosu(), 1).website is None


# --- Description ---

def test_description_from_featured():
    assert normalize(_zen(), 1).description == "Leading UK/US supply teacher marketplace."


def test_description_none_when_not_featured():
    assert normalize(_uphill(), 1).description is None


# --- Stage ---

def test_stage_exited():
    assert normalize(_gosu(), 1).stage == "Exited"


def test_stage_none_when_not_exited():
    assert normalize(_zen(), 1).stage is None


# --- Logo ---

def test_logo_url():
    assert normalize(_zen(), 1).logo_url == "https://cdn.prod.website-files.com/zen_logo.avif"


def test_logo_url_none_when_missing():
    raw = _zen()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


# --- All-None fields ---

def test_stage_year_none():
    assert normalize(_zen(), 1).stage_year is None


def test_founded_year_none():
    assert normalize(_zen(), 1).founded_year is None


def test_invested_year_none():
    assert normalize(_zen(), 1).invested_year is None


def test_source_modified_none():
    assert normalize(_zen(), 1).source_modified is None


def test_ticker_symbol_none():
    assert normalize(_zen(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_zen(), 1).acquirer is None


def test_founders_none():
    assert normalize(_zen(), 1).founders is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && .venv/bin/pytest tests/test_brighteye_normalizer.py -v 2>&1 | head -15
```

Expected: `ModuleNotFoundError: No module named 'vc_crawler.crawlers.brighteye.normalizer'`

- [ ] **Step 3: Implement the normalizer**

Create `vc_crawler/crawlers/brighteye/normalizer.py`:

```python
from __future__ import annotations

import re

from vc_crawler.models import Company

PORTFOLIO_URL = "https://www.brighteyevc.com/portfolio"

_COPY_RE = re.compile(r"-copy$")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def normalize(raw: dict, company_id: int) -> Company:
    clean_slug = _COPY_RE.sub("", raw.get("slug", ""))
    name = raw.get("name") or _slug_to_name(clean_slug)

    return Company(
        id=company_id,
        fund="brighteye",
        name=name,
        slug=clean_slug,
        fund_url=PORTFOLIO_URL,
        sectors=raw.get("categories") or [],
        website=raw.get("website") or None,
        description=raw.get("description") or None,
        stage="Exited" if raw.get("is_exited") else None,
        stage_year=None,
        founded_year=None,
        invested_year=None,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=None,
    )


def _slug_to_name(slug: str) -> str:
    return " ".join(word.capitalize() for word in slug.split("-") if word)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && .venv/bin/pytest tests/test_brighteye_normalizer.py -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/brighteye/normalizer.py tests/test_brighteye_normalizer.py
git commit -m "feat: add brighteye normalizer"
```

---

## Task 4: Crawler — tests then implementation

**Files:**
- Create: `tests/test_brighteye_crawler.py`
- Create: `vc_crawler/crawlers/brighteye/crawler.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_brighteye_crawler.py`:

```python
from pathlib import Path

from vc_crawler.crawlers.brighteye.crawler import BrighteyeCrawler
from vc_crawler.models import Company

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "brighteye_portfolio.html"


class _FakeResp:
    def __init__(self, text: str):
        self.text = text


class _FakeClient:
    def __init__(self, html: str):
        self._html = html
        self.calls: list[str] = []

    def get(self, url, **kw):
        self.calls.append(url)
        return _FakeResp(self._html)


def _make_client():
    return _FakeClient(FIXTURE_HTML.read_text(encoding="utf-8"))


def test_returns_list_of_companies():
    companies = BrighteyeCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    assert len(BrighteyeCrawler(_make_client()).run()) == 4


def test_sequential_ids():
    companies = BrighteyeCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3, 4]


def test_all_fund_brighteye():
    companies = BrighteyeCrawler(_make_client()).run()
    assert all(c.fund == "brighteye" for c in companies)


def test_limit_truncates():
    companies = BrighteyeCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = BrighteyeCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    BrighteyeCrawler(client).run()
    assert any("brighteyevc.com/portfolio" in u for u in client.calls)


def test_enrich_false_accepted():
    companies = BrighteyeCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 4


def test_workers_param_accepted():
    companies = BrighteyeCrawler(_make_client()).run(workers=10)
    assert len(companies) == 4
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && .venv/bin/pytest tests/test_brighteye_crawler.py -v 2>&1 | head -15
```

Expected: `ImportError: cannot import name 'BrighteyeCrawler'`

- [ ] **Step 3: Implement the crawler**

Create `vc_crawler/crawlers/brighteye/crawler.py`:

```python
from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company

from .normalizer import normalize
from .parser import PORTFOLIO_URL, parse_portfolio_page

log = logging.getLogger(__name__)


class BrighteyeCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching BrightEye Ventures portfolio page ...")
        resp = self.client.get(PORTFOLIO_URL)
        raw_records = parse_portfolio_page(resp.text)
        log.info("Parsed %d companies", len(raw_records))
        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]
        if limit:
            companies = companies[:limit]
        return companies
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && .venv/bin/pytest tests/test_brighteye_crawler.py -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/brighteye/crawler.py tests/test_brighteye_crawler.py
git commit -m "feat: add BrighteyeCrawler"
```

---

## Task 5: CLI Registration

**Files:**
- Modify: `vc_crawler/__main__.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_vc_main.py` — open the file and append this test:

```python
def test_fund_registry_contains_brighteye():
    from vc_crawler.__main__ import _FUND_REGISTRY
    assert "brighteye" in _FUND_REGISTRY
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && .venv/bin/pytest tests/test_vc_main.py::test_fund_registry_contains_brighteye -v
```

Expected: FAIL — `AssertionError`

- [ ] **Step 3: Register brighteye in the CLI**

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
}
```

- [ ] **Step 4: Run all tests to verify nothing broke**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && .venv/bin/pytest --tb=short -q
```

Expected: all tests pass (no regressions)

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/__main__.py tests/test_vc_main.py
git commit -m "feat: register brighteye in CLI"
```
