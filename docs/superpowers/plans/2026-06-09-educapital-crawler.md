# EduCapital Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `EduCapitalCrawler` that fetches 41 portfolio companies from a single Webflow CMS page and saves them to `data/edu-capital/`.

**Architecture:** Single GET to `https://www.educapitalvc.com/portfolio`, BeautifulSoup parses `.portfolio_content.w-dyn-item` cards. Company name is derived from the website domain (no text name field in HTML). Follows the established 3-file parser/normalizer/crawler pattern identical to `learn_capital` and `brighteye`.

**Tech Stack:** Python 3.10, BeautifulSoup4 (`lxml`), `urllib.parse`, `re`, pytest

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `vc_crawler/crawlers/edu_capital/__init__.py` | Package marker |
| Create | `vc_crawler/crawlers/edu_capital/parser.py` | HTML → list[dict] |
| Create | `vc_crawler/crawlers/edu_capital/normalizer.py` | dict → Company |
| Create | `vc_crawler/crawlers/edu_capital/crawler.py` | Orchestration |
| Create | `tests/fixtures/educapital_portfolio.html` | Minimal 4-card fixture |
| Create | `tests/test_educapital_parser.py` | Parser tests |
| Create | `tests/test_educapital_normalizer.py` | Normalizer tests |
| Create | `tests/test_educapital_crawler.py` | Crawler integration tests |
| Modify | `vc_crawler/__main__.py` | Register `"edu-capital"` key |

---

## Task 1: HTML fixture

**Files:**
- Create: `tests/fixtures/educapital_portfolio.html`

- [ ] **Step 1: Write the fixture file**

Create `tests/fixtures/educapital_portfolio.html` with exactly **4 cards** covering all cases:
- Card 1: `360learning.com` — `Future of work`, NOT acquired
- Card 2: `appscho.com` — `Future of education`, IS acquired
- Card 3: `buddy.ai` — `Future of education`, NOT acquired
- Card 4: Apple Store URL — `Future of education`, NOT acquired (edge case)

```html
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"/><title>Our Portfolio</title></head>
<body>
<div fs-cmsfilter-element="list" class="portfolio_collection w-dyn-list">
  <div role="list" class="portfolio_grid w-dyn-items">

    <!-- Card 1: 360learning — not acquired, Future of work -->
    <div role="listitem" class="portfolio_content w-dyn-item">
      <div class="portfolio_card">
        <div class="tag is-portfolio w-condition-invisible">Acquired</div>
        <img src="https://cdn.prod.website-files.com/abc123_360_logo.png"
             loading="lazy" alt="" class="portfolio_logo"/>
        <p class="text-color-purple">Collaborative LMS</p>
        <div class="fs-filter-category" fs-cmsfilter-field="category">Future of work</div>
        <a class="portfolio_card-back w-inline-block" href="https://360learning.com" target="_blank">
          <div class="button is-icon"><div>Discover</div></div>
        </a>
        <a class="portfolio_card-back w-inline-block" href="https://360learning.com" target="_blank">
          <div class="button is-icon"><div>Discover</div></div>
        </a>
      </div>
    </div>

    <!-- Card 2: appscho — acquired, Future of education -->
    <div role="listitem" class="portfolio_content w-dyn-item">
      <div class="portfolio_card">
        <div class="tag is-portfolio">Acquired</div>
        <img src="https://cdn.prod.website-files.com/def456_Appscho_.png"
             loading="lazy" alt="" class="portfolio_logo"/>
        <p class="text-color-purple">Application for school management for students</p>
        <div class="fs-filter-category" fs-cmsfilter-field="category">Future of education</div>
        <a class="portfolio_card-back w-inline-block" href="https://www.appscho.com/" target="_blank">
          <div class="button is-icon"><div>Discover</div></div>
        </a>
        <a class="portfolio_card-back w-inline-block" href="https://www.appscho.com/" target="_blank">
          <div class="button is-icon"><div>Discover</div></div>
        </a>
      </div>
    </div>

    <!-- Card 3: buddy.ai — not acquired, Future of education -->
    <div role="listitem" class="portfolio_content w-dyn-item">
      <div class="portfolio_card">
        <div class="tag is-portfolio w-condition-invisible">Acquired</div>
        <img src="https://cdn.prod.website-files.com/ghi789_buddy_logo.jpg"
             loading="lazy" alt="" class="portfolio_logo"/>
        <p class="text-color-purple">AI-based language tutor for children</p>
        <div class="fs-filter-category" fs-cmsfilter-field="category">Future of education</div>
        <a class="portfolio_card-back w-inline-block" href="https://buddy.ai/fr/" target="_blank">
          <div class="button is-icon"><div>Discover</div></div>
        </a>
        <a class="portfolio_card-back w-inline-block" href="https://buddy.ai/fr/" target="_blank">
          <div class="button is-icon"><div>Discover</div></div>
        </a>
      </div>
    </div>

    <!-- Card 4: Apple Store link (edge case) — not acquired, Future of education -->
    <div role="listitem" class="portfolio_content w-dyn-item">
      <div class="portfolio_card">
        <div class="tag is-portfolio w-condition-invisible">Acquired</div>
        <img src="https://cdn.prod.website-files.com/jkl012_screenshot.jpg"
             loading="lazy" alt="" class="portfolio_logo"/>
        <p class="text-color-purple">Conversational AI for language learning</p>
        <div class="fs-filter-category" fs-cmsfilter-field="category">Future of education</div>
        <a class="portfolio_card-back w-inline-block"
           href="https://apps.apple.com/fr/app/emma-parler-anglais/id6737470910"
           target="_blank">
          <div class="button is-icon"><div>Discover</div></div>
        </a>
        <a class="portfolio_card-back w-inline-block"
           href="https://apps.apple.com/fr/app/emma-parler-anglais/id6737470910"
           target="_blank">
          <div class="button is-icon"><div>Discover</div></div>
        </a>
      </div>
    </div>

  </div>
</div>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add tests/fixtures/educapital_portfolio.html
git commit -m "test: add EduCapital portfolio HTML fixture"
```

---

## Task 2: Parser

**Files:**
- Create: `vc_crawler/crawlers/edu_capital/__init__.py`
- Create: `vc_crawler/crawlers/edu_capital/parser.py`
- Create: `tests/test_educapital_parser.py`

- [ ] **Step 1: Write failing parser tests**

Create `tests/test_educapital_parser.py`:

```python
from pathlib import Path
from vc_crawler.crawlers.edu_capital.parser import (
    PORTFOLIO_URL,
    parse_portfolio_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "educapital_portfolio.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://www.educapitalvc.com/portfolio"


def test_returns_list_of_dicts():
    result = parse_portfolio_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_four_companies():
    assert len(parse_portfolio_page(FIXTURE)) == 4


def test_empty_page_returns_empty_list():
    assert parse_portfolio_page("<html><body></body></html>") == []


# --- Card 1: 360learning ---

def test_card1_logo_url():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["logo_url"] == "https://cdn.prod.website-files.com/abc123_360_logo.png"


def test_card1_description():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["description"] == "Collaborative LMS"


def test_card1_category():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["category"] == "Future of work"


def test_card1_website():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["website"] == "https://360learning.com"


def test_card1_not_acquired():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["acquired"] is False


# --- Card 2: appscho (acquired) ---

def test_card2_acquired_true():
    r = parse_portfolio_page(FIXTURE)[1]
    assert r["acquired"] is True


def test_card2_website():
    r = parse_portfolio_page(FIXTURE)[1]
    assert r["website"] == "https://www.appscho.com/"


def test_card2_category():
    r = parse_portfolio_page(FIXTURE)[1]
    assert r["category"] == "Future of education"


# --- Card 3: buddy.ai ---

def test_card3_not_acquired():
    r = parse_portfolio_page(FIXTURE)[2]
    assert r["acquired"] is False


def test_card3_website():
    r = parse_portfolio_page(FIXTURE)[2]
    assert r["website"] == "https://buddy.ai/fr/"


# --- Card 4: Apple Store URL ---

def test_card4_website_apple():
    r = parse_portfolio_page(FIXTURE)[3]
    assert r["website"] == "https://apps.apple.com/fr/app/emma-parler-anglais/id6737470910"


def test_card4_not_acquired():
    r = parse_portfolio_page(FIXTURE)[3]
    assert r["acquired"] is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && source .venv/bin/activate && pytest tests/test_educapital_parser.py -v 2>&1 | head -30
```

Expected: `ERROR` — module not found.

- [ ] **Step 3: Create package marker**

Create `vc_crawler/crawlers/edu_capital/__init__.py` (empty file):

```python
```

- [ ] **Step 4: Implement parser**

Create `vc_crawler/crawlers/edu_capital/parser.py`:

```python
from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.educapitalvc.com/portfolio"


def parse_portfolio_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    items = soup.select(".portfolio_content.w-dyn-item")
    return [_parse_item(item) for item in items]


def _parse_item(item) -> dict:
    logo_img = item.find("img", class_="portfolio_logo")
    logo_url = logo_img["src"] if logo_img else None

    desc_el = item.find("p", class_="text-color-purple")
    description = desc_el.get_text(strip=True) if desc_el else None

    cat_el = item.find(attrs={"fs-cmsfilter-field": "category"})
    category = cat_el.get_text(strip=True) if cat_el else None

    back_links = item.select("a.portfolio_card-back")
    website = back_links[0].get("href") if back_links else None

    tag_el = item.find("div", class_="tag")
    acquired = bool(
        tag_el and "w-condition-invisible" not in tag_el.get("class", [])
    )

    return {
        "logo_url": logo_url,
        "description": description,
        "category": category,
        "website": website,
        "acquired": acquired,
    }
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_educapital_parser.py -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add vc_crawler/crawlers/edu_capital/__init__.py vc_crawler/crawlers/edu_capital/parser.py tests/test_educapital_parser.py
git commit -m "feat: add EduCapital parser"
```

---

## Task 3: Normalizer

**Files:**
- Create: `vc_crawler/crawlers/edu_capital/normalizer.py`
- Create: `tests/test_educapital_normalizer.py`

- [ ] **Step 1: Write failing normalizer tests**

Create `tests/test_educapital_normalizer.py`:

```python
from vc_crawler.crawlers.edu_capital.normalizer import normalize, PORTFOLIO_URL, _name_from_url
from vc_crawler.models import Company


def _r360():
    return {
        "logo_url": "https://cdn.prod.website-files.com/abc123_360_logo.png",
        "description": "Collaborative LMS",
        "category": "Future of work",
        "website": "https://360learning.com",
        "acquired": False,
    }


def _rappscho():
    return {
        "logo_url": "https://cdn.prod.website-files.com/def456_Appscho_.png",
        "description": "Application for school management for students",
        "category": "Future of education",
        "website": "https://www.appscho.com/",
        "acquired": True,
    }


def _rbuddy():
    return {
        "logo_url": "https://cdn.prod.website-files.com/ghi789_buddy_logo.jpg",
        "description": "AI-based language tutor for children",
        "category": "Future of education",
        "website": "https://buddy.ai/fr/",
        "acquired": False,
    }


def _remma():
    return {
        "logo_url": "https://cdn.prod.website-files.com/jkl012_screenshot.jpg",
        "description": "Conversational AI for language learning",
        "category": "Future of education",
        "website": "https://apps.apple.com/fr/app/emma-parler-anglais/id6737470910",
        "acquired": False,
    }


# --- Basic shape ---

def test_returns_company_instance():
    assert isinstance(normalize(_r360(), 1), Company)


def test_fund_is_edu_capital():
    assert normalize(_r360(), 1).fund == "edu-capital"


def test_id_assigned():
    assert normalize(_r360(), 42).id == 42


def test_fund_url_constant():
    assert normalize(_r360(), 1).fund_url == PORTFOLIO_URL


def test_fund_url_value():
    assert normalize(_r360(), 1).fund_url == "https://www.educapitalvc.com/portfolio"


# --- _name_from_url ---

def test_name_from_url_plain_domain():
    assert _name_from_url("https://360learning.com") == "360learning"


def test_name_from_url_strips_www():
    assert _name_from_url("https://www.appscho.com/") == "appscho"


def test_name_from_url_subdomain_stripped():
    assert _name_from_url("https://buddy.ai/fr/") == "buddy"


def test_name_from_url_apple_store():
    assert _name_from_url(
        "https://apps.apple.com/fr/app/emma-parler-anglais/id6737470910"
    ) == "emma"


def test_name_from_url_empty_string():
    assert _name_from_url("") == ""


# --- name field on Company ---

def test_name_360learning():
    assert normalize(_r360(), 1).name == "360learning"


def test_name_appscho():
    assert normalize(_rappscho(), 1).name == "appscho"


def test_name_buddy():
    assert normalize(_rbuddy(), 1).name == "buddy"


def test_name_emma_from_apple_url():
    assert normalize(_remma(), 1).name == "emma"


# --- slug ---

def test_slug_360learning():
    assert normalize(_r360(), 1).slug == "360learning"


def test_slug_appscho():
    assert normalize(_rappscho(), 1).slug == "appscho"


# --- sectors ---

def test_sectors_future_of_work():
    assert normalize(_r360(), 1).sectors == ["Future of work"]


def test_sectors_future_of_education():
    assert normalize(_rbuddy(), 1).sectors == ["Future of education"]


def test_sectors_empty_when_no_category():
    raw = _r360()
    raw["category"] = None
    assert normalize(raw, 1).sectors == []


# --- description ---

def test_description():
    assert normalize(_r360(), 1).description == "Collaborative LMS"


def test_description_none_when_missing():
    raw = _r360()
    raw["description"] = None
    assert normalize(raw, 1).description is None


# --- website ---

def test_website():
    assert normalize(_r360(), 1).website == "https://360learning.com"


def test_website_none_when_missing():
    raw = _r360()
    raw["website"] = None
    assert normalize(raw, 1).website is None


# --- stage ---

def test_stage_acquired():
    assert normalize(_rappscho(), 1).stage == "Acquired"


def test_stage_none_when_not_acquired():
    assert normalize(_r360(), 1).stage is None


# --- logo ---

def test_logo_url():
    assert normalize(_r360(), 1).logo_url == "https://cdn.prod.website-files.com/abc123_360_logo.png"


def test_logo_url_none_when_missing():
    raw = _r360()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


# --- All-None fields ---

def test_stage_year_none():
    assert normalize(_r360(), 1).stage_year is None


def test_founded_year_none():
    assert normalize(_r360(), 1).founded_year is None


def test_invested_year_none():
    assert normalize(_r360(), 1).invested_year is None


def test_source_modified_none():
    assert normalize(_r360(), 1).source_modified is None


def test_ticker_symbol_none():
    assert normalize(_r360(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_r360(), 1).acquirer is None


def test_founders_none():
    assert normalize(_r360(), 1).founders is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_educapital_normalizer.py -v 2>&1 | head -20
```

Expected: `ERROR` — module not found.

- [ ] **Step 3: Implement normalizer**

Create `vc_crawler/crawlers/edu_capital/normalizer.py`:

```python
from __future__ import annotations

import re
from urllib.parse import urlparse

from vc_crawler.models import Company

PORTFOLIO_URL = "https://www.educapitalvc.com/portfolio"
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def normalize(raw: dict, company_id: int) -> Company:
    name = _name_from_url(raw.get("website") or "")
    return Company(
        id=company_id,
        fund="edu-capital",
        name=name,
        slug=_slugify(name),
        fund_url=PORTFOLIO_URL,
        sectors=[raw["category"]] if raw.get("category") else [],
        website=raw.get("website") or None,
        description=raw.get("description") or None,
        stage="Acquired" if raw.get("acquired") else None,
        stage_year=None,
        founded_year=None,
        invested_year=None,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=None,
    )


def _name_from_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    host = parsed.netloc
    host = re.sub(r"^www\.", "", host)
    if host == "apps.apple.com":
        m = re.search(r"/app/([^/]+)/", parsed.path)
        if m:
            return m.group(1).split("-")[0]
        return ""
    return host.split(".")[0]


def _slugify(name: str) -> str:
    return _NON_ALNUM_RE.sub("-", name.lower()).strip("-")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_educapital_normalizer.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/edu_capital/normalizer.py tests/test_educapital_normalizer.py
git commit -m "feat: add EduCapital normalizer"
```

---

## Task 4: Crawler

**Files:**
- Create: `vc_crawler/crawlers/edu_capital/crawler.py`
- Create: `tests/test_educapital_crawler.py`

- [ ] **Step 1: Write failing crawler tests**

Create `tests/test_educapital_crawler.py`:

```python
from pathlib import Path

from vc_crawler.crawlers.edu_capital.crawler import EduCapitalCrawler
from vc_crawler.models import Company

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "educapital_portfolio.html"


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
    companies = EduCapitalCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    assert len(EduCapitalCrawler(_make_client()).run()) == 4


def test_sequential_ids():
    companies = EduCapitalCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3, 4]


def test_all_fund_edu_capital():
    companies = EduCapitalCrawler(_make_client()).run()
    assert all(c.fund == "edu-capital" for c in companies)


def test_limit_truncates():
    companies = EduCapitalCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = EduCapitalCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    EduCapitalCrawler(client).run()
    assert any("educapitalvc.com/portfolio" in u for u in client.calls)


def test_enrich_false_accepted():
    companies = EduCapitalCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 4


def test_workers_param_accepted():
    companies = EduCapitalCrawler(_make_client()).run(workers=10)
    assert len(companies) == 4
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_educapital_crawler.py -v 2>&1 | head -20
```

Expected: `ERROR` — module not found.

- [ ] **Step 3: Implement crawler**

Create `vc_crawler/crawlers/edu_capital/crawler.py`:

```python
from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company

from .normalizer import normalize
from .parser import PORTFOLIO_URL, parse_portfolio_page

log = logging.getLogger(__name__)


class EduCapitalCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching EduCapital portfolio page ...")
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
pytest tests/test_educapital_crawler.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/edu_capital/crawler.py tests/test_educapital_crawler.py
git commit -m "feat: add EduCapitalCrawler"
```

---

## Task 5: CLI registration and full test run

**Files:**
- Modify: `vc_crawler/__main__.py` (add `"edu-capital"` entry)

- [ ] **Step 1: Register in CLI**

Edit `vc_crawler/__main__.py`. Add `"edu-capital"` to `_FUND_REGISTRY`:

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
}
```

- [ ] **Step 2: Run the full test suite**

```bash
pytest --tb=short -q
```

Expected: all existing tests still pass, new tests pass. Zero failures.

- [ ] **Step 3: Commit**

```bash
git add vc_crawler/__main__.py
git commit -m "feat: register edu-capital in CLI"
```

---

## Task 6: Live crawl and data file

**Files:**
- Create: `data/edu-capital/companies.json`
- Create: `data/edu-capital/companies.csv`

- [ ] **Step 1: Run live crawl**

```bash
cd /home/zylex/SBER/vc-portfolio-crawler && source .venv/bin/activate
python -m vc_crawler --fund edu-capital --verbose
```

Expected output ends with: `Done: 41 companies from edu-capital`

- [ ] **Step 2: Verify output files exist and look correct**

```bash
python -c "
import json
data = json.load(open('data/edu-capital/companies.json'))
print(f'Count: {len(data)}')
for c in data[:3]:
    print(c['id'], c['name'], c['website'], c['sectors'], c['stage'])
"
```

Expected: 41 records, names like `360learning`, `appscho`, `buddy`.

- [ ] **Step 3: Commit data and release tag**

```bash
git add data/edu-capital/companies.json data/edu-capital/companies.csv
git commit -m "release: v2.7.0 EduCapital portfolio data"
```
