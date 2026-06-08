# Learn Capital Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `learn-capital` fund crawler that extracts 78 portfolio companies from learn.vc/ventures and exports them to JSON/CSV.

**Architecture:** Single HTTP GET to `https://learn.vc/ventures`; all company data is embedded in the page as a `__NEXT_DATA__` JSON blob (Next.js + Prismic CMS). `parser.py` extracts the `props.pageProps.ventures` array, `normalizer.py` maps Prismic fields → `Company`, and `LearnCrawler` wires them together following the exact same pattern as `GSVCrawler`.

**Tech Stack:** Python 3.10, requests (via `PoliteClient`), `re` + `json` (stdlib — no BeautifulSoup needed), pytest.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `vc_crawler/crawlers/learn_capital/__init__.py` | Package marker (empty) |
| Create | `vc_crawler/crawlers/learn_capital/parser.py` | Extract ventures list from `__NEXT_DATA__` JSON |
| Create | `vc_crawler/crawlers/learn_capital/normalizer.py` | Map raw Prismic dict → `Company` |
| Create | `vc_crawler/crawlers/learn_capital/crawler.py` | `LearnCrawler(BaseCrawler)` |
| Modify | `vc_crawler/__main__.py` | Register `"learn-capital"` in `_FUND_REGISTRY` |
| Create | `tests/fixtures/learn_capital_ventures.html` | Minimal HTML fixture with 3 companies |
| Create | `tests/test_learn_capital_parser.py` | Parser unit tests |
| Create | `tests/test_learn_capital_normalizer.py` | Normalizer unit tests |
| Create | `tests/test_learn_capital_crawler.py` | Crawler integration tests |
| Modify | `tests/test_vc_main.py` | Add `test_main_writes_learn_capital_outputs` |
| Modify | `README.md` | Add learn-capital row to fund table + usage examples |

---

## Task 1: HTML fixture

**Files:**
- Create: `tests/fixtures/learn_capital_ventures.html`

- [ ] **Step 1: Create the fixture file**

The fixture must be a minimal but representative HTML page with three companies covering all code paths:
- Company A (**Edify Academy**): education tag, active (not acquired/public), has description, no founders
- Company B (**TalentBridge**): community tag, active, has founders (`"Alice Kim, Bob Chen"`), no description → headline fallback
- Company C (**LearnCo**): finance tag, `public: true` → stage `"Public"`, has description and founders

Write `tests/fixtures/learn_capital_ventures.html`:

```html
<!DOCTYPE html>
<html lang="en-us">
<head><title>Learn | Ventures</title></head>
<body>
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "venturePage": {"data": {"body": []}},
      "ventures": [
        {
          "id": "aaa111",
          "uid": null,
          "url": "/ventures",
          "type": "ventures",
          "tags": ["education"],
          "first_publication_date": "2022-01-18T21:50:00+0000",
          "last_publication_date": "2025-06-01T10:00:00+0000",
          "data": {
            "name": [{"type": "heading1", "text": "Edify Academy", "spans": []}],
            "color_logo": {
              "dimensions": {"width": 400, "height": 100},
              "alt": null,
              "copyright": null,
              "url": "https://images.prismic.io/learn-site/edify-logo.png"
            },
            "headline": [{"type": "heading3", "text": "Personalizing education for every learner.", "spans": []}],
            "description": [{"type": "paragraph", "text": "An adaptive learning platform for K-12 students.", "spans": []}],
            "founders": [],
            "visit": {"link_type": "Web", "url": "https://edify.academy"},
            "acquired": false,
            "public": false
          }
        },
        {
          "id": "bbb222",
          "uid": null,
          "url": "/ventures",
          "type": "ventures",
          "tags": ["community"],
          "first_publication_date": "2022-02-01T12:00:00+0000",
          "last_publication_date": "2025-05-15T08:00:00+0000",
          "data": {
            "name": [{"type": "heading1", "text": "TalentBridge", "spans": []}],
            "color_logo": {
              "dimensions": {"width": 300, "height": 80},
              "alt": null,
              "copyright": null,
              "url": "https://images.prismic.io/learn-site/tb-logo.png"
            },
            "headline": [{"type": "heading3", "text": "Bridging the global talent gap.", "spans": []}],
            "description": [{"type": "paragraph", "text": "", "spans": []}],
            "founders": [{"type": "heading6", "text": "Alice Kim, Bob Chen", "spans": []}],
            "visit": {"link_type": "Web", "url": "https://talentbridge.io"},
            "acquired": false,
            "public": false
          }
        },
        {
          "id": "ccc333",
          "uid": null,
          "url": "/ventures",
          "type": "ventures",
          "tags": ["finance"],
          "first_publication_date": "2022-03-10T09:00:00+0000",
          "last_publication_date": "2025-04-20T14:00:00+0000",
          "data": {
            "name": [{"type": "heading1", "text": "LearnCo", "spans": []}],
            "color_logo": {
              "dimensions": {"width": 500, "height": 150},
              "alt": null,
              "copyright": null,
              "url": "https://images.prismic.io/learn-site/learnco-logo.png"
            },
            "headline": [{"type": "heading3", "text": "Reimagining student financing.", "spans": []}],
            "description": [{"type": "paragraph", "text": "Innovative student-centric lending products.", "spans": []}],
            "founders": [{"type": "heading6", "text": "Carlos Ruiz", "spans": []}],
            "visit": {"link_type": "Web", "url": "https://learnco.com"},
            "acquired": false,
            "public": true
          }
        }
      ]
    }
  },
  "page": "/ventures",
  "query": {},
  "buildId": "test"
}
</script>
</body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add tests/fixtures/learn_capital_ventures.html
git commit -m "test: add learn_capital_ventures.html fixture"
```

---

## Task 2: Parser — tests first

**Files:**
- Create: `tests/test_learn_capital_parser.py`
- Create: `vc_crawler/crawlers/learn_capital/__init__.py` (empty)
- Create: `vc_crawler/crawlers/learn_capital/parser.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_learn_capital_parser.py`:

```python
from pathlib import Path
from vc_crawler.crawlers.learn_capital.parser import (
    PORTFOLIO_URL,
    parse_ventures_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "learn_capital_ventures.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://learn.vc/ventures"


def test_returns_list_of_dicts():
    result = parse_ventures_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_three_companies():
    assert len(parse_ventures_page(FIXTURE)) == 3


def test_empty_page_returns_empty_list():
    assert parse_ventures_page("<html><body></body></html>") == []


def test_missing_ventures_key_returns_empty_list():
    import json
    html = '<script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{}}}</script>'
    assert parse_ventures_page(html) == []


# --- Company A: Edify Academy (index 0) ---

def test_company_a_name():
    assert parse_ventures_page(FIXTURE)[0]["name"] == "Edify Academy"


def test_company_a_description():
    assert parse_ventures_page(FIXTURE)[0]["description"] == "An adaptive learning platform for K-12 students."


def test_company_a_headline():
    assert parse_ventures_page(FIXTURE)[0]["headline"] == "Personalizing education for every learner."


def test_company_a_website():
    assert parse_ventures_page(FIXTURE)[0]["website"] == "https://edify.academy"


def test_company_a_logo_url():
    assert parse_ventures_page(FIXTURE)[0]["logo_url"] == "https://images.prismic.io/learn-site/edify-logo.png"


def test_company_a_founders_text_empty():
    assert parse_ventures_page(FIXTURE)[0]["founders_text"] == ""


def test_company_a_tags():
    assert parse_ventures_page(FIXTURE)[0]["tags"] == ["education"]


def test_company_a_acquired_false():
    assert parse_ventures_page(FIXTURE)[0]["acquired"] is False


def test_company_a_public_false():
    assert parse_ventures_page(FIXTURE)[0]["public"] is False


# --- Company B: TalentBridge (index 1) — founders present, empty description ---

def test_company_b_name():
    assert parse_ventures_page(FIXTURE)[1]["name"] == "TalentBridge"


def test_company_b_description_empty():
    assert parse_ventures_page(FIXTURE)[1]["description"] is None


def test_company_b_headline():
    assert parse_ventures_page(FIXTURE)[1]["headline"] == "Bridging the global talent gap."


def test_company_b_founders_text():
    assert parse_ventures_page(FIXTURE)[1]["founders_text"] == "Alice Kim, Bob Chen"


def test_company_b_tags():
    assert parse_ventures_page(FIXTURE)[1]["tags"] == ["community"]


# --- Company C: LearnCo (index 2) — public: true ---

def test_company_c_name():
    assert parse_ventures_page(FIXTURE)[2]["name"] == "LearnCo"


def test_company_c_public_true():
    assert parse_ventures_page(FIXTURE)[2]["public"] is True


def test_company_c_acquired_false():
    assert parse_ventures_page(FIXTURE)[2]["acquired"] is False


def test_company_c_tags():
    assert parse_ventures_page(FIXTURE)[2]["tags"] == ["finance"]


def test_company_c_founders_text():
    assert parse_ventures_page(FIXTURE)[2]["founders_text"] == "Carlos Ruiz"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_learn_capital_parser.py -v 2>&1 | head -30
```

Expected: `ModuleNotFoundError: No module named 'vc_crawler.crawlers.learn_capital'`

- [ ] **Step 3: Create the package and implement parser**

Create `vc_crawler/crawlers/learn_capital/__init__.py` (empty file).

Create `vc_crawler/crawlers/learn_capital/parser.py`:

```python
from __future__ import annotations

import json
import re

PORTFOLIO_URL = "https://learn.vc/ventures"
_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def parse_ventures_page(html: str) -> list[dict]:
    m = _NEXT_DATA_RE.search(html)
    if not m:
        return []
    data = json.loads(m.group(1))
    ventures = data.get("props", {}).get("pageProps", {}).get("ventures", [])
    return [_extract(v) for v in ventures]


def _extract(v: dict) -> dict:
    d = v.get("data", {})

    name_nodes = d.get("name") or []
    name = name_nodes[0].get("text", "") if name_nodes else ""

    desc_nodes = d.get("description") or []
    description_text = desc_nodes[0].get("text", "") if desc_nodes else ""

    headline_nodes = d.get("headline") or []
    headline_text = headline_nodes[0].get("text", "") if headline_nodes else ""

    visit = d.get("visit") or {}
    website = visit.get("url") if visit.get("link_type") == "Web" else None

    color_logo = d.get("color_logo") or {}
    logo_url = color_logo.get("url") or None

    founders_nodes = d.get("founders") or []
    founders_text = founders_nodes[0].get("text", "") if founders_nodes else ""

    return {
        "name": name,
        "description": description_text or None,
        "headline": headline_text or None,
        "website": website,
        "logo_url": logo_url,
        "founders_text": founders_text,
        "tags": v.get("tags", []),
        "acquired": bool(d.get("acquired", False)),
        "public": bool(d.get("public", False)),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_learn_capital_parser.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/learn_capital/__init__.py \
        vc_crawler/crawlers/learn_capital/parser.py \
        tests/test_learn_capital_parser.py
git commit -m "feat: add LearnCapital parser (extracts __NEXT_DATA__ JSON)"
```

---

## Task 3: Normalizer — tests first

**Files:**
- Create: `tests/test_learn_capital_normalizer.py`
- Create: `vc_crawler/crawlers/learn_capital/normalizer.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_learn_capital_normalizer.py`:

```python
from vc_crawler.crawlers.learn_capital.normalizer import normalize, PORTFOLIO_URL
from vc_crawler.models import Company


def _edify() -> dict:
    return {
        "name": "Edify Academy",
        "description": "An adaptive learning platform for K-12 students.",
        "headline": "Personalizing education for every learner.",
        "website": "https://edify.academy",
        "logo_url": "https://images.prismic.io/learn-site/edify-logo.png",
        "founders_text": "",
        "tags": ["education"],
        "acquired": False,
        "public": False,
    }


def _talentbridge() -> dict:
    return {
        "name": "TalentBridge",
        "description": None,
        "headline": "Bridging the global talent gap.",
        "website": "https://talentbridge.io",
        "logo_url": "https://images.prismic.io/learn-site/tb-logo.png",
        "founders_text": "Alice Kim, Bob Chen",
        "tags": ["community"],
        "acquired": False,
        "public": False,
    }


def _learnco() -> dict:
    return {
        "name": "LearnCo",
        "description": "Innovative student-centric lending products.",
        "headline": "Reimagining student financing.",
        "website": "https://learnco.com",
        "logo_url": "https://images.prismic.io/learn-site/learnco-logo.png",
        "founders_text": "Carlos Ruiz",
        "tags": ["finance"],
        "acquired": False,
        "public": True,
    }


def test_returns_company_instance():
    assert isinstance(normalize(_edify(), 1), Company)


def test_fund_is_learn_capital():
    assert normalize(_edify(), 1).fund == "learn-capital"


def test_id_assigned():
    assert normalize(_edify(), 42).id == 42


def test_name():
    assert normalize(_edify(), 1).name == "Edify Academy"


def test_slug():
    assert normalize(_edify(), 1).slug == "edify-academy"


def test_slug_simple():
    assert normalize(_talentbridge(), 1).slug == "talentbridge"


def test_fund_url_constant():
    assert normalize(_edify(), 1).fund_url == PORTFOLIO_URL


def test_fund_url_value():
    assert normalize(_edify(), 1).fund_url == "https://learn.vc/ventures"


def test_sectors_from_tags():
    assert normalize(_edify(), 1).sectors == ["education"]


def test_sectors_community():
    assert normalize(_talentbridge(), 1).sectors == ["community"]


def test_sectors_finance():
    assert normalize(_learnco(), 1).sectors == ["finance"]


def test_website():
    assert normalize(_edify(), 1).website == "https://edify.academy"


def test_website_none_when_missing():
    raw = _edify()
    raw["website"] = None
    assert normalize(raw, 1).website is None


def test_description_uses_description_field():
    assert normalize(_edify(), 1).description == "An adaptive learning platform for K-12 students."


def test_description_falls_back_to_headline():
    assert normalize(_talentbridge(), 1).description == "Bridging the global talent gap."


def test_description_none_when_both_missing():
    raw = _edify()
    raw["description"] = None
    raw["headline"] = None
    assert normalize(raw, 1).description is None


def test_logo_url():
    assert normalize(_edify(), 1).logo_url == "https://images.prismic.io/learn-site/edify-logo.png"


def test_logo_url_none_when_missing():
    raw = _edify()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


def test_stage_none_for_active():
    assert normalize(_edify(), 1).stage is None


def test_stage_public():
    assert normalize(_learnco(), 1).stage == "Public"


def test_stage_acquired():
    raw = _edify()
    raw["acquired"] = True
    assert normalize(raw, 1).stage == "Acquired"


def test_stage_acquired_takes_priority_over_public():
    raw = _edify()
    raw["acquired"] = True
    raw["public"] = True
    assert normalize(raw, 1).stage == "Acquired"


def test_founders_none_when_empty():
    assert normalize(_edify(), 1).founders is None


def test_founders_single():
    assert normalize(_learnco(), 1).founders == ["Carlos Ruiz"]


def test_founders_multiple():
    assert normalize(_talentbridge(), 1).founders == ["Alice Kim", "Bob Chen"]


def test_founded_year_none():
    assert normalize(_edify(), 1).founded_year is None


def test_invested_year_none():
    assert normalize(_edify(), 1).invested_year is None


def test_stage_year_none():
    assert normalize(_edify(), 1).stage_year is None


def test_ticker_symbol_none():
    assert normalize(_edify(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_edify(), 1).acquirer is None


def test_source_modified_none():
    assert normalize(_edify(), 1).source_modified is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_learn_capital_normalizer.py -v 2>&1 | head -20
```

Expected: `ModuleNotFoundError` or `ImportError` for `normalizer`.

- [ ] **Step 3: Implement normalizer**

Create `vc_crawler/crawlers/learn_capital/normalizer.py`:

```python
from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

PORTFOLIO_URL = "https://learn.vc/ventures"
_NON_ALNUM_RE = re.compile(r'[^a-z0-9]+')


def normalize(raw: dict, company_id: int) -> Company:
    founders = _parse_founders(raw.get("founders_text", ""))
    stage = _parse_stage(raw)

    return Company(
        id=company_id,
        fund="learn-capital",
        name=raw.get("name", ""),
        slug=_slugify(raw.get("name", "")),
        fund_url=PORTFOLIO_URL,
        sectors=raw.get("tags", []),
        website=raw.get("website") or None,
        description=raw.get("description") or raw.get("headline") or None,
        stage=stage,
        stage_year=None,
        founded_year=None,
        invested_year=None,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=founders if founders else None,
    )


def _parse_stage(raw: dict) -> Optional[str]:
    if raw.get("acquired"):
        return "Acquired"
    if raw.get("public"):
        return "Public"
    return None


def _parse_founders(text: str) -> list[str]:
    if not text:
        return []
    return [f.strip() for f in text.split(",") if f.strip()]


def _slugify(name: str) -> str:
    return _NON_ALNUM_RE.sub("-", name.lower()).strip("-")
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_learn_capital_normalizer.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/learn_capital/normalizer.py \
        tests/test_learn_capital_normalizer.py
git commit -m "feat: add LearnCapital normalizer"
```

---

## Task 4: Crawler — tests first

**Files:**
- Create: `tests/test_learn_capital_crawler.py`
- Create: `vc_crawler/crawlers/learn_capital/crawler.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_learn_capital_crawler.py`:

```python
from pathlib import Path

from vc_crawler.crawlers.learn_capital.crawler import LearnCrawler
from vc_crawler.models import Company

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "learn_capital_ventures.html"


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
    companies = LearnCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    assert len(LearnCrawler(_make_client()).run()) == 3


def test_sequential_ids():
    companies = LearnCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3]


def test_all_fund_learn_capital():
    companies = LearnCrawler(_make_client()).run()
    assert all(c.fund == "learn-capital" for c in companies)


def test_limit_truncates():
    companies = LearnCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = LearnCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    LearnCrawler(client).run()
    assert any("learn.vc/ventures" in u for u in client.calls)


def test_enrich_false_accepted():
    companies = LearnCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 3


def test_workers_param_accepted():
    companies = LearnCrawler(_make_client()).run(workers=10)
    assert len(companies) == 3
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_learn_capital_crawler.py -v 2>&1 | head -20
```

Expected: `ImportError` for `LearnCrawler`.

- [ ] **Step 3: Implement crawler**

Create `vc_crawler/crawlers/learn_capital/crawler.py`:

```python
from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company

from .normalizer import normalize
from .parser import PORTFOLIO_URL, parse_ventures_page

log = logging.getLogger(__name__)


class LearnCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching Learn Capital ventures page ...")
        resp = self.client.get(PORTFOLIO_URL)
        raw_records = parse_ventures_page(resp.text)
        log.info("Parsed %d companies", len(raw_records))
        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]
        if limit:
            companies = companies[:limit]
        return companies
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_learn_capital_crawler.py -v
```

Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/learn_capital/crawler.py \
        tests/test_learn_capital_crawler.py
git commit -m "feat: add LearnCrawler"
```

---

## Task 5: Register in CLI + main test

**Files:**
- Modify: `vc_crawler/__main__.py`
- Modify: `tests/test_vc_main.py`

- [ ] **Step 1: Write the failing CLI test**

Open `tests/test_vc_main.py` and append this test at the end of the file:

```python
def test_main_writes_learn_capital_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.learn_capital.crawler as lc_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="learn-capital", name="Edify Academy",
                            slug="edify-academy",
                            fund_url="https://learn.vc/ventures")]
    monkeypatch.setattr(lc_mod, "LearnCrawler", Fake)
    rc = cli.main(["--fund", "learn-capital", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "learn-capital" / "companies.json").exists()
    assert (tmp_path / "learn-capital" / "companies.csv").exists()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/python -m pytest tests/test_vc_main.py::test_main_writes_learn_capital_outputs -v
```

Expected: `SystemExit` or `argparse` error — `"learn-capital"` is not yet a valid `--fund` choice.

- [ ] **Step 3: Register learn-capital in CLI**

Edit `vc_crawler/__main__.py`. In `_FUND_REGISTRY`, add the new entry after `"gsv-ventures"`:

```python
_FUND_REGISTRY = {
    "sequoia": "vc_crawler.crawlers.sequoia.crawler.SequoiaCrawler",
    "a16z": "vc_crawler.crawlers.a16z.crawler.A16ZCrawler",
    "a16z-speedrun": "vc_crawler.crawlers.a16z_speedrun.crawler.SpeedrunCrawler",
    "owl-ventures": "vc_crawler.crawlers.owl_ventures.crawler.OwlCrawler",
    "reach-capital": "vc_crawler.crawlers.reach_capital.crawler.ReachCrawler",
    "gsv-ventures": "vc_crawler.crawlers.gsv_ventures.crawler.GSVCrawler",
    "learn-capital": "vc_crawler.crawlers.learn_capital.crawler.LearnCrawler",
}
```

- [ ] **Step 4: Run all tests**

```bash
.venv/bin/python -m pytest -v
```

Expected: all tests PASS. Verify no regressions.

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/__main__.py tests/test_vc_main.py
git commit -m "feat: register learn-capital in CLI"
```

---

## Task 6: Update README

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add fund row to the supported-funds table**

In `README.md`, add a new row to the table after the GSV Ventures row:

```markdown
| [Learn Capital](https://learn.vc/ventures) | Next.js `__NEXT_DATA__` JSON (single request) | ~78 |
```

- [ ] **Step 2: Add usage example**

In the Usage section, add after the GSV example:

```markdown
# Crawl Learn Capital portfolio (~78 companies, single Next.js page request)
.venv/bin/python -m vc_crawler --fund learn-capital
```

- [ ] **Step 3: Add output path**

In the "Output files" list, add:
```markdown
- `data/learn-capital/companies.json` / `data/learn-capital/companies.csv`
```

- [ ] **Step 4: Update the --fund flag description**

In the "All Options" table, update the `--fund` flag to include `learn-capital`:

```
| `--fund {sequoia,a16z,a16z-speedrun,owl-ventures,reach-capital,gsv-ventures,learn-capital}` | *(required)* | Which fund to crawl |
```

- [ ] **Step 5: Add fund entry to the `fund` field description in the Output Schema table**

Update the `fund` row description to include `"learn-capital"`.

- [ ] **Step 6: Add How It Works section for Learn Capital**

After the GSV Ventures section in "How It Works", add:

```markdown
### Learn Capital
Single HTTP request to `https://learn.vc/ventures`. The site is built with Next.js + Prismic CMS — all ~78 portfolio companies are embedded in the page as `props.pageProps.ventures` inside a `<script id="__NEXT_DATA__">` JSON blob. No JS rendering required. Each venture record contains name, logo URL (`color_logo.url`), description, headline, website (`visit.url`), sector tags, founder names, and acquisition/IPO status flags.
```

- [ ] **Step 7: Run full test suite to confirm nothing broken**

```bash
.venv/bin/python -m pytest -v
```

Expected: all tests PASS.

- [ ] **Step 8: Commit**

```bash
git add README.md
git commit -m "docs: add learn-capital to README"
```

---

## Task 7: Release commit

- [ ] **Step 1: Manual smoke test against live site**

```bash
.venv/bin/python -m vc_crawler --fund learn-capital --limit 5 --format json --verbose
```

Expected output:
```
INFO vc_crawler.crawlers.learn_capital.crawler: Fetching Learn Capital ventures page ...
INFO vc_crawler.crawlers.learn_capital.crawler: Parsed 78 companies
INFO vc_crawler: Done: 5 companies from learn-capital
INFO vc_crawler: Wrote data/learn-capital/companies.json
```

Verify `data/learn-capital/companies.json` contains 5 valid company objects.

- [ ] **Step 2: Run full crawl**

```bash
.venv/bin/python -m vc_crawler --fund learn-capital --format both
```

Verify `data/learn-capital/companies.json` and `data/learn-capital/companies.csv` exist and contain ~78 companies.

- [ ] **Step 3: Release commit**

```bash
git add data/learn-capital/
git commit -m "release: v2.5.0 Learn Capital portfolio data"
```
