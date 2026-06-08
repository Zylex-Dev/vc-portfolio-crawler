# GSV Ventures Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `gsv-ventures` fund to the VC Portfolio Crawler that fetches ~87 portfolio companies from `https://gsv.ventures/portfolio/` via a single static HTML GET request.

**Architecture:** Single-stage, no enrichment — mirrors the `owl_ventures` pattern exactly. One HTTP request fetches a static HTML page containing all company cards. Each card is parsed into a raw dict, then normalized into the shared `Company` model.

**Tech Stack:** Python 3.10+, BeautifulSoup4/lxml, pytest, existing `BaseCrawler` / `Company` / `PoliteClient` infrastructure.

---

### Task 1: Create HTML test fixture

**Files:**
- Create: `tests/fixtures/gsv_ventures_portfolio.html`

The fixture contains 3 representative cards used by all downstream tests:
- **Card A** (`EduLearn Pro`, fund2) — full data: description paragraph, logo, 2 founders, investment, year, segment
- **Card B** (`SkillUp`, fund1) — minimal: only name, tagline, website link; no `<aside>`, no description `<p>`
- **Card C** (`LearnPath`, fund3) — 3 founders, no description paragraph (only `<h2>` tagline)

- [ ] **Step 1: Create the fixture file**

`tests/fixtures/gsv_ventures_portfolio.html`:
```html
<!DOCTYPE html>
<html>
<body>
<div class="c-grid js-portfolio-grid">

  <!-- Card A: full data, fund2 -->
  <div class="c-grid--item active fund2" data-position="0">
    <div class="c-grid--item-image">
      <img class="lazyload" data-src="https://gsv.ventures/wp-content/uploads/logo-edulearnpro.png" src=""/>
    </div>
    <div class="c-grid--item-content">
      <div class="c-grid--item-hero">
        <img class="lazyload" data-src="https://gsv.ventures/wp-content/uploads/hero-edulearnpro.jpg" src=""/>
      </div>
      <div class="c-grid--item-copy">
        <main>
          <div class="company-tags">
            <span class="company-name">EduLearn Pro</span>
            <span class="company-location">San Francisco, CA</span>
          </div>
          <h2>Transforming how students learn online</h2>
          <p>EduLearn Pro is an online learning platform for K-12 students.</p>
          <p><a href="https://edulearnpro.com/" rel="noopener" target="_blank">Learn more</a> about <strong>EduLearn Pro</strong></p>
        </main>
        <aside>
          <ul class="company-info">
            <li><span class="company-info--title">Founders/Leadership</span>Alice Smith, Bob Jones</li>
            <li><span class="company-info--title">Investment</span>Series A, 2021</li>
            <li><span class="company-info--title">Year Founded</span>2018</li>
            <li><span class="company-info--title">Segment</span>Pre-K-12</li>
          </ul>
        </aside>
      </div>
    </div>
  </div>

  <!-- Card B: minimal data, fund1, no aside -->
  <div class="c-grid--item active fund1" data-position="1">
    <div class="c-grid--item-image">
      <img class="lazyload" data-src="https://gsv.ventures/wp-content/uploads/logo-skillup.png" src=""/>
    </div>
    <div class="c-grid--item-content">
      <div class="c-grid--item-copy">
        <main>
          <div class="company-tags">
            <span class="company-name">SkillUp</span>
            <span class="company-location">New York, NY</span>
          </div>
          <h2>Building tomorrow's workforce today</h2>
          <p><a href="https://skillup.io/" rel="noopener" target="_blank">Learn more</a> about <strong>SkillUp</strong></p>
        </main>
      </div>
    </div>
  </div>

  <!-- Card C: fund3, 3 founders, no description paragraph -->
  <div class="c-grid--item active fund3" data-position="2">
    <div class="c-grid--item-image">
      <img class="lazyload" data-src="https://gsv.ventures/wp-content/uploads/logo-learnpath.png" src=""/>
    </div>
    <div class="c-grid--item-content">
      <div class="c-grid--item-copy">
        <main>
          <div class="company-tags">
            <span class="company-name">LearnPath</span>
            <span class="company-location">Austin, TX</span>
          </div>
          <h2>Personalized learning journeys for everyone</h2>
          <p><a href="https://learnpath.com/" rel="noopener" target="_blank">Learn more</a> about <strong>LearnPath</strong></p>
        </main>
        <aside>
          <ul class="company-info">
            <li><span class="company-info--title">Founders/Leadership</span>Carol Davis, Dan Evans, Eve Foster</li>
            <li><span class="company-info--title">Investment</span>Seed, 2020</li>
            <li><span class="company-info--title">Year Founded</span>2019</li>
            <li><span class="company-info--title">Segment</span>Post-Secondary</li>
          </ul>
        </aside>
      </div>
    </div>
  </div>

</div>
</body>
</html>
```

- [ ] **Step 2: Verify fixture is readable**

Run: `python3 -c "from pathlib import Path; h = Path('tests/fixtures/gsv_ventures_portfolio.html').read_text(); print(len(h), 'bytes')"`  
Expected: prints a byte count (non-zero).

- [ ] **Step 3: Commit fixture**

```bash
git add tests/fixtures/gsv_ventures_portfolio.html
git commit -m "test: add GSV Ventures HTML fixture (3 cards)"
```

---

### Task 2: Parser — TDD

**Files:**
- Create: `tests/test_gsv_parser.py`
- Create: `vc_crawler/crawlers/gsv_ventures/parser.py`

The parser fetches `https://gsv.ventures/portfolio/`, finds every `div.c-grid--item`, and extracts raw field dicts. The "Learn more" `<a>` tag is the website link; any other `<p>` is the description. `company-info` `<li>` values are extracted by stripping the `<span>` title text from the full `li` text.

- [ ] **Step 1: Write the failing tests**

`tests/test_gsv_parser.py`:
```python
from pathlib import Path
from vc_crawler.crawlers.gsv_ventures.parser import (
    PORTFOLIO_URL,
    parse_portfolio_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "gsv_ventures_portfolio.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://gsv.ventures/portfolio/"


def test_returns_list_of_dicts():
    result = parse_portfolio_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_three_companies():
    assert len(parse_portfolio_page(FIXTURE)) == 3


def test_empty_page_returns_empty_list():
    assert parse_portfolio_page("<html><body></body></html>") == []


# --- Card A: EduLearn Pro (index 0) ---

def test_card_a_name():
    assert parse_portfolio_page(FIXTURE)[0]["name"] == "EduLearn Pro"


def test_card_a_tagline():
    assert parse_portfolio_page(FIXTURE)[0]["tagline"] == "Transforming how students learn online"


def test_card_a_description():
    assert parse_portfolio_page(FIXTURE)[0]["description"] == "EduLearn Pro is an online learning platform for K-12 students."


def test_card_a_website():
    assert parse_portfolio_page(FIXTURE)[0]["website"] == "https://edulearnpro.com/"


def test_card_a_logo_url():
    assert parse_portfolio_page(FIXTURE)[0]["logo_url"] == "https://gsv.ventures/wp-content/uploads/logo-edulearnpro.png"


def test_card_a_founders():
    assert parse_portfolio_page(FIXTURE)[0]["founders"] == ["Alice Smith", "Bob Jones"]


def test_card_a_investment():
    assert parse_portfolio_page(FIXTURE)[0]["investment"] == "Series A, 2021"


def test_card_a_founded_year_str():
    assert parse_portfolio_page(FIXTURE)[0]["founded_year_str"] == "2018"


def test_card_a_sector():
    assert parse_portfolio_page(FIXTURE)[0]["sector"] == "Pre-K-12"


# --- Card B: SkillUp (index 1) — minimal, no aside ---

def test_card_b_name():
    assert parse_portfolio_page(FIXTURE)[1]["name"] == "SkillUp"


def test_card_b_website():
    assert parse_portfolio_page(FIXTURE)[1]["website"] == "https://skillup.io/"


def test_card_b_description_none():
    assert parse_portfolio_page(FIXTURE)[1]["description"] is None


def test_card_b_founders_empty():
    assert parse_portfolio_page(FIXTURE)[1]["founders"] == []


def test_card_b_investment_none():
    assert parse_portfolio_page(FIXTURE)[1]["investment"] is None


def test_card_b_founded_year_str_none():
    assert parse_portfolio_page(FIXTURE)[1]["founded_year_str"] is None


def test_card_b_sector_none():
    assert parse_portfolio_page(FIXTURE)[1]["sector"] is None


# --- Card C: LearnPath (index 2) — 3 founders, no description p ---

def test_card_c_name():
    assert parse_portfolio_page(FIXTURE)[2]["name"] == "LearnPath"


def test_card_c_founders_multiple():
    assert parse_portfolio_page(FIXTURE)[2]["founders"] == ["Carol Davis", "Dan Evans", "Eve Foster"]


def test_card_c_description_none():
    assert parse_portfolio_page(FIXTURE)[2]["description"] is None


def test_card_c_investment():
    assert parse_portfolio_page(FIXTURE)[2]["investment"] == "Seed, 2020"


def test_card_c_sector():
    assert parse_portfolio_page(FIXTURE)[2]["sector"] == "Post-Secondary"
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
.venv/bin/python -m pytest tests/test_gsv_parser.py -v 2>&1 | head -20
```
Expected: `ModuleNotFoundError: No module named 'vc_crawler.crawlers.gsv_ventures'`

- [ ] **Step 3: Create the package and implement parser**

Create `vc_crawler/crawlers/gsv_ventures/__init__.py` (empty file).

Create `vc_crawler/crawlers/gsv_ventures/parser.py`:
```python
from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://gsv.ventures/portfolio/"


def parse_portfolio_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    return [_parse_card(card) for card in soup.find_all("div", class_="c-grid--item")]


def _parse_card(card) -> dict:
    raw: dict = {
        "name": "",
        "tagline": None,
        "description": None,
        "website": None,
        "logo_url": None,
        "founders": [],
        "investment": None,
        "founded_year_str": None,
        "sector": None,
    }

    img_wrapper = card.find(class_="c-grid--item-image")
    if img_wrapper:
        logo = img_wrapper.find("img")
        if logo:
            raw["logo_url"] = logo.get("data-src") or None

    content = card.find(class_="c-grid--item-content")
    if not content:
        return raw

    main = content.find("main")
    if main:
        tags = main.find(class_="company-tags")
        if tags:
            name_el = tags.find(class_="company-name")
            raw["name"] = name_el.get_text(strip=True) if name_el else ""

        h2 = main.find("h2")
        if h2:
            raw["tagline"] = h2.get_text(strip=True)

        for p in main.find_all("p"):
            a = p.find("a")
            if a and a.get_text(strip=True).lower().startswith("learn more"):
                raw["website"] = a.get("href") or None
            elif not raw["description"]:
                text = p.get_text(strip=True)
                if text:
                    raw["description"] = text

    aside = content.find("aside")
    if aside:
        for li in aside.find_all("li"):
            title_el = li.find(class_="company-info--title")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            val = li.get_text(strip=True)[len(title):].strip()
            if not val:
                continue
            if title == "Founders/Leadership":
                raw["founders"] = [f.strip() for f in val.split(",") if f.strip()]
            elif title == "Investment":
                raw["investment"] = val
            elif title == "Year Founded":
                raw["founded_year_str"] = val
            elif title == "Segment":
                raw["sector"] = val

    return raw
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
.venv/bin/python -m pytest tests/test_gsv_parser.py -v
```
Expected: all tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/gsv_ventures/__init__.py \
        vc_crawler/crawlers/gsv_ventures/parser.py \
        tests/test_gsv_parser.py
git commit -m "feat: add GSV Ventures HTML parser"
```

---

### Task 3: Normalizer — TDD

**Files:**
- Create: `tests/test_gsv_normalizer.py`
- Create: `vc_crawler/crawlers/gsv_ventures/normalizer.py`

The normalizer converts a raw dict into `Company`. Key logic: `_parse_investment("Series A, 2021")` → `("Series A", 2021)`; `_slugify("EduLearn Pro")` → `"edulearn-pro"`; description prefers the `description` key, falls back to `tagline`.

- [ ] **Step 1: Write the failing tests**

`tests/test_gsv_normalizer.py`:
```python
from vc_crawler.crawlers.gsv_ventures.normalizer import normalize, PORTFOLIO_URL
from vc_crawler.models import Company


def _edulearnpro():
    return {
        "name": "EduLearn Pro",
        "tagline": "Transforming how students learn online",
        "description": "EduLearn Pro is an online learning platform for K-12 students.",
        "website": "https://edulearnpro.com/",
        "logo_url": "https://gsv.ventures/wp-content/uploads/logo-edulearnpro.png",
        "founders": ["Alice Smith", "Bob Jones"],
        "investment": "Series A, 2021",
        "founded_year_str": "2018",
        "sector": "Pre-K-12",
    }


def _skillup():
    return {
        "name": "SkillUp",
        "tagline": "Building tomorrow's workforce today",
        "description": None,
        "website": "https://skillup.io/",
        "logo_url": "https://gsv.ventures/wp-content/uploads/logo-skillup.png",
        "founders": [],
        "investment": None,
        "founded_year_str": None,
        "sector": None,
    }


def _learnpath():
    return {
        "name": "LearnPath",
        "tagline": "Personalized learning journeys for everyone",
        "description": None,
        "website": "https://learnpath.com/",
        "logo_url": "https://gsv.ventures/wp-content/uploads/logo-learnpath.png",
        "founders": ["Carol Davis", "Dan Evans", "Eve Foster"],
        "investment": "Seed, 2020",
        "founded_year_str": "2019",
        "sector": "Post-Secondary",
    }


def test_returns_company_instance():
    assert isinstance(normalize(_edulearnpro(), 1), Company)


def test_fund_is_gsv_ventures():
    assert normalize(_edulearnpro(), 1).fund == "gsv-ventures"


def test_id_assigned():
    assert normalize(_edulearnpro(), 42).id == 42


def test_name():
    assert normalize(_edulearnpro(), 1).name == "EduLearn Pro"


def test_slug():
    assert normalize(_edulearnpro(), 1).slug == "edulearn-pro"


def test_slug_simple():
    assert normalize(_skillup(), 1).slug == "skillup"


def test_fund_url_constant():
    assert normalize(_edulearnpro(), 1).fund_url == PORTFOLIO_URL


def test_fund_url_value():
    assert normalize(_edulearnpro(), 1).fund_url == "https://gsv.ventures/portfolio/"


def test_sectors_from_segment():
    assert normalize(_edulearnpro(), 1).sectors == ["Pre-K-12"]


def test_sectors_empty_when_no_segment():
    assert normalize(_skillup(), 1).sectors == []


def test_sectors_post_secondary():
    assert normalize(_learnpath(), 1).sectors == ["Post-Secondary"]


def test_website():
    assert normalize(_edulearnpro(), 1).website == "https://edulearnpro.com/"


def test_website_none_when_missing():
    raw = _edulearnpro()
    raw["website"] = None
    assert normalize(raw, 1).website is None


def test_description_uses_paragraph():
    assert normalize(_edulearnpro(), 1).description == "EduLearn Pro is an online learning platform for K-12 students."


def test_description_falls_back_to_tagline():
    assert normalize(_skillup(), 1).description == "Building tomorrow's workforce today"


def test_description_tagline_when_no_paragraph():
    assert normalize(_learnpath(), 1).description == "Personalized learning journeys for everyone"


def test_stage_series_a():
    assert normalize(_edulearnpro(), 1).stage == "Series A"


def test_stage_seed():
    assert normalize(_learnpath(), 1).stage == "Seed"


def test_stage_none_when_no_investment():
    assert normalize(_skillup(), 1).stage is None


def test_invested_year_from_investment():
    assert normalize(_edulearnpro(), 1).invested_year == 2021


def test_invested_year_seed():
    assert normalize(_learnpath(), 1).invested_year == 2020


def test_invested_year_none_when_no_investment():
    assert normalize(_skillup(), 1).invested_year is None


def test_founded_year():
    assert normalize(_edulearnpro(), 1).founded_year == 2018


def test_founded_year_none_when_missing():
    assert normalize(_skillup(), 1).founded_year is None


def test_logo_url():
    assert normalize(_edulearnpro(), 1).logo_url == "https://gsv.ventures/wp-content/uploads/logo-edulearnpro.png"


def test_logo_url_none_when_missing():
    raw = _edulearnpro()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


def test_founders():
    assert normalize(_edulearnpro(), 1).founders == ["Alice Smith", "Bob Jones"]


def test_founders_multiple():
    assert normalize(_learnpath(), 1).founders == ["Carol Davis", "Dan Evans", "Eve Foster"]


def test_founders_none_when_empty():
    assert normalize(_skillup(), 1).founders is None


def test_stage_year_none():
    assert normalize(_edulearnpro(), 1).stage_year is None


def test_ticker_symbol_none():
    assert normalize(_edulearnpro(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_edulearnpro(), 1).acquirer is None


def test_source_modified_none():
    assert normalize(_edulearnpro(), 1).source_modified is None
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
.venv/bin/python -m pytest tests/test_gsv_normalizer.py -v 2>&1 | head -10
```
Expected: `ImportError` — `normalizer` module not found.

- [ ] **Step 3: Implement normalizer**

Create `vc_crawler/crawlers/gsv_ventures/normalizer.py`:
```python
from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

PORTFOLIO_URL = "https://gsv.ventures/portfolio/"
_YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')
_NON_ALNUM_RE = re.compile(r'[^a-z0-9]+')


def normalize(raw: dict, company_id: int) -> Company:
    stage, invested_year = _parse_investment(raw.get("investment"))
    founders = raw.get("founders") or []
    sector = raw.get("sector")

    return Company(
        id=company_id,
        fund="gsv-ventures",
        name=raw.get("name", ""),
        slug=_slugify(raw.get("name", "")),
        fund_url=PORTFOLIO_URL,
        sectors=[sector] if sector else [],
        website=raw.get("website") or None,
        description=raw.get("description") or raw.get("tagline") or None,
        stage=stage,
        stage_year=None,
        founded_year=_parse_int(raw.get("founded_year_str")),
        invested_year=invested_year,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=founders if founders else None,
    )


def _slugify(name: str) -> str:
    return _NON_ALNUM_RE.sub("-", name.lower()).strip("-")


def _parse_investment(text: Optional[str]) -> tuple[Optional[str], Optional[int]]:
    if not text:
        return None, None
    parts = text.split(",", 1)
    stage = parts[0].strip() or None
    year: Optional[int] = None
    if len(parts) > 1:
        m = _YEAR_RE.search(parts[1])
        if m:
            year = int(m.group())
    return stage, year


def _parse_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    try:
        return int(text.strip())
    except ValueError:
        return None
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
.venv/bin/python -m pytest tests/test_gsv_normalizer.py -v
```
Expected: all tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/gsv_ventures/normalizer.py \
        tests/test_gsv_normalizer.py
git commit -m "feat: add GSV Ventures normalizer"
```

---

### Task 4: Crawler — TDD

**Files:**
- Create: `tests/test_gsv_crawler.py`
- Create: `vc_crawler/crawlers/gsv_ventures/crawler.py`

The crawler makes a single GET to `PORTFOLIO_URL`, delegates to `parse_portfolio_page`, and calls `normalize` for each raw record. All `workers` / `enrich` params are accepted but unused (single-stage).

- [ ] **Step 1: Write the failing tests**

`tests/test_gsv_crawler.py`:
```python
from pathlib import Path

from vc_crawler.crawlers.gsv_ventures.crawler import GSVCrawler
from vc_crawler.models import Company

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "gsv_ventures_portfolio.html"


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
    companies = GSVCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    assert len(GSVCrawler(_make_client()).run()) == 3


def test_sequential_ids():
    companies = GSVCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3]


def test_all_fund_gsv_ventures():
    companies = GSVCrawler(_make_client()).run()
    assert all(c.fund == "gsv-ventures" for c in companies)


def test_limit_truncates():
    companies = GSVCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = GSVCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    GSVCrawler(client).run()
    assert any("gsv.ventures/portfolio" in u for u in client.calls)


def test_enrich_false_accepted():
    companies = GSVCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 3


def test_workers_param_accepted():
    companies = GSVCrawler(_make_client()).run(workers=10)
    assert len(companies) == 3
```

- [ ] **Step 2: Run tests — confirm they fail**

```bash
.venv/bin/python -m pytest tests/test_gsv_crawler.py -v 2>&1 | head -10
```
Expected: `ImportError` — `crawler` module not found.

- [ ] **Step 3: Implement crawler**

Create `vc_crawler/crawlers/gsv_ventures/crawler.py`:
```python
from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company

from .normalizer import normalize
from .parser import PORTFOLIO_URL, parse_portfolio_page

log = logging.getLogger(__name__)


class GSVCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching GSV Ventures portfolio page ...")
        resp = self.client.get(PORTFOLIO_URL)
        raw_records = parse_portfolio_page(resp.text)
        log.info("Parsed %d companies", len(raw_records))
        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]
        if limit:
            companies = companies[:limit]
        return companies
```

- [ ] **Step 4: Run tests — confirm they pass**

```bash
.venv/bin/python -m pytest tests/test_gsv_crawler.py -v
```
Expected: all tests `PASSED`.

- [ ] **Step 5: Run the full test suite — confirm no regressions**

```bash
.venv/bin/python -m pytest -v
```
Expected: all tests `PASSED` (no regressions).

- [ ] **Step 6: Commit**

```bash
git add vc_crawler/crawlers/gsv_ventures/crawler.py \
        tests/test_gsv_crawler.py
git commit -m "feat: add GSVCrawler"
```

---

### Task 5: Register fund in CLI + integration test

**Files:**
- Modify: `vc_crawler/__main__.py`
- Modify: `tests/test_vc_main.py`

Add `"gsv-ventures"` to `_FUND_REGISTRY` and verify the CLI writes `companies.json` + `companies.csv` to `data/gsv-ventures/`.

- [ ] **Step 1: Write the failing integration test**

Append to `tests/test_vc_main.py`:
```python
def test_main_writes_gsv_ventures_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.gsv_ventures.crawler as gsv_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="gsv-ventures", name="EduLearn Pro",
                            slug="edulearn-pro",
                            fund_url="https://gsv.ventures/portfolio/")]
    monkeypatch.setattr(gsv_mod, "GSVCrawler", Fake)
    rc = cli.main(["--fund", "gsv-ventures", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "gsv-ventures" / "companies.json").exists()
    assert (tmp_path / "gsv-ventures" / "companies.csv").exists()
```

- [ ] **Step 2: Run test — confirm it fails**

```bash
.venv/bin/python -m pytest tests/test_vc_main.py::test_main_writes_gsv_ventures_outputs -v
```
Expected: `FAILED` — `argument --fund: invalid choice: 'gsv-ventures'`

- [ ] **Step 3: Register the fund**

In `vc_crawler/__main__.py`, add one line to `_FUND_REGISTRY`:
```python
_FUND_REGISTRY = {
    "sequoia": "vc_crawler.crawlers.sequoia.crawler.SequoiaCrawler",
    "a16z": "vc_crawler.crawlers.a16z.crawler.A16ZCrawler",
    "a16z-speedrun": "vc_crawler.crawlers.a16z_speedrun.crawler.SpeedrunCrawler",
    "owl-ventures": "vc_crawler.crawlers.owl_ventures.crawler.OwlCrawler",
    "reach-capital": "vc_crawler.crawlers.reach_capital.crawler.ReachCrawler",
    "gsv-ventures": "vc_crawler.crawlers.gsv_ventures.crawler.GSVCrawler",
}
```

- [ ] **Step 4: Run test — confirm it passes**

```bash
.venv/bin/python -m pytest tests/test_vc_main.py::test_main_writes_gsv_ventures_outputs -v
```
Expected: `PASSED`.

- [ ] **Step 5: Run the full test suite**

```bash
.venv/bin/python -m pytest -v
```
Expected: all tests `PASSED`.

- [ ] **Step 6: Commit**

```bash
git add vc_crawler/__main__.py tests/test_vc_main.py
git commit -m "feat: register gsv-ventures in CLI"
```

---

### Task 6: Update README

**Files:**
- Modify: `README.md`

Four sections need updating: fund table, usage examples, output files list, "All Options" flag description, output schema `fund` field, and a new "How It Works → GSV Ventures" section.

- [ ] **Step 1: Add GSV Ventures to the fund table**

In the supported funds table, add a row after Reach Capital:
```markdown
| [GSV Ventures](https://gsv.ventures/portfolio/) | Static HTML (single request) | ~87 |
```

- [ ] **Step 2: Add usage example**

In the Usage section, add after the Reach Capital example:
```bash
# Crawl GSV Ventures portfolio (~87 companies, single static-HTML request)
.venv/bin/python -m vc_crawler --fund gsv-ventures
```

- [ ] **Step 3: Add output file path**

In the output files list, add:
```
- `data/gsv-ventures/companies.json` / `data/gsv-ventures/companies.csv`
```

- [ ] **Step 4: Update --fund flag description**

In the "All Options" table, extend the `--fund` choices:
```
`--fund {sequoia,a16z,a16z-speedrun,owl-ventures,reach-capital,gsv-ventures}`
```

- [ ] **Step 5: Update output schema fund field**

In the Output Schema table, extend the `fund` field description:
```
`"sequoia"`, `"a16z"`, `"a16z-speedrun"`, `"owl-ventures"`, `"reach-capital"`, or `"gsv-ventures"`
```

- [ ] **Step 6: Add "How It Works → GSV Ventures" section**

After the Reach Capital section in "How It Works", add:
```markdown
### GSV Ventures
Single HTTP request to `https://gsv.ventures/portfolio/`. All ~87 portfolio companies are fully embedded in the static HTML as `div.c-grid--item` elements — no JS rendering required. Each card contains the company name, logo (`img.lazyload[data-src]`), tagline (`h2`), optional description (`p`), website ("Learn more" link), and a `ul.company-info` aside with investment round, year founded, segment, and founders/leadership.
```

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -m "docs: add gsv-ventures to README"
```
