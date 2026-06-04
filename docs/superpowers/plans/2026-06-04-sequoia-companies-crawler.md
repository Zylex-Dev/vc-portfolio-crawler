# Sequoia Companies Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python crawler that collects all ~490 companies from Sequoia Capital's
Our Companies page and exports them as JSON + CSV.

**Architecture:** Enumerate the full company index from the WordPress REST API
(`/wp-json/wp/v2/company`, paginated), resolve sector names from the categories
taxonomy, then enrich each company by fetching its server-rendered detail page
(`/companies/<slug>/`) over plain HTTP and parsing it with BeautifulSoup. Small
single-responsibility modules, each unit-tested over fixtures.

**Tech Stack:** Python 3.10, `requests`, `beautifulsoup4` + `lxml`, `pytest`.

**Spec:** `docs/superpowers/specs/2026-06-04-sequoia-companies-crawler-design.md`

---

## Environment & Network Notes

- The local Bash sandbox has **no outbound network**. Two steps therefore require
  network and must be run either by the user via `! <cmd>` in-session, or with the
  Bash sandbox disabled:
  1. **Task 0** — `pip install` of dependencies.
  2. **Task 11** — live reconciliation + end-to-end crawl.
- Every other task (the TDD unit tests) runs fully **offline** against fixtures once
  dependencies are installed.

## File Structure

```
sequoia_crawler/
├── __init__.py          # package marker
├── http_client.py       # build_session(), PoliteClient (UA, retry, timeout, rate limit)
├── api.py               # fetch_categories(), iter_companies(), to_company()
├── detail_parser.py     # parse_detail(html) -> dict   (pure function)
├── sitemap.py           # fetch_company_slugs() for completeness cross-check
├── enrich.py            # enrich_company(), enrich_all() (thread pool)
├── models.py            # Company dataclass + CSV_FIELDS
├── export.py            # write_json(), write_csv()
└── __main__.py          # CLI: build_companies(), main()
tests/
├── __init__.py
├── fixtures/
│   └── admob_like.html  # synthetic fixture mirroring a detail page
├── test_models.py
├── test_http_client.py
├── test_api.py
├── test_detail_parser.py
├── test_sitemap.py
├── test_enrich.py
├── test_export.py
└── test_main.py
requirements.txt
README.md
.gitignore
output/                  # crawl results (git-ignored contents)
```

---

## Task 0: Project scaffold & dependencies

**Files:**
- Create: `requirements.txt`, `.gitignore`, `sequoia_crawler/__init__.py`, `tests/__init__.py`

- [ ] **Step 1: Create `requirements.txt`**

```
requests>=2.31
beautifulsoup4>=4.12
lxml>=5.0
pytest>=8.0
```

- [ ] **Step 2: Create `.gitignore`**

```
.venv/
__pycache__/
*.pyc
output/*.json
output/*.csv
tests/fixtures/*_real.html
```

- [ ] **Step 3: Create empty package markers**

Create `sequoia_crawler/__init__.py`:
```python
"""Sequoia Capital portfolio companies crawler."""
```
Create `tests/__init__.py`:
```python
```

- [ ] **Step 4: Create venv and install deps** (REQUIRES NETWORK)

Run: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
Expected: installs requests, beautifulsoup4, lxml, pytest successfully.

- [ ] **Step 5: Verify imports**

Run: `.venv/bin/python -c "import requests, bs4, lxml; print('ok')"`
Expected: prints `ok`

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore sequoia_crawler/__init__.py tests/__init__.py
git commit -m "chore: project scaffold and dependencies"
```

---

## Task 1: Company model

**Files:**
- Create: `sequoia_crawler/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_models.py
from sequoia_crawler.models import Company, CSV_FIELDS


def _company():
    return Company(
        id=1, name="AdMob", slug="admob",
        sequoia_url="https://sequoiacap.com/companies/admob/",
        sectors=["GTM", "AI"], website="https://www.admob.com",
    )


def test_to_dict_keeps_sectors_as_list():
    d = _company().to_dict()
    assert d["name"] == "AdMob"
    assert d["sectors"] == ["GTM", "AI"]
    assert d["status"] is None


def test_to_csv_row_joins_sectors():
    row = _company().to_csv_row()
    assert row["sectors"] == "GTM;AI"
    assert row["website"] == "https://www.admob.com"


def test_csv_fields_match_dataclass_keys():
    assert set(CSV_FIELDS) == set(_company().to_dict().keys())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_models.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sequoia_crawler.models'`

- [ ] **Step 3: Write minimal implementation**

```python
# sequoia_crawler/models.py
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Company:
    id: int
    name: str
    slug: str
    sequoia_url: str
    sectors: list[str] = field(default_factory=list)
    website: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    status_year: Optional[int] = None
    founded_year: Optional[int] = None
    partnered_year: Optional[int] = None
    logo_url: Optional[str] = None
    source_modified: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_csv_row(self) -> dict:
        row = asdict(self)
        row["sectors"] = ";".join(self.sectors)
        return row


CSV_FIELDS = [
    "id", "name", "slug", "sequoia_url", "sectors", "website",
    "description", "status", "status_year", "founded_year",
    "partnered_year", "logo_url", "source_modified",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_models.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add sequoia_crawler/models.py tests/test_models.py
git commit -m "feat: Company model with JSON/CSV serialization"
```

---

## Task 2: HTTP client (session + polite rate-limited GET)

**Files:**
- Create: `sequoia_crawler/http_client.py`
- Test: `tests/test_http_client.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_http_client.py
import pytest

from sequoia_crawler.http_client import build_session, PoliteClient


class FakeResp:
    def __init__(self, status=200):
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, resp):
        self.resp = resp
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.resp


def test_build_session_sets_user_agent():
    s = build_session(user_agent="x/1.0")
    assert s.headers["User-Agent"] == "x/1.0"


def test_build_session_mounts_retry_adapter():
    s = build_session(total_retries=4)
    adapter = s.get_adapter("https://example.com")
    assert adapter.max_retries.total == 4


def test_polite_get_delegates_and_sets_timeout():
    resp = FakeResp(200)
    sess = FakeSession(resp)
    client = PoliteClient(session=sess, delay=0, timeout=15)
    out = client.get("https://example.com", params={"a": 1})
    assert out is resp
    url, kwargs = sess.calls[0]
    assert url == "https://example.com"
    assert kwargs["timeout"] == 15
    assert kwargs["params"] == {"a": 1}


def test_polite_get_raises_on_http_error():
    client = PoliteClient(session=FakeSession(FakeResp(500)), delay=0)
    with pytest.raises(RuntimeError):
        client.get("https://example.com")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_http_client.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sequoia_crawler.http_client'`

- [ ] **Step 3: Write minimal implementation**

```python
# sequoia_crawler/http_client.py
from __future__ import annotations

import threading
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_USER_AGENT = "sequoia-companies-crawler/1.0 (research; +https://sequoiacap.com)"
DEFAULT_TIMEOUT = 30


def build_session(
    user_agent: str = DEFAULT_USER_AGENT,
    total_retries: int = 4,
    backoff_factor: float = 0.5,
) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent})
    retry = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


class PoliteClient:
    """Wraps a Session and enforces a minimum spacing between request starts.

    Thread-safe: the spacing gate is guarded by a lock so a shared client can be
    used from a thread pool while still rate-limiting overall request starts.
    """

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        delay: float = 0.2,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.session = session or build_session()
        self.delay = delay
        self.timeout = timeout
        self._lock = threading.Lock()
        self._next_allowed = 0.0

    def _throttle(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self._next_allowed - now
            if wait > 0:
                time.sleep(wait)
                now = time.monotonic()
            self._next_allowed = now + self.delay

    def get(self, url: str, **kwargs) -> requests.Response:
        if self.delay:
            self._throttle()
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.get(url, **kwargs)
        resp.raise_for_status()
        return resp
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_http_client.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add sequoia_crawler/http_client.py tests/test_http_client.py
git commit -m "feat: polite retrying HTTP client"
```

---

## Task 3: REST API client (categories + company index)

**Files:**
- Create: `sequoia_crawler/api.py`
- Test: `tests/test_api.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_api.py
from sequoia_crawler.api import fetch_categories, iter_companies, to_company


class FakeResp:
    def __init__(self, payload, headers=None):
        self._payload = payload
        self.headers = headers or {}

    def json(self):
        return self._payload


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params=None, **kwargs):
        self.calls.append((url, params))
        return self.responses.pop(0)


def test_fetch_categories_builds_id_name_map():
    resp = FakeResp(
        [{"id": 189, "name": "AI"}, {"id": 196, "name": "Fintech"}],
        headers={"X-WP-TotalPages": "1"},
    )
    mapping = fetch_categories(FakeClient([resp]))
    assert mapping == {189: "AI", 196: "Fintech"}


def test_iter_companies_paginates_via_total_pages_header():
    page1 = FakeResp([{"id": 1}, {"id": 2}], headers={"X-WP-TotalPages": "2"})
    page2 = FakeResp([{"id": 3}], headers={"X-WP-TotalPages": "2"})
    client = FakeClient([page1, page2])
    ids = [c["id"] for c in iter_companies(client)]
    assert ids == [1, 2, 3]
    assert len(client.calls) == 2


def test_to_company_maps_fields_and_resolves_sectors():
    raw = {
        "id": 10, "slug": "admob",
        "link": "https://sequoiacap.com/companies/admob/",
        "title": {"rendered": "AdMob &amp; Co"},
        "categories": [186, 1],
        "modified": "2026-06-02T21:10:47",
    }
    c = to_company(raw, {186: "GTM", 1: "Uncategorized"})
    assert c.name == "AdMob & Co"          # HTML entities decoded
    assert c.slug == "admob"
    assert c.sequoia_url == "https://sequoiacap.com/companies/admob/"
    assert c.sectors == ["GTM"]            # "Uncategorized" dropped
    assert c.source_modified == "2026-06-02T21:10:47"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_api.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sequoia_crawler.api'`

- [ ] **Step 3: Write minimal implementation**

```python
# sequoia_crawler/api.py
from __future__ import annotations

import html
from typing import Iterator

from .models import Company

BASE = "https://sequoiacap.com/wp-json/wp/v2"
_DROP_SECTORS = {"Uncategorized"}


def _paginate(client, url: str, params: dict) -> Iterator[dict]:
    page = 1
    while True:
        resp = client.get(url, params={**params, "page": page})
        items = resp.json()
        if not items:
            break
        for item in items:
            yield item
        total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break
        page += 1


def fetch_categories(client, base: str = BASE) -> dict[int, str]:
    """Return {term_id: sector_name} for the company category taxonomy."""
    mapping: dict[int, str] = {}
    for term in _paginate(client, f"{base}/categories", {"per_page": 100}):
        mapping[term["id"]] = term["name"]
    return mapping


def iter_companies(client, base: str = BASE) -> Iterator[dict]:
    """Yield raw company JSON objects across all pages."""
    yield from _paginate(
        client,
        f"{base}/company",
        {"per_page": 100, "orderby": "title", "order": "asc"},
    )


def to_company(raw: dict, sectors_map: dict[int, str]) -> Company:
    sectors = [
        sectors_map[cid]
        for cid in raw.get("categories", [])
        if cid in sectors_map and sectors_map[cid] not in _DROP_SECTORS
    ]
    return Company(
        id=raw["id"],
        name=html.unescape(raw["title"]["rendered"]).strip(),
        slug=raw["slug"],
        sequoia_url=raw["link"],
        sectors=sectors,
        source_modified=raw.get("modified"),
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_api.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add sequoia_crawler/api.py tests/test_api.py
git commit -m "feat: WordPress REST API client for company index"
```

---

## Task 4: Detail-page parser

**Files:**
- Create: `sequoia_crawler/detail_parser.py`, `tests/fixtures/admob_like.html`
- Test: `tests/test_detail_parser.py`

- [ ] **Step 1: Create the fixture**

```html
<!-- tests/fixtures/admob_like.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta property="og:description"
        content="AdMob built a pay-per-click marketplace for mobile apps. Now part of Google.">
  <meta property="og:image"
        content="https://sequoiacap.com/wp-content/uploads/admob-logo.png">
  <title>AdMob | Sequoia Capital</title>
</head>
<body>
  <main>
    <h1>AdMob</h1>
    <p class="sector">GTM</p>
    <ul class="facts">
      <li>Founded 2006</li>
      <li>Partnered 2006</li>
      <li>Acquired 2010</li>
    </ul>
    <a class="cta" href="https://www.admob.com">Visit website</a>
    <div class="about">
      <p>AdMob built a pay-per-click marketplace for mobile apps.</p>
    </div>
  </main>
</body>
</html>
```

- [ ] **Step 2: Write the failing test**

```python
# tests/test_detail_parser.py
from pathlib import Path

from sequoia_crawler.detail_parser import parse_detail

FIXTURE = Path(__file__).parent / "fixtures" / "admob_like.html"


def test_parse_detail_extracts_all_fields():
    data = parse_detail(FIXTURE.read_text(encoding="utf-8"))
    assert data["website"] == "https://www.admob.com"
    assert "pay-per-click" in data["description"]
    assert data["status"] == "Acquired"
    assert data["status_year"] == 2010
    assert data["founded_year"] == 2006
    assert data["partnered_year"] == 2006
    assert data["logo_url"].endswith("admob-logo.png")


def test_parse_detail_missing_fields_are_none():
    data = parse_detail("<html><body><p>nothing here</p></body></html>")
    assert data["website"] is None
    assert data["description"] is None
    assert data["status"] is None
    assert data["status_year"] is None
    assert data["founded_year"] is None
    assert data["partnered_year"] is None
    assert data["logo_url"] is None
```

- [ ] **Step 3: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_detail_parser.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sequoia_crawler.detail_parser'`

- [ ] **Step 4: Write minimal implementation**

```python
# sequoia_crawler/detail_parser.py
from __future__ import annotations

import html
import re
from typing import Optional

from bs4 import BeautifulSoup

# Milestone label + optional year (e.g. "Acquired 2010", "IPO 2019", "Public").
_STATUS_RE = re.compile(
    r"\b(Acquired|Acquisition|IPO|Public|Merged)\b\s*(\d{4})?", re.IGNORECASE
)
_FOUNDED_RE = re.compile(r"Founded\s+(\d{4})", re.IGNORECASE)
_PARTNERED_RE = re.compile(r"Partnered\s+(\d{4})", re.IGNORECASE)

# Hosts that are never the company's own marketing site.
_SKIP_HOSTS = (
    "sequoiacap.com", "twitter.com", "x.com", "facebook.com",
    "linkedin.com", "instagram.com", "youtube.com", "t.co", "medium.com",
)


def _meta(soup: BeautifulSoup, prop: Optional[str] = None,
          name: Optional[str] = None) -> Optional[str]:
    if prop:
        tag = soup.find("meta", property=prop)
        if tag and tag.get("content"):
            return tag["content"].strip()
    if name:
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None


def _is_external(href: str) -> bool:
    return href.startswith("http") and not any(h in href for h in _SKIP_HOSTS)


def _find_website(soup: BeautifulSoup) -> Optional[str]:
    # 1) An explicit "visit website"-style call to action.
    for a in soup.find_all("a", href=True):
        label = a.get_text(" ", strip=True).lower()
        if ("website" in label or "visit" in label) and _is_external(a["href"]):
            return a["href"]
    # 2) Fallback: the first external, non-social link on the page.
    for a in soup.find_all("a", href=True):
        if _is_external(a["href"]):
            return a["href"]
    return None


def _search_year(pattern: re.Pattern, text: str) -> Optional[int]:
    m = pattern.search(text)
    return int(m.group(1)) if m else None


def parse_detail(html_text: str) -> dict:
    soup = BeautifulSoup(html_text, "lxml")
    text = soup.get_text(" ", strip=True)

    description = _meta(soup, prop="og:description", name="description")

    status = None
    status_year = None
    m = _STATUS_RE.search(text)
    if m:
        status = m.group(1).title()
        if m.group(2):
            status_year = int(m.group(2))

    return {
        "website": _find_website(soup),
        "description": html.unescape(description) if description else None,
        "status": status,
        "status_year": status_year,
        "founded_year": _search_year(_FOUNDED_RE, text),
        "partnered_year": _search_year(_PARTNERED_RE, text),
        "logo_url": _meta(soup, prop="og:image"),
    }
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_detail_parser.py -v`
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add sequoia_crawler/detail_parser.py tests/test_detail_parser.py tests/fixtures/admob_like.html
git commit -m "feat: detail page parser for company fields"
```

> NOTE: selectors/regex here are heuristic (built without the real raw HTML). Task 11
> reconciles them against a downloaded live page and tunes them if needed.

---

## Task 5: Sitemap completeness source

**Files:**
- Create: `sequoia_crawler/sitemap.py`
- Test: `tests/test_sitemap.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sitemap.py
from sequoia_crawler.sitemap import fetch_company_slugs

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://sequoiacap.com/companies/admob/</loc></url>
  <url><loc>https://sequoiacap.com/companies/stripe/</loc></url>
  <url><loc>https://sequoiacap.com/our-companies/</loc></url>
</urlset>"""


class FakeResp:
    text = SAMPLE_XML


class FakeClient:
    def get(self, url, **kwargs):
        return FakeResp()


def test_fetch_company_slugs_extracts_only_company_slugs():
    slugs = fetch_company_slugs(FakeClient())
    assert slugs == {"admob", "stripe"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_sitemap.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sequoia_crawler.sitemap'`

- [ ] **Step 3: Write minimal implementation**

```python
# sequoia_crawler/sitemap.py
from __future__ import annotations

import re

SITEMAP_URL = "https://sequoiacap.com/company-sitemap.xml"
_SLUG_RE = re.compile(r"/companies/([^/]+)/")


def fetch_company_slugs(client, url: str = SITEMAP_URL) -> set[str]:
    """Return the set of company slugs listed in the company sitemap."""
    resp = client.get(url)
    return set(_SLUG_RE.findall(resp.text))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_sitemap.py -v`
Expected: 1 passed

- [ ] **Step 5: Commit**

```bash
git add sequoia_crawler/sitemap.py tests/test_sitemap.py
git commit -m "feat: company sitemap slug source for completeness check"
```

---

## Task 6: Enrichment (per-company + concurrent)

**Files:**
- Create: `sequoia_crawler/enrich.py`
- Test: `tests/test_enrich.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_enrich.py
from sequoia_crawler.enrich import enrich_company, enrich_all
from sequoia_crawler.models import Company

HTML = (
    '<html><head>'
    '<meta property="og:description" content="Desc">'
    '</head><body>'
    '<a href="https://www.example.com">Visit website</a>'
    '<span>Founded 2010</span>'
    '</body></html>'
)


class OkClient:
    def __init__(self, text):
        self._text = text

    def get(self, url, **kwargs):
        class R:
            text = self._text
        return R()


class FailClient:
    def get(self, url, **kwargs):
        raise RuntimeError("boom")


def _company(slug="a"):
    return Company(
        id=1, name="A", slug=slug,
        sequoia_url=f"https://sequoiacap.com/companies/{slug}/",
    )


def test_enrich_company_merges_parsed_fields():
    c = enrich_company(OkClient(HTML), _company())
    assert c.website == "https://www.example.com"
    assert c.description == "Desc"
    assert c.founded_year == 2010


def test_enrich_company_survives_fetch_error():
    c = enrich_company(FailClient(), _company())
    assert c.website is None
    assert c.name == "A"


def test_enrich_all_preserves_input_order():
    companies = [_company("a"), _company("b"), _company("c")]
    out = enrich_all(OkClient("<html></html>"), companies, workers=3)
    assert [c.slug for c in out] == ["a", "b", "c"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_enrich.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sequoia_crawler.enrich'`

- [ ] **Step 3: Write minimal implementation**

```python
# sequoia_crawler/enrich.py
from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace

from .detail_parser import parse_detail
from .models import Company

log = logging.getLogger(__name__)


def enrich_company(client, company: Company) -> Company:
    """Fetch a company's detail page and merge parsed fields. Never raises."""
    try:
        resp = client.get(company.sequoia_url)
    except Exception as exc:  # noqa: BLE001 - isolate per-page failures
        log.warning("enrich failed for %s: %s", company.slug, exc)
        return company
    fields = parse_detail(resp.text)
    updates = {k: v for k, v in fields.items() if v is not None}
    return replace(company, **updates)


def enrich_all(client, companies: list[Company], workers: int = 5) -> list[Company]:
    """Enrich all companies concurrently, preserving input order."""
    order = {c.slug: i for i, c in enumerate(companies)}
    results: list[Company] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(enrich_company, client, c) for c in companies]
        for fut in as_completed(futures):
            results.append(fut.result())
    results.sort(key=lambda c: order[c.slug])
    return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_enrich.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add sequoia_crawler/enrich.py tests/test_enrich.py
git commit -m "feat: concurrent detail-page enrichment"
```

---

## Task 7: Exporters (JSON + CSV)

**Files:**
- Create: `sequoia_crawler/export.py`
- Test: `tests/test_export.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_export.py
import csv
import json

from sequoia_crawler.export import write_json, write_csv
from sequoia_crawler.models import Company


def _company():
    return Company(
        id=1, name="AdMob", slug="admob", sequoia_url="https://x/",
        sectors=["GTM", "AI"], website="https://www.admob.com", status="Acquired",
        status_year=2010,
    )


def test_write_json_round_trips(tmp_path):
    path = tmp_path / "companies.json"
    write_json([_company()], path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["name"] == "AdMob"
    assert data[0]["sectors"] == ["GTM", "AI"]
    assert data[0]["status_year"] == 2010


def test_write_csv_joins_sectors_and_has_header(tmp_path):
    path = tmp_path / "companies.csv"
    write_csv([_company()], path)
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows[0]["sectors"] == "GTM;AI"
    assert rows[0]["name"] == "AdMob"
    assert rows[0]["status"] == "Acquired"


def test_writers_create_missing_parent_dir(tmp_path):
    nested = tmp_path / "out" / "companies.json"
    write_json([_company()], nested)
    assert nested.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_export.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'sequoia_crawler.export'`

- [ ] **Step 3: Write minimal implementation**

```python
# sequoia_crawler/export.py
from __future__ import annotations

import csv
import json
from pathlib import Path

from .models import Company, CSV_FIELDS


def write_json(companies: list[Company], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [c.to_dict() for c in companies]
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def write_csv(companies: list[Company], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for company in companies:
            writer.writerow(company.to_csv_row())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_export.py -v`
Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add sequoia_crawler/export.py tests/test_export.py
git commit -m "feat: JSON and CSV exporters"
```

---

## Task 8: CLI orchestration

**Files:**
- Create: `sequoia_crawler/__main__.py`
- Test: `tests/test_main.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_main.py
import sequoia_crawler.__main__ as cli
from sequoia_crawler.models import Company


def _sample():
    return [Company(id=1, name="A", slug="a", sequoia_url="u", sectors=["AI"])]


def test_main_writes_both_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "build_companies", lambda client: _sample())
    monkeypatch.setattr(cli, "_check_completeness", lambda client, companies: None)
    rc = cli.main(["--out", str(tmp_path), "--no-enrich", "--format", "both"])
    assert rc == 0
    assert (tmp_path / "companies.json").exists()
    assert (tmp_path / "companies.csv").exists()


def test_main_limit_truncates(tmp_path, monkeypatch):
    many = [Company(id=i, name=str(i), slug=str(i), sequoia_url="u") for i in range(10)]
    monkeypatch.setattr(cli, "build_companies", lambda client: many)
    monkeypatch.setattr(cli, "_check_completeness", lambda client, companies: None)
    captured = {}
    monkeypatch.setattr(cli, "write_json", lambda comps, path: captured.update(n=len(comps)))
    monkeypatch.setattr(cli, "write_csv", lambda comps, path: None)
    rc = cli.main(["--out", str(tmp_path), "--no-enrich", "--format", "json", "--limit", "3"])
    assert rc == 0
    assert captured["n"] == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_main.py -v`
Expected: FAIL with `ModuleNotFoundError` / `AttributeError` for `build_companies`

- [ ] **Step 3: Write minimal implementation**

```python
# sequoia_crawler/__main__.py
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from . import api
from .enrich import enrich_all
from .export import write_csv, write_json
from .http_client import PoliteClient
from .sitemap import fetch_company_slugs

log = logging.getLogger("sequoia_crawler")


def build_companies(client) -> list:
    sectors = api.fetch_categories(client)
    log.info("Loaded %d sector categories", len(sectors))
    return [api.to_company(raw, sectors) for raw in api.iter_companies(client)]


def _check_completeness(client, companies) -> None:
    try:
        sitemap_slugs = fetch_company_slugs(client)
    except Exception as exc:  # noqa: BLE001
        log.warning("sitemap check skipped: %s", exc)
        return
    have = {c.slug for c in companies}
    missing = sitemap_slugs - have
    extra = have - sitemap_slugs
    log.info(
        "Completeness: api=%d sitemap=%d missing_from_api=%d api_only=%d",
        len(have), len(sitemap_slugs), len(missing), len(extra),
    )
    if missing:
        log.warning("Slugs in sitemap but not in API: %s", sorted(missing)[:20])


def _parse_args(argv):
    p = argparse.ArgumentParser(
        prog="sequoia_crawler",
        description="Crawl Sequoia Capital portfolio companies to JSON/CSV.",
    )
    p.add_argument("--out", type=Path, default=Path("output"))
    p.add_argument("--format", choices=["json", "csv", "both"], default="both")
    p.add_argument("--workers", type=int, default=5)
    p.add_argument("--delay", type=float, default=0.2)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--no-enrich", action="store_true",
                   help="index only; skip detail-page enrichment")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    client = PoliteClient(delay=args.delay)

    log.info("Fetching company index from REST API ...")
    companies = build_companies(client)
    log.info("Index: %d companies", len(companies))
    _check_completeness(client, companies)

    if args.limit:
        companies = companies[: args.limit]
        log.info("Limited to %d companies", len(companies))

    if not args.no_enrich:
        log.info("Enriching %d companies (workers=%d) ...", len(companies), args.workers)
        companies = enrich_all(client, companies, workers=args.workers)

    args.out.mkdir(parents=True, exist_ok=True)
    if args.format in ("json", "both"):
        write_json(companies, args.out / "companies.json")
        log.info("Wrote %s", args.out / "companies.json")
    if args.format in ("csv", "both"):
        write_csv(companies, args.out / "companies.csv")
        log.info("Wrote %s", args.out / "companies.csv")

    log.info("Done: %d companies", len(companies))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_main.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add sequoia_crawler/__main__.py tests/test_main.py
git commit -m "feat: CLI orchestration with completeness check"
```

---

## Task 9: Full offline test suite green

**Files:** none (verification)

- [ ] **Step 1: Run the whole suite**

Run: `.venv/bin/python -m pytest -v`
Expected: all tests pass (Tasks 1–8), no network used.

- [ ] **Step 2: Commit if any fixups were needed** (otherwise skip)

```bash
git commit -am "test: full offline suite green"
```

---

## Task 10: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write `README.md`**

````markdown
# Sequoia Capital Companies Crawler

Collects all companies listed on
[Sequoia's Our Companies page](https://sequoiacap.com/our-companies/#all-panel)
and exports them to JSON and CSV.

## How it works

1. Enumerates the full company list from the WordPress REST API
   (`/wp-json/wp/v2/company`, paginated).
2. Resolves sector names from the categories taxonomy.
3. Enriches each company from its server-rendered detail page
   (`/companies/<slug>/`): website, description, status, founded/partnered years, logo.
4. Writes `output/companies.json` and `output/companies.csv`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

```bash
# Full crawl (index + enrichment) -> output/companies.json + .csv
.venv/bin/python -m sequoia_crawler

# Index only (fast, no detail pages)
.venv/bin/python -m sequoia_crawler --no-enrich

# Quick test on 5 companies, JSON only, verbose
.venv/bin/python -m sequoia_crawler --limit 5 --format json --verbose
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--out DIR` | `output` | Output directory |
| `--format {json,csv,both}` | `both` | Output format(s) |
| `--workers N` | `5` | Enrichment concurrency |
| `--delay SECONDS` | `0.2` | Min spacing between request starts |
| `--limit N` | — | Process only the first N companies |
| `--no-enrich` | off | Index only; skip detail pages |
| `--verbose` | off | Debug logging |

## Tests

```bash
.venv/bin/python -m pytest -v
```
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: usage README"
```

---

## Task 11: Live reconciliation & end-to-end run (REQUIRES NETWORK)

**Files:**
- Create (git-ignored): `tests/fixtures/admob_real.html`, `output/companies.json`, `output/companies.csv`

> Run this task with network available: either the user runs the commands via `! <cmd>`
> in-session, or Bash is run with the sandbox disabled.

- [ ] **Step 1: Download a real detail page as a reconciliation fixture**

Run:
```bash
.venv/bin/python -c "from sequoia_crawler.http_client import PoliteClient; open('tests/fixtures/admob_real.html','w',encoding='utf-8').write(PoliteClient().get('https://sequoiacap.com/companies/admob/').text)"
```
Expected: file `tests/fixtures/admob_real.html` created (non-empty).

- [ ] **Step 2: Run the parser against the real page and check known values**

Run:
```bash
.venv/bin/python -c "from sequoia_crawler.detail_parser import parse_detail; d=parse_detail(open('tests/fixtures/admob_real.html',encoding='utf-8').read()); print(d)"
```
Expected: `website` ≈ `https://www.admob.com`, `description` mentions "pay-per-click",
`status` == `Acquired`, `status_year` == 2010, `founded_year` == 2006,
`partnered_year` == 2006.

- [ ] **Step 3: If any field is wrong, tune `detail_parser.py`**

Inspect the real HTML around the wrong field (e.g. `grep -i "admob.com\|Acquired\|Founded" tests/fixtures/admob_real.html`), adjust the selector/regex in
`sequoia_crawler/detail_parser.py`, and re-run Step 2 until all known values match.
Re-run `.venv/bin/python -m pytest tests/test_detail_parser.py -v` to keep the
synthetic-fixture tests green.

- [ ] **Step 4: Run a small live crawl**

Run: `.venv/bin/python -m sequoia_crawler --limit 5 --verbose`
Expected: logs the index count and completeness line; writes `output/companies.json`
and `output/companies.csv` with 5 enriched companies.

- [ ] **Step 5: Inspect a sample**

Run: `.venv/bin/python -c "import json; d=json.load(open('output/companies.json')); print(len(d)); print(d[0])"`
Expected: company objects populated with name, sequoia_url, sectors, and (where present)
website/description/status.

- [ ] **Step 6: Run the full crawl**

Run: `.venv/bin/python -m sequoia_crawler --verbose`
Expected: index ≈ 490 companies; completeness log shows `missing_from_api=0` (or only a
handful, logged). `output/companies.json` and `output/companies.csv` contain all
companies.

- [ ] **Step 7: Sanity-check totals**

Run: `.venv/bin/python -c "import json; d=json.load(open('output/companies.json')); print('total', len(d)); print('with_website', sum(1 for c in d if c['website'])); print('with_status', sum(1 for c in d if c['status']))"`
Expected: `total` ≈ 490; a substantial share have website/status populated.

- [ ] **Step 8: Commit the parser fixes** (outputs stay git-ignored)

```bash
git add sequoia_crawler/detail_parser.py
git commit -m "fix: reconcile detail parser with live page" || echo "no parser changes needed"
```

---

## Self-Review Notes

- **Spec coverage:** index via REST API (Task 3), sector resolution (Task 3),
  detail enrichment incl. website/description/status/years/logo (Tasks 4, 6),
  sitemap completeness check (Tasks 5, 8), JSON+CSV output (Task 7), reliability
  (retry/backoff/rate-limit/error isolation in Tasks 2, 6), CLI flags incl.
  `--no-enrich/--limit/--workers/--out/--format/--verbose` (Task 8), TDD with
  fixtures throughout, live reconciliation for the heuristic parser (Task 11).
- **Known risk:** `detail_parser` selectors are heuristic (no raw HTML was available
  at planning time). Task 11 validates and tunes them against a real page; synthetic
  fixture tests guard the contract.
