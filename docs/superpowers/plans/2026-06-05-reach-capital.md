# Reach Capital Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Reach Capital (Learning sector) portfolio crawler that fetches ~95 companies via WordPress AJAX infinite-scroll and exports them in the project's standard JSON/CSV format.

**Architecture:** Single-stage crawl — one GET for the initial page, one GET for a WordPress nonce, then repeated POSTs to `admin-ajax.php` with PHP-style array-encoded args and increasing `offset` until the response is empty. Parser is shared across the initial page HTML and every AJAX fragment. Follows the `owl_ventures` module structure: `parser.py → normalizer.py → crawler.py`.

**Tech Stack:** Python 3.10+, `requests`, `beautifulsoup4 + lxml`, `pytest`. No new dependencies.

---

## File Map

| Action | Path |
|---|---|
| Create | `tests/fixtures/reach_capital_portfolio.html` |
| Create | `tests/fixtures/reach_capital_ajax.html` |
| Modify | `vc_crawler/http_client.py` (add `post()`) |
| Modify | `tests/test_http_client.py` (add post tests) |
| Create | `vc_crawler/crawlers/reach_capital/__init__.py` |
| Create | `vc_crawler/crawlers/reach_capital/parser.py` |
| Create | `tests/test_reach_parser.py` |
| Create | `vc_crawler/crawlers/reach_capital/normalizer.py` |
| Create | `tests/test_reach_normalizer.py` |
| Create | `vc_crawler/crawlers/reach_capital/crawler.py` |
| Create | `tests/test_reach_crawler.py` |
| Modify | `vc_crawler/__main__.py` (register fund) |
| Modify | `tests/test_vc_main.py` (add integration test) |
| Modify | `README.md` (add fund entry) |

---

## Task 1: Create HTML fixtures

**Files:**
- Create: `tests/fixtures/reach_capital_portfolio.html`
- Create: `tests/fixtures/reach_capital_ajax.html`

These fixtures represent the real HTML structure observed on `https://www.reachcapital.com/companies/?sector=learning`. The portfolio fixture has 3 cards (1 normal with full data, 1 exited, 1 with no founders). The AJAX fixture has 2 cards (as returned by `admin-ajax.php`).

- [ ] **Step 1: Create portfolio fixture**

`tests/fixtures/reach_capital_portfolio.html`:

```html
<!DOCTYPE html>
<html>
<body>

<!-- Company 1: BookNook — active, full data, two founders -->
<div class="reach-portfolio-card" data-aos="fade-up">
 <div class="reach-portfolio-card__grid">
  <div class="reach-portfolio-card__company">
   <div class="reach-portfolio-card__title">BookNook</div>
   <div class="reach-portfolio-card__tags">
    <div class="reach-portfolio-card__tag">Learning</div>
   </div>
  </div>
  <div class="reach-portfolio-card__info">
   <div class="reach-portfolio-card__desc reach-editor-content">
    <p>Literacy platform connecting students with certified tutors.</p>
   </div>
  </div>
  <div class="reach-portfolio-card__investor">
   <div class="reach-portfolio-card__investor-list">
    <a class="reach-portfolio-card__investor-item" href="https://www.reachcapital.com/team/shauntel/">Shauntel Gry</a>
   </div>
  </div>
 </div>
 <div class="reach-portfolio-card__spoiler">
  <div class="reach-portfolio-card__grid">
   <div></div>
   <div class="reach-portfolio-card__info-items">
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_year">
     <div class="reach-portfolio-card__info-item-title">Founded</div>
     <div class="reach-portfolio-card__info-item-desc">2016</div>
    </div>
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_location">
     <div class="reach-portfolio-card__info-item-title">Headquarters</div>
     <div class="reach-portfolio-card__info-item-desc">Houston, TX</div>
    </div>
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_founders">
     <div class="reach-portfolio-card__info-item-title">Leadership</div>
     <div class="reach-portfolio-card__info-item-desc">
      <span>Dana Brown</span>
      <span>Michael Lombardo</span>
     </div>
    </div>
   </div>
   <div class="reach-portfolio-card__logo">
    <a class="reach-logo-card reach-contain-img" href="https://booknook.com/" target="_blank">
     <img alt="BookNook logo" src="https://www.reachcapital.com/wp-content/uploads/BookNook.png"/>
    </a>
   </div>
  </div>
 </div>
</div>

<!-- Company 2: Abl — exited, three founders -->
<div class="reach-portfolio-card" data-aos="fade-up">
 <div class="reach-portfolio-card__grid">
  <div class="reach-portfolio-card__company">
   <div class="reach-portfolio-card__title">Abl</div>
   <div class="reach-portfolio-card__tags">
    <div class="reach-portfolio-card__tag">Learning</div>
    <div class="reach-portfolio-card__tag reach-portfolio-card__tag_exited">Exit</div>
   </div>
  </div>
  <div class="reach-portfolio-card__info">
   <div class="reach-portfolio-card__desc reach-editor-content">
    <p>Master scheduling tools and guidance for schools.</p>
   </div>
  </div>
  <div class="reach-portfolio-card__investor"></div>
 </div>
 <div class="reach-portfolio-card__spoiler">
  <div class="reach-portfolio-card__grid">
   <div></div>
   <div class="reach-portfolio-card__info-items">
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_year">
     <div class="reach-portfolio-card__info-item-title">Founded</div>
     <div class="reach-portfolio-card__info-item-desc">2015</div>
    </div>
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_location">
     <div class="reach-portfolio-card__info-item-title">Headquarters</div>
     <div class="reach-portfolio-card__info-item-desc">San Francisco, CA</div>
    </div>
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_founders">
     <div class="reach-portfolio-card__info-item-title">Leadership</div>
     <div class="reach-portfolio-card__info-item-desc">
      <span>Adam Pisoni</span>
      <span>Amy Filsinger</span>
      <span>Chris Walsh</span>
     </div>
    </div>
   </div>
   <div class="reach-portfolio-card__logo">
    <a class="reach-logo-card reach-contain-img" href="https://ablschools.com/" target="_blank">
     <img alt="Abl logo" src="https://www.reachcapital.com/wp-content/uploads/Abl.png"/>
    </a>
   </div>
  </div>
 </div>
</div>

<!-- Company 3: Aprende Institute — active, no founders section -->
<div class="reach-portfolio-card" data-aos="fade-up">
 <div class="reach-portfolio-card__grid">
  <div class="reach-portfolio-card__company">
   <div class="reach-portfolio-card__title">Aprende Institute</div>
   <div class="reach-portfolio-card__tags">
    <div class="reach-portfolio-card__tag">Learning</div>
   </div>
  </div>
  <div class="reach-portfolio-card__info">
   <div class="reach-portfolio-card__desc reach-editor-content">
    <p>The leading online education platform for vocational skills training.</p>
   </div>
  </div>
  <div class="reach-portfolio-card__investor"></div>
 </div>
 <div class="reach-portfolio-card__spoiler">
  <div class="reach-portfolio-card__grid">
   <div></div>
   <div class="reach-portfolio-card__info-items">
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_year">
     <div class="reach-portfolio-card__info-item-title">Founded</div>
     <div class="reach-portfolio-card__info-item-desc">2020</div>
    </div>
   </div>
   <div class="reach-portfolio-card__logo">
    <a class="reach-logo-card reach-contain-img" href="https://aprende.com/" target="_blank">
     <img alt="Aprende logo" src="https://www.reachcapital.com/wp-content/uploads/Aprende.png"/>
    </a>
   </div>
  </div>
 </div>
</div>

</body>
</html>
```

- [ ] **Step 2: Create AJAX fixture**

`tests/fixtures/reach_capital_ajax.html` (format matches real `admin-ajax.php` response):

```html
<div class="reach-portfolio-listing__list">

<!-- Company 4: Desmos — active, single founder -->
<div class="reach-portfolio-card" data-aos="fade-up">
 <div class="reach-portfolio-card__grid">
  <div class="reach-portfolio-card__company">
   <div class="reach-portfolio-card__title">Desmos</div>
   <div class="reach-portfolio-card__tags">
    <div class="reach-portfolio-card__tag">Learning</div>
   </div>
  </div>
  <div class="reach-portfolio-card__info">
   <div class="reach-portfolio-card__desc reach-editor-content">
    <p>Beautiful, free math for everyone.</p>
   </div>
  </div>
  <div class="reach-portfolio-card__investor">
   <div class="reach-portfolio-card__investor-list">
    <a class="reach-portfolio-card__investor-item" href="https://www.reachcapital.com/team/jennifer/">Jennifer Carolan</a>
   </div>
  </div>
 </div>
 <div class="reach-portfolio-card__spoiler">
  <div class="reach-portfolio-card__grid">
   <div></div>
   <div class="reach-portfolio-card__info-items">
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_year">
     <div class="reach-portfolio-card__info-item-title">Founded</div>
     <div class="reach-portfolio-card__info-item-desc">2011</div>
    </div>
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_location">
     <div class="reach-portfolio-card__info-item-title">Headquarters</div>
     <div class="reach-portfolio-card__info-item-desc">San Francisco, CA</div>
    </div>
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_founders">
     <div class="reach-portfolio-card__info-item-title">Leadership</div>
     <div class="reach-portfolio-card__info-item-desc">
      <span>Eli Luberoff</span>
     </div>
    </div>
   </div>
   <div class="reach-portfolio-card__logo">
    <a class="reach-logo-card reach-contain-img" href="https://www.desmos.com/" target="_blank">
     <img alt="Desmos logo" src="https://www.reachcapital.com/wp-content/uploads/Desmos.png"/>
    </a>
   </div>
  </div>
 </div>
</div>

<!-- Company 5: Brilliant — exited, no founders -->
<div class="reach-portfolio-card" data-aos="fade-up">
 <div class="reach-portfolio-card__grid">
  <div class="reach-portfolio-card__company">
   <div class="reach-portfolio-card__title">Brilliant</div>
   <div class="reach-portfolio-card__tags">
    <div class="reach-portfolio-card__tag">Learning</div>
    <div class="reach-portfolio-card__tag reach-portfolio-card__tag_exited">Exit</div>
   </div>
  </div>
  <div class="reach-portfolio-card__info">
   <div class="reach-portfolio-card__desc reach-editor-content">
    <p>Learn by doing: interactive STEM courses.</p>
   </div>
  </div>
  <div class="reach-portfolio-card__investor"></div>
 </div>
 <div class="reach-portfolio-card__spoiler">
  <div class="reach-portfolio-card__grid">
   <div></div>
   <div class="reach-portfolio-card__info-items">
    <div class="reach-portfolio-card__info-item reach-portfolio-card__info-item_year">
     <div class="reach-portfolio-card__info-item-title">Founded</div>
     <div class="reach-portfolio-card__info-item-desc">2012</div>
    </div>
   </div>
   <div class="reach-portfolio-card__logo">
    <a class="reach-logo-card reach-contain-img" href="https://brilliant.org/" target="_blank">
     <img alt="Brilliant logo" src="https://www.reachcapital.com/wp-content/uploads/Brilliant.png"/>
    </a>
   </div>
  </div>
 </div>
</div>

</div>
```

- [ ] **Step 3: Commit fixtures**

```bash
git add tests/fixtures/reach_capital_portfolio.html tests/fixtures/reach_capital_ajax.html
git commit -m "test: add Reach Capital HTML fixtures"
```

---

## Task 2: Add `post()` to PoliteClient

**Files:**
- Modify: `vc_crawler/http_client.py`
- Modify: `tests/test_http_client.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_http_client.py`:

```python
class FakeSessionWithPost:
    def __init__(self, resp):
        self.resp = resp
        self.calls: list[tuple] = []

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        return self.resp

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return self.resp


def test_polite_post_delegates_and_sets_timeout():
    resp = FakeResp(200)
    sess = FakeSessionWithPost(resp)
    client = PoliteClient(session=sess, delay=0, timeout=15)
    out = client.post("https://example.com", data="foo=bar")
    assert out is resp
    method, url, kwargs = sess.calls[0]
    assert method == "post"
    assert url == "https://example.com"
    assert kwargs["timeout"] == 15
    assert kwargs["data"] == "foo=bar"


def test_polite_post_raises_on_http_error():
    class FakeSessionErr:
        def post(self, url, **kwargs):
            return FakeResp(500)
    client = PoliteClient(session=FakeSessionErr(), delay=0)
    with pytest.raises(RuntimeError):
        client.post("https://example.com")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_http_client.py::test_polite_post_delegates_and_sets_timeout tests/test_http_client.py::test_polite_post_raises_on_http_error -v
```

Expected: FAIL with `AttributeError: 'PoliteClient' object has no attribute 'post'`

- [ ] **Step 3: Add `post()` to PoliteClient**

In `vc_crawler/http_client.py`, after the `get()` method (line ~63), add:

```python
    def post(self, url: str, **kwargs) -> requests.Response:
        if self.delay:
            self._throttle()
        kwargs.setdefault("timeout", self.timeout)
        resp = self.session.post(url, **kwargs)
        resp.raise_for_status()
        return resp
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_http_client.py -v
```

Expected: all PASS (including the 4 existing tests)

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/http_client.py tests/test_http_client.py
git commit -m "feat: add post() method to PoliteClient"
```

---

## Task 3: Implement parser

**Files:**
- Create: `vc_crawler/crawlers/reach_capital/__init__.py`
- Create: `vc_crawler/crawlers/reach_capital/parser.py`
- Create: `tests/test_reach_parser.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_reach_parser.py`:

```python
from pathlib import Path
import pytest
from vc_crawler.crawlers.reach_capital.parser import (
    PORTFOLIO_URL,
    parse_cards,
)

PORTFOLIO_FIXTURE = (
    Path(__file__).parent / "fixtures" / "reach_capital_portfolio.html"
).read_text(encoding="utf-8")

AJAX_FIXTURE = (
    Path(__file__).parent / "fixtures" / "reach_capital_ajax.html"
).read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://www.reachcapital.com/companies/?sector=learning"


def test_returns_list_of_dicts():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_three_companies_from_portfolio():
    assert len(parse_cards(PORTFOLIO_FIXTURE)) == 3


def test_returns_two_companies_from_ajax():
    assert len(parse_cards(AJAX_FIXTURE)) == 2


def test_empty_html_returns_empty_list():
    assert parse_cards("<html><body></body></html>") == []


def test_company_name():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["name"] == "BookNook"


def test_second_company_name():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["name"] == "Abl"


def test_active_company_not_exited():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["is_exited"] is False


def test_exited_company_flag():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["is_exited"] is True


def test_ajax_exited_company():
    result = parse_cards(AJAX_FIXTURE)
    assert result[1]["is_exited"] is True


def test_description():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["description"] == "Literacy platform connecting students with certified tutors."


def test_description_second_company():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["description"] == "Master scheduling tools and guidance for schools."


def test_founded_year_str():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["founded_year_str"] == "2016"


def test_founded_year_str_second():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["founded_year_str"] == "2015"


def test_founded_year_str_ajax():
    result = parse_cards(AJAX_FIXTURE)
    assert result[0]["founded_year_str"] == "2011"


def test_founders_list():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["founders"] == ["Dana Brown", "Michael Lombardo"]


def test_founders_multiple():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["founders"] == ["Adam Pisoni", "Amy Filsinger", "Chris Walsh"]


def test_founders_empty_when_no_leadership_section():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[2]["founders"] == []


def test_website():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["website"] == "https://booknook.com/"


def test_website_second():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["website"] == "https://ablschools.com/"


def test_logo_url():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["logo_url"] == "https://www.reachcapital.com/wp-content/uploads/BookNook.png"


def test_logo_url_second():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["logo_url"] == "https://www.reachcapital.com/wp-content/uploads/Abl.png"


def test_ajax_company_name():
    result = parse_cards(AJAX_FIXTURE)
    assert result[0]["name"] == "Desmos"


def test_ajax_website():
    result = parse_cards(AJAX_FIXTURE)
    assert result[0]["website"] == "https://www.desmos.com/"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_reach_parser.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vc_crawler.crawlers.reach_capital'`

- [ ] **Step 3: Create package init**

Create `vc_crawler/crawlers/reach_capital/__init__.py` (empty file):

```python
```

- [ ] **Step 4: Create parser**

Create `vc_crawler/crawlers/reach_capital/parser.py`:

```python
from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.reachcapital.com/companies/?sector=learning"
AJAX_URL = "https://www.reachcapital.com/wp-admin/admin-ajax.php"
NONCE_URL = f"{AJAX_URL}?action=reach_get_nonce"


def parse_cards(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.find_all("div", class_="reach-portfolio-card")
    result = []
    for card in cards:
        raw = _parse_card(card)
        if raw["name"]:
            result.append(raw)
    return result


def _parse_card(card) -> dict:
    raw: dict = {}

    title_el = card.find(class_="reach-portfolio-card__title")
    raw["name"] = title_el.get_text(strip=True) if title_el else ""

    raw["is_exited"] = bool(card.find(class_="reach-portfolio-card__tag_exited"))

    desc_el = card.find(class_="reach-portfolio-card__desc")
    p = desc_el.find("p") if desc_el else None
    raw["description"] = p.get_text(strip=True) or None if p else None

    spoiler = card.find(class_="reach-portfolio-card__spoiler")
    raw.update(_parse_spoiler(spoiler) if spoiler else _empty_spoiler())

    return raw


def _parse_spoiler(spoiler) -> dict:
    out: dict = {"founded_year_str": None, "founders": [], "website": None, "logo_url": None}

    year_item = spoiler.find(class_="reach-portfolio-card__info-item_year")
    if year_item:
        desc = year_item.find(class_="reach-portfolio-card__info-item-desc")
        out["founded_year_str"] = desc.get_text(strip=True) or None if desc else None

    founders_item = spoiler.find(class_="reach-portfolio-card__info-item_founders")
    if founders_item:
        desc = founders_item.find(class_="reach-portfolio-card__info-item-desc")
        if desc:
            out["founders"] = [
                s.get_text(strip=True)
                for s in desc.find_all("span")
                if s.get_text(strip=True)
            ]

    logo_div = spoiler.find(class_="reach-portfolio-card__logo")
    if logo_div:
        link = logo_div.find("a", class_="reach-logo-card")
        out["website"] = link.get("href") or None if link else None
        img = logo_div.find("img")
        out["logo_url"] = img.get("src") or None if img else None

    return out


def _empty_spoiler() -> dict:
    return {"founded_year_str": None, "founders": [], "website": None, "logo_url": None}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_reach_parser.py -v
```

Expected: all PASS

- [ ] **Step 6: Commit**

```bash
git add vc_crawler/crawlers/reach_capital/__init__.py \
        vc_crawler/crawlers/reach_capital/parser.py \
        tests/test_reach_parser.py
git commit -m "feat: add Reach Capital HTML parser"
```

---

## Task 4: Implement normalizer

**Files:**
- Create: `vc_crawler/crawlers/reach_capital/normalizer.py`
- Create: `tests/test_reach_normalizer.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_reach_normalizer.py`:

```python
from vc_crawler.crawlers.reach_capital.normalizer import normalize
from vc_crawler.models import Company


def _booknook():
    return {
        "name": "BookNook",
        "is_exited": False,
        "description": "Literacy platform connecting students with certified tutors.",
        "website": "https://booknook.com/",
        "logo_url": "https://www.reachcapital.com/wp-content/uploads/BookNook.png",
        "founded_year_str": "2016",
        "founders": ["Dana Brown", "Michael Lombardo"],
    }


def _abl():
    return {
        "name": "Abl",
        "is_exited": True,
        "description": "Master scheduling tools and guidance for schools.",
        "website": "https://ablschools.com/",
        "logo_url": "https://www.reachcapital.com/wp-content/uploads/Abl.png",
        "founded_year_str": "2015",
        "founders": ["Adam Pisoni", "Amy Filsinger", "Chris Walsh"],
    }


def _aprende():
    return {
        "name": "Aprende Institute",
        "is_exited": False,
        "description": "The leading online education platform for vocational skills training.",
        "website": "https://aprende.com/",
        "logo_url": "https://www.reachcapital.com/wp-content/uploads/Aprende.png",
        "founded_year_str": "2020",
        "founders": [],
    }


def test_returns_company_instance():
    assert isinstance(normalize(_booknook(), 1), Company)


def test_fund_is_reach_capital():
    assert normalize(_booknook(), 1).fund == "reach-capital"


def test_id_assigned():
    assert normalize(_booknook(), 42).id == 42


def test_name():
    assert normalize(_booknook(), 1).name == "BookNook"


def test_slug_single_word():
    assert normalize(_booknook(), 1).slug == "booknook"


def test_slug_two_words():
    assert normalize(_aprende(), 1).slug == "aprende-institute"


def test_fund_url():
    assert normalize(_booknook(), 1).fund_url == "https://www.reachcapital.com/companies/?sector=learning"


def test_sectors():
    assert normalize(_booknook(), 1).sectors == ["Learning"]


def test_website():
    assert normalize(_booknook(), 1).website == "https://booknook.com/"


def test_website_none_when_missing():
    raw = _booknook()
    raw["website"] = None
    assert normalize(raw, 1).website is None


def test_description():
    assert normalize(_booknook(), 1).description == "Literacy platform connecting students with certified tutors."


def test_description_none_when_missing():
    raw = _booknook()
    raw["description"] = None
    assert normalize(raw, 1).description is None


def test_stage_none_when_active():
    assert normalize(_booknook(), 1).stage is None


def test_stage_exit_when_exited():
    assert normalize(_abl(), 1).stage == "Exit"


def test_founded_year():
    assert normalize(_booknook(), 1).founded_year == 2016


def test_founded_year_abl():
    assert normalize(_abl(), 1).founded_year == 2015


def test_founded_year_none_when_missing():
    raw = _booknook()
    raw["founded_year_str"] = None
    assert normalize(raw, 1).founded_year is None


def test_founded_year_invalid_string_returns_none():
    raw = _booknook()
    raw["founded_year_str"] = "not-a-year"
    assert normalize(raw, 1).founded_year is None


def test_founders():
    assert normalize(_booknook(), 1).founders == ["Dana Brown", "Michael Lombardo"]


def test_founders_multiple():
    assert normalize(_abl(), 1).founders == ["Adam Pisoni", "Amy Filsinger", "Chris Walsh"]


def test_founders_none_when_empty_list():
    assert normalize(_aprende(), 1).founders is None


def test_logo_url():
    assert normalize(_booknook(), 1).logo_url == "https://www.reachcapital.com/wp-content/uploads/BookNook.png"


def test_logo_url_none_when_missing():
    raw = _booknook()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


def test_invested_year_none():
    assert normalize(_booknook(), 1).invested_year is None


def test_stage_year_none():
    assert normalize(_booknook(), 1).stage_year is None


def test_ticker_symbol_none():
    assert normalize(_booknook(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_booknook(), 1).acquirer is None


def test_source_modified_none():
    assert normalize(_booknook(), 1).source_modified is None
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_reach_normalizer.py -v
```

Expected: FAIL with `ImportError`

- [ ] **Step 3: Create normalizer**

Create `vc_crawler/crawlers/reach_capital/normalizer.py`:

```python
from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

FUND_URL = "https://www.reachcapital.com/companies/?sector=learning"
_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")


def normalize(raw: dict, company_id: int) -> Company:
    founders = raw.get("founders") or []
    return Company(
        id=company_id,
        fund="reach-capital",
        name=raw.get("name", ""),
        slug=_slugify(raw.get("name", "")),
        fund_url=FUND_URL,
        sectors=["Learning"],
        website=raw.get("website") or None,
        description=raw.get("description") or None,
        stage="Exit" if raw.get("is_exited") else None,
        stage_year=None,
        founded_year=_parse_int(raw.get("founded_year_str")),
        invested_year=None,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=founders if founders else None,
    )


def _slugify(name: str) -> str:
    return _SLUG_STRIP_RE.sub("-", name.lower()).strip("-")


def _parse_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    try:
        return int(text.strip())
    except ValueError:
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_reach_normalizer.py -v
```

Expected: all PASS

- [ ] **Step 5: Commit**

```bash
git add vc_crawler/crawlers/reach_capital/normalizer.py tests/test_reach_normalizer.py
git commit -m "feat: add Reach Capital normalizer"
```

---

## Task 5: Implement crawler

**Files:**
- Create: `vc_crawler/crawlers/reach_capital/crawler.py`
- Create: `tests/test_reach_crawler.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_reach_crawler.py`:

```python
from pathlib import Path
from vc_crawler.crawlers.reach_capital.crawler import ReachCrawler
from vc_crawler.crawlers.reach_capital.parser import PORTFOLIO_URL, AJAX_URL, NONCE_URL
from vc_crawler.models import Company

PORTFOLIO_HTML = (
    Path(__file__).parent / "fixtures" / "reach_capital_portfolio.html"
).read_text(encoding="utf-8")

AJAX_HTML = (
    Path(__file__).parent / "fixtures" / "reach_capital_ajax.html"
).read_text(encoding="utf-8")

NONCE_JSON = '{"success":true,"data":{"nonce":"test-nonce-123"}}'


class _FakeResp:
    def __init__(self, text: str):
        self.text = text


class _FakeClient:
    """
    get_responses: popped in order for each client.get() call.
    post_responses: popped in order for each client.post() call.
    """
    def __init__(self, get_responses: list[str], post_responses: list[str]):
        self._gets = list(get_responses)
        self._posts = list(post_responses)
        self.get_calls: list[str] = []
        self.post_calls: list[str] = []
        self.post_data: list = []

    def get(self, url, **kw):
        self.get_calls.append(url)
        return _FakeResp(self._gets.pop(0))

    def post(self, url, **kw):
        self.post_calls.append(url)
        self.post_data.append(kw.get("data", ""))
        return _FakeResp(self._posts.pop(0))


def _make_client(extra_ajax_pages: int = 0):
    """
    Standard client: page HTML + nonce + one AJAX batch + empty stop signal.
    extra_ajax_pages adds additional AJAX batches before the stop signal.
    """
    return _FakeClient(
        get_responses=[PORTFOLIO_HTML, NONCE_JSON],
        post_responses=[AJAX_HTML] * (1 + extra_ajax_pages) + [""],
    )


def test_returns_list_of_companies():
    companies = ReachCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_combined_companies():
    # 3 from portfolio page + 2 from AJAX batch
    companies = ReachCrawler(_make_client()).run()
    assert len(companies) == 5


def test_all_fund_reach_capital():
    companies = ReachCrawler(_make_client()).run()
    assert all(c.fund == "reach-capital" for c in companies)


def test_sequential_ids():
    companies = ReachCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3, 4, 5]


def test_limit_truncates():
    companies = ReachCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = ReachCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    ReachCrawler(client).run()
    assert PORTFOLIO_URL in client.get_calls


def test_fetches_nonce():
    client = _make_client()
    ReachCrawler(client).run()
    assert NONCE_URL in client.get_calls


def test_posts_to_ajax_url():
    client = _make_client()
    ReachCrawler(client).run()
    assert AJAX_URL in client.post_calls


def test_stops_when_ajax_returns_empty():
    # Empty response after first batch — should stop and return 3+2=5 companies
    client = _make_client()
    companies = ReachCrawler(client).run()
    assert len(companies) == 5
    assert len(client.post_calls) == 2  # one real batch + one empty stop


def test_offset_increments_in_ajax_posts():
    client = _make_client(extra_ajax_pages=1)
    ReachCrawler(client).run()
    # First POST: offset=16, second POST: offset=32, third POST (empty stop): offset=48
    assert "args%5Boffset%5D=16" in client.post_data[0]
    assert "args%5Boffset%5D=32" in client.post_data[1]


def test_enrich_false_accepted():
    companies = ReachCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 5


def test_workers_param_accepted():
    companies = ReachCrawler(_make_client()).run(workers=10)
    assert len(companies) == 5
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/python -m pytest tests/test_reach_crawler.py -v
```

Expected: FAIL with `ImportError: cannot import name 'ReachCrawler'`

- [ ] **Step 3: Create crawler**

Create `vc_crawler/crawlers/reach_capital/crawler.py`:

```python
from __future__ import annotations

import json
import logging
import urllib.parse

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company

from .normalizer import normalize
from .parser import AJAX_URL, NONCE_URL, PORTFOLIO_URL, parse_cards

log = logging.getLogger(__name__)

_BATCH_SIZE = 16
_BASE_ARGS: list[tuple[str, str]] = [
    ("args[post_type]", "portfolio"),
    ("args[posts_per_page]", str(_BATCH_SIZE)),
    ("args[post_status]", "publish"),
    ("args[fields]", "ids"),
    ("args[add_args][sector]", "learning"),
    ("args[orderby]", "title"),
    ("args[order]", "ASC"),
    ("args[tax_query][0][taxonomy]", "sector"),
    ("args[tax_query][0][field]", "slug"),
    ("args[tax_query][0][terms]", "learning"),
]


class ReachCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching Reach Capital portfolio page ...")
        resp = self.client.get(PORTFOLIO_URL)
        raw_records = parse_cards(resp.text)
        log.info("Parsed %d companies from page", len(raw_records))

        nonce_resp = self.client.get(NONCE_URL)
        nonce = json.loads(nonce_resp.text)["data"]["nonce"]

        offset = _BATCH_SIZE
        while True:
            data = urllib.parse.urlencode(
                _BASE_ARGS + [
                    ("action", "reach_portfolio_filter"),
                    ("nonce", nonce),
                    ("args[offset]", str(offset)),
                ]
            )
            ajax_resp = self.client.post(
                AJAX_URL,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                },
            )
            if not ajax_resp.text.strip():
                break
            batch = parse_cards(ajax_resp.text)
            if not batch:
                break
            raw_records.extend(batch)
            log.info("Loaded batch at offset %d: %d companies", offset, len(batch))
            offset += _BATCH_SIZE

        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]
        if limit:
            companies = companies[:limit]
        return companies
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
.venv/bin/python -m pytest tests/test_reach_crawler.py -v
```

Expected: all PASS

- [ ] **Step 5: Run full test suite to check for regressions**

```bash
.venv/bin/python -m pytest -v
```

Expected: all existing tests still PASS

- [ ] **Step 6: Commit**

```bash
git add vc_crawler/crawlers/reach_capital/crawler.py tests/test_reach_crawler.py
git commit -m "feat: add Reach Capital crawler"
```

---

## Task 6: Register fund, integration test, and README

**Files:**
- Modify: `vc_crawler/__main__.py`
- Modify: `tests/test_vc_main.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing integration test**

Append to `tests/test_vc_main.py`:

```python
def test_main_writes_reach_capital_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.reach_capital.crawler as rc_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="reach-capital", name="BookNook",
                            slug="booknook",
                            fund_url="https://www.reachcapital.com/companies/?sector=learning")]
    monkeypatch.setattr(rc_mod, "ReachCrawler", Fake)
    rc = cli.main(["--fund", "reach-capital", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "reach-capital" / "companies.json").exists()
    assert (tmp_path / "reach-capital" / "companies.csv").exists()
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/python -m pytest tests/test_vc_main.py::test_main_writes_reach_capital_outputs -v
```

Expected: FAIL with `argument --fund: invalid choice: 'reach-capital'`

- [ ] **Step 3: Register fund in `__main__.py`**

In `vc_crawler/__main__.py`, add one entry to `_FUND_REGISTRY` (after the `"owl-ventures"` line):

```python
_FUND_REGISTRY = {
    "sequoia": "vc_crawler.crawlers.sequoia.crawler.SequoiaCrawler",
    "a16z": "vc_crawler.crawlers.a16z.crawler.A16ZCrawler",
    "a16z-speedrun": "vc_crawler.crawlers.a16z_speedrun.crawler.SpeedrunCrawler",
    "owl-ventures": "vc_crawler.crawlers.owl_ventures.crawler.OwlCrawler",
    "reach-capital": "vc_crawler.crawlers.reach_capital.crawler.ReachCrawler",
}
```

- [ ] **Step 4: Run integration test to verify it passes**

```bash
.venv/bin/python -m pytest tests/test_vc_main.py::test_main_writes_reach_capital_outputs -v
```

Expected: PASS

- [ ] **Step 5: Run full test suite**

```bash
.venv/bin/python -m pytest -v
```

Expected: all PASS

- [ ] **Step 6: Update README.md**

In `README.md`, add a row to the **Supported funds** table (after the Owl Ventures row):

```markdown
| [Reach Capital](https://www.reachcapital.com/companies/?sector=learning) | WordPress AJAX infinite-scroll (Learning sector) | ~95 |
```

Add a usage example in the **Usage** section (after the Owl Ventures example):

```bash
# Crawl Reach Capital Learning portfolio (~95 companies, AJAX pagination)
.venv/bin/python -m vc_crawler --fund reach-capital
```

Add output path in the output files list:

```
- `data/reach-capital/companies.json` / `data/reach-capital/companies.csv`
```

Update the `--fund` flag description in the **All Options** table:

```
| `--fund {sequoia,a16z,a16z-speedrun,owl-ventures,reach-capital}` | *(required)* | Which fund to crawl |
```

Add a **Reach Capital** section under **How It Works**:

```markdown
### Reach Capital
Two-step pipeline:
1. Fetch `https://www.reachcapital.com/companies/?sector=learning` — first 16 companies are in the static HTML
2. Obtain a WordPress nonce via `admin-ajax.php?action=reach_get_nonce`, then POST to `admin-ajax.php` with action `reach_portfolio_filter` and PHP-array-encoded args, incrementing `offset` by 16 until the response is empty

All company data (name, description, website, logo, founded year, leadership) is embedded in the HTML card markup. No detail-page requests needed.
```

- [ ] **Step 7: Commit everything**

```bash
git add vc_crawler/__main__.py tests/test_vc_main.py README.md
git commit -m "release: v2.3.0 Reach Capital Learning portfolio"
```
