# Owl Ventures Crawler Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Owl Ventures as a fourth supported fund by parsing all 92 portfolio companies from a single GET to `https://www.owlvc.com/portfolio`.

**Architecture:** Single-stage Webflow HTML scraper following the `a16z_speedrun` pattern — one GET request, BeautifulSoup parsing of embedded `div.portfolio-card` elements, normalizer mapping raw dicts to Company objects. No pagination, no API keys.

**Tech Stack:** Python 3.10+, `requests`, `beautifulsoup4` (already in requirements.txt)

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `vc_crawler/crawlers/owl_ventures/__init__.py` | Package marker |
| Create | `vc_crawler/crawlers/owl_ventures/parser.py` | HTML → list[dict] |
| Create | `vc_crawler/crawlers/owl_ventures/normalizer.py` | dict → Company |
| Create | `vc_crawler/crawlers/owl_ventures/crawler.py` | BaseCrawler subclass |
| Create | `tests/fixtures/owl_ventures_portfolio.html` | 4-company fixture |
| Create | `tests/test_owl_parser.py` | Parser unit tests |
| Create | `tests/test_owl_normalizer.py` | Normalizer unit tests |
| Create | `tests/test_owl_crawler.py` | Crawler integration tests |
| Modify | `vc_crawler/__main__.py` | Register "owl-ventures" |
| Modify | `tests/test_vc_main.py` | CLI smoke test |

---

## Task 1: HTML fixture

**Files:**
- Create: `tests/fixtures/owl_ventures_portfolio.html`

This fixture covers four cases: active company (full data), acquired company, company with multiple sectors, company with missing optional fields (Webflow's `w-condition-invisible` pattern).

- [ ] **Step 1.1: Create the fixture file**

```html
<!DOCTYPE html>
<html>
<body>

<!-- Company 1: Amira Learning — active, Pre K-12, full data, has co-founder -->
<div class="portfolio-card border-b-l" fs-list-field="*">
 <img alt="" class="image-57" src="https://cdn.example.com/amira.svg"/>
 <div class="text-block-10">Amira Learning</div>
 <div class="portfolio-card-content">
  <div class="portfolio-card-hover-content-holder">
   <div class="w-condition-invisible">
    <div class="text-block-6 w-condition-invisible">Acquired</div>
    <div class="text-block-6 w-condition-invisible">Acquired By :</div>
    <div class="text-block-7 w-dyn-bind-empty"></div>
   </div>
   <p class="porfolio-card-para">Reinventing learning to read.</p>
  </div>
 </div>
 <div class="acquired-text w-condition-invisible">Acquired</div>
 <div class="pop-up-wrapper" style="display:none;opacity:0">
  <div class="pop-up-content-wrapper">
   <div class="pop-up-top">
    <div class="w-condition-invisible">
     <div class="pop-up-acquired w-condition-invisible">Acquired</div>
     <div class="pop-up-acquired w-condition-invisible">Acquired By :</div>
     <div class="text-block-7 _1 w-dyn-bind-empty"></div>
    </div>
    <div class="collection-list-3">
     <div class="w-dyn-list">
      <div class="collection-list-3 w-dyn-items" role="list">
       <div class="w-dyn-item" role="listitem"><div class="sub-category">Pre K-12</div></div>
      </div>
     </div>
     <div class="w-dyn-list">
      <div class="collection-list-3 w-dyn-items" role="list">
       <div class="w-dyn-item" role="listitem"><div class="sub-category">North America</div></div>
      </div>
     </div>
    </div>
   </div>
   <div class="pop-up-wrap">
    <div class="pop-up-left">
     <div class="div-block-29">
      <div class="portfolio-name">Amira Learning</div>
      <p class="text-color-black mobile-1rem">Amira listens to young students read aloud and provides real-time tutoring.</p>
     </div>
     <div class="pop-up-buttons-wrapper">
      <a class="button black-bg width w-inline-block" href="https://amiralearning.com/" target="_blank"><div>Visit Website</div></a>
      <a class="button transparent width w-inline-block" href="https://amiralearning.com/news" target="_blank"><div>Read Press Release</div></a>
     </div>
    </div>
    <div class="pop-up-right">
     <div class="pop-up-right-content-holder _1">
      <div class="invaestment-title">Initial Investment</div>
      <p class="text-color-black font-size-1rem">Led Series A in 2019</p>
     </div>
     <div class="pop-up-right-content-holder">
      <div class="invaestment-title">Year Founded</div>
      <p class="text-color-black font-size-1rem">2017</p>
     </div>
     <div class="pop-up-right-content-holder">
      <div class="invaestment-title">Headquarters</div>
      <p class="text-color-black font-size-1rem">San Francisco Bay Area</p>
     </div>
     <div class="pop-up-right-content-holder w-condition-invisible">
      <div class="invaestment-title">Founder</div>
      <p class="text-color-black font-size-1rem w-dyn-bind-empty"></p>
     </div>
     <div class="pop-up-right-content-holder">
      <div class="invaestment-title">Co-Founders</div>
      <p class="text-color-black font-size-1rem">Pete Jungwirth</p>
     </div>
    </div>
   </div>
  </div>
 </div>
 <div class="nest-item-holder">
  <a class="w-inline-block" href="/portfolio/amira"><div></div></a>
 </div>
</div>

<!-- Company 2: Abl — acquired by BetterLesson -->
<div class="portfolio-card border-b-l" fs-list-field="*">
 <img alt="" class="image-57" src="https://cdn.example.com/abl.svg"/>
 <div class="text-block-10">Abl</div>
 <div class="portfolio-card-content">
  <div class="portfolio-card-hover-content-holder">
   <div>
    <div class="text-block-6 w-condition-invisible">Acquired</div>
    <div class="text-block-6">Acquired By :</div>
    <div class="text-block-7">BetterLesson</div>
   </div>
   <p class="porfolio-card-para">Helping school leaders manage their time.</p>
  </div>
 </div>
 <div class="acquired-text">Acquired</div>
 <div class="pop-up-wrapper" style="display:none;opacity:0">
  <div class="pop-up-content-wrapper">
   <div class="pop-up-top">
    <div>
     <div class="pop-up-acquired w-condition-invisible">Acquired</div>
     <div class="pop-up-acquired">Acquired By :</div>
     <div class="text-block-7 _1">BetterLesson</div>
    </div>
    <div class="collection-list-3">
     <div class="w-dyn-list">
      <div class="collection-list-3 w-dyn-items" role="list">
       <div class="w-dyn-item" role="listitem"><div class="sub-category">Pre K-12</div></div>
      </div>
     </div>
     <div class="w-dyn-list">
      <div class="collection-list-3 w-dyn-items" role="list">
       <div class="w-dyn-item" role="listitem"><div class="sub-category">North America</div></div>
      </div>
     </div>
    </div>
   </div>
   <div class="pop-up-wrap">
    <div class="pop-up-left">
     <div class="div-block-29">
      <div class="portfolio-name">Abl</div>
      <p class="text-color-black mobile-1rem">Abl offers a cloud-based platform for school scheduling.</p>
     </div>
     <div class="pop-up-buttons-wrapper">
      <a class="button black-bg width w-inline-block" href="https://www.ablschools.com/" target="_blank"><div>Visit Website</div></a>
     </div>
    </div>
    <div class="pop-up-right">
     <div class="pop-up-right-content-holder _1">
      <div class="invaestment-title">Initial Investment</div>
      <p class="text-color-black font-size-1rem">Led Series A in 2016</p>
     </div>
     <div class="pop-up-right-content-holder">
      <div class="invaestment-title">Year Founded</div>
      <p class="text-color-black font-size-1rem">2015</p>
     </div>
     <div class="pop-up-right-content-holder">
      <div class="invaestment-title">Founder</div>
      <p class="text-color-black font-size-1rem">Adam Pisoni</p>
     </div>
    </div>
   </div>
  </div>
 </div>
 <div class="nest-item-holder">
  <a class="w-inline-block" href="/portfolio/abl"><div></div></a>
 </div>
</div>

<!-- Company 3: Quizlet — multiple sectors (Pre K-12 + Post-Secondary), no investment info -->
<div class="portfolio-card border-b-l" fs-list-field="*">
 <img alt="" class="image-57" src="https://cdn.example.com/quizlet.svg"/>
 <div class="text-block-10">Quizlet</div>
 <div class="portfolio-card-content">
  <div class="portfolio-card-hover-content-holder">
   <div class="w-condition-invisible">
    <div class="text-block-6 w-condition-invisible">Acquired</div>
    <div class="text-block-6 w-condition-invisible">Acquired By :</div>
    <div class="text-block-7 w-dyn-bind-empty"></div>
   </div>
   <p class="porfolio-card-para">Helping students study and memorize anything.</p>
  </div>
 </div>
 <div class="acquired-text w-condition-invisible">Acquired</div>
 <div class="pop-up-wrapper" style="display:none;opacity:0">
  <div class="pop-up-content-wrapper">
   <div class="pop-up-top">
    <div class="w-condition-invisible">
     <div class="pop-up-acquired w-condition-invisible">Acquired</div>
     <div class="pop-up-acquired w-condition-invisible">Acquired By :</div>
     <div class="text-block-7 _1 w-dyn-bind-empty"></div>
    </div>
    <div class="collection-list-3">
     <div class="w-dyn-list">
      <div class="collection-list-3 w-dyn-items" role="list">
       <div class="w-dyn-item" role="listitem"><div class="sub-category">Pre K-12</div></div>
       <div class="w-dyn-item" role="listitem"><div class="sub-category">Post-Secondary</div></div>
      </div>
     </div>
     <div class="w-dyn-list">
      <div class="collection-list-3 w-dyn-items" role="list">
       <div class="w-dyn-item" role="listitem"><div class="sub-category">North America</div></div>
      </div>
     </div>
    </div>
   </div>
   <div class="pop-up-wrap">
    <div class="pop-up-left">
     <div class="div-block-29">
      <div class="portfolio-name">Quizlet</div>
      <p class="text-color-black mobile-1rem">Quizlet makes studying tools that help students practice and master what they are learning.</p>
     </div>
     <div class="pop-up-buttons-wrapper">
      <a class="button black-bg width w-inline-block" href="https://quizlet.com/" target="_blank"><div>Visit Website</div></a>
     </div>
    </div>
    <div class="pop-up-right">
     <div class="pop-up-right-content-holder w-condition-invisible">
      <div class="invaestment-title">Initial Investment</div>
      <p class="text-color-black font-size-1rem w-dyn-bind-empty"></p>
     </div>
     <div class="pop-up-right-content-holder">
      <div class="invaestment-title">Year Founded</div>
      <p class="text-color-black font-size-1rem">2005</p>
     </div>
     <div class="pop-up-right-content-holder w-condition-invisible">
      <div class="invaestment-title">Co-Founders</div>
      <p class="text-color-black font-size-1rem w-dyn-bind-empty"></p>
     </div>
    </div>
   </div>
  </div>
 </div>
 <div class="nest-item-holder">
  <a class="w-inline-block" href="/portfolio/quizlet"><div></div></a>
 </div>
</div>

<!-- Company 4: Apna — Future of Work, Asia, no investment, no founders -->
<div class="portfolio-card border-b-l" fs-list-field="*">
 <img alt="" class="image-57" src="https://cdn.example.com/apna.svg"/>
 <div class="text-block-10">Apna</div>
 <div class="portfolio-card-content">
  <div class="portfolio-card-hover-content-holder">
   <div class="w-condition-invisible">
    <div class="text-block-6 w-condition-invisible">Acquired</div>
    <div class="text-block-6 w-condition-invisible">Acquired By :</div>
    <div class="text-block-7 w-dyn-bind-empty"></div>
   </div>
   <p class="porfolio-card-para">Professional networking and jobs platform in India.</p>
  </div>
 </div>
 <div class="acquired-text w-condition-invisible">Acquired</div>
 <div class="pop-up-wrapper" style="display:none;opacity:0">
  <div class="pop-up-content-wrapper">
   <div class="pop-up-top">
    <div class="w-condition-invisible">
     <div class="pop-up-acquired w-condition-invisible">Acquired</div>
     <div class="pop-up-acquired w-condition-invisible">Acquired By :</div>
     <div class="text-block-7 _1 w-dyn-bind-empty"></div>
    </div>
    <div class="collection-list-3">
     <div class="w-dyn-list">
      <div class="collection-list-3 w-dyn-items" role="list">
       <div class="w-dyn-item" role="listitem"><div class="sub-category">Future of Work</div></div>
      </div>
     </div>
     <div class="w-dyn-list">
      <div class="collection-list-3 w-dyn-items" role="list">
       <div class="w-dyn-item" role="listitem"><div class="sub-category">Asia</div></div>
      </div>
     </div>
    </div>
   </div>
   <div class="pop-up-wrap">
    <div class="pop-up-left">
     <div class="div-block-29">
      <div class="portfolio-name">Apna</div>
      <p class="text-color-black mobile-1rem">India's largest professional networking and jobs platform for blue- and grey-collar workers.</p>
     </div>
     <div class="pop-up-buttons-wrapper">
      <a class="button black-bg width w-inline-block" href="https://apna.co/" target="_blank"><div>Visit Website</div></a>
     </div>
    </div>
    <div class="pop-up-right">
     <div class="pop-up-right-content-holder w-condition-invisible">
      <div class="invaestment-title">Initial Investment</div>
      <p class="text-color-black font-size-1rem w-dyn-bind-empty"></p>
     </div>
     <div class="pop-up-right-content-holder">
      <div class="invaestment-title">Year Founded</div>
      <p class="text-color-black font-size-1rem">2019</p>
     </div>
     <div class="pop-up-right-content-holder w-condition-invisible">
      <div class="invaestment-title">Founder</div>
      <p class="text-color-black font-size-1rem w-dyn-bind-empty"></p>
     </div>
     <div class="pop-up-right-content-holder w-condition-invisible">
      <div class="invaestment-title">Co-Founders</div>
      <p class="text-color-black font-size-1rem w-dyn-bind-empty"></p>
     </div>
    </div>
   </div>
  </div>
 </div>
 <div class="nest-item-holder">
  <a class="w-inline-block" href="/portfolio/apna"><div></div></a>
 </div>
</div>

</body>
</html>
```

Save to `tests/fixtures/owl_ventures_portfolio.html`.

- [ ] **Step 1.2: Commit the fixture**

```bash
git add tests/fixtures/owl_ventures_portfolio.html
git commit -m "test: add Owl Ventures HTML fixture (4 companies)"
```

---

## Task 2: Parser

**Files:**
- Create: `vc_crawler/crawlers/owl_ventures/parser.py`
- Create: `tests/test_owl_parser.py`

- [ ] **Step 2.1: Write failing parser tests**

Create `tests/test_owl_parser.py`:

```python
from pathlib import Path
import pytest
from vc_crawler.crawlers.owl_ventures.parser import (
    PORTFOLIO_URL,
    parse_portfolio_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "owl_ventures_portfolio.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://www.owlvc.com/portfolio"


def test_returns_list_of_dicts():
    result = parse_portfolio_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_four_companies():
    assert len(parse_portfolio_page(FIXTURE)) == 4


def test_empty_page_returns_empty_list():
    assert parse_portfolio_page("<html><body></body></html>") == []


# --- name ---

def test_active_company_name():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["name"] == "Amira Learning"


def test_acquired_company_name():
    result = parse_portfolio_page(FIXTURE)
    assert result[1]["name"] == "Abl"


# --- acquired / acquirer ---

def test_active_company_not_acquired():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["is_acquired"] is False


def test_acquired_company_flag():
    result = parse_portfolio_page(FIXTURE)
    assert result[1]["is_acquired"] is True


def test_acquirer_set_for_acquired():
    result = parse_portfolio_page(FIXTURE)
    assert result[1]["acquirer"] == "BetterLesson"


def test_acquirer_none_for_active():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["acquirer"] is None


# --- logo ---

def test_logo_url():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["logo_url"] == "https://cdn.example.com/amira.svg"


# --- description ---

def test_description():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["description"] == "Amira listens to young students read aloud and provides real-time tutoring."


# --- website ---

def test_website():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["website"] == "https://amiralearning.com/"


def test_website_not_press_release():
    # "Visit Website" must be chosen over "Read Press Release"
    result = parse_portfolio_page(FIXTURE)
    assert "news" not in (result[0]["website"] or "")


# --- fund_path ---

def test_fund_path():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["fund_path"] == "/portfolio/amira"


def test_fund_path_abl():
    result = parse_portfolio_page(FIXTURE)
    assert result[1]["fund_path"] == "/portfolio/abl"


# --- sectors ---

def test_single_sector():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["sectors"] == ["Pre K-12"]


def test_multiple_sectors():
    result = parse_portfolio_page(FIXTURE)
    # Quizlet is index 2 — Pre K-12 + Post-Secondary
    assert result[2]["sectors"] == ["Pre K-12", "Post-Secondary"]


def test_different_sector():
    result = parse_portfolio_page(FIXTURE)
    # Apna is index 3 — Future of Work
    assert result[3]["sectors"] == ["Future of Work"]


# --- investment / founded year ---

def test_initial_investment_string():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["initial_investment"] == "Led Series A in 2019"


def test_initial_investment_none_when_hidden():
    result = parse_portfolio_page(FIXTURE)
    # Quizlet and Apna have w-condition-invisible on Initial Investment
    assert result[2]["initial_investment"] is None
    assert result[3]["initial_investment"] is None


def test_founded_year_string():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["founded_year_str"] == "2017"


# --- founders ---

def test_founders_collected():
    result = parse_portfolio_page(FIXTURE)
    # Amira has Co-Founders: Pete Jungwirth
    assert "Pete Jungwirth" in result[0]["founders"]


def test_founders_empty_when_all_hidden():
    result = parse_portfolio_page(FIXTURE)
    # Apna has all founder fields hidden
    assert result[3]["founders"] == []
```

- [ ] **Step 2.2: Run tests — expect ImportError (module does not exist yet)**

```bash
.venv/bin/python -m pytest tests/test_owl_parser.py -v 2>&1 | head -20
```

Expected: `ImportError: No module named 'vc_crawler.crawlers.owl_ventures'`

- [ ] **Step 2.3: Create the package skeleton**

Create `vc_crawler/crawlers/owl_ventures/__init__.py` (empty):

```python
```

- [ ] **Step 2.4: Implement `parser.py`**

Create `vc_crawler/crawlers/owl_ventures/parser.py`:

```python
from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.owlvc.com/portfolio"


def parse_portfolio_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    return [_parse_card(card) for card in soup.find_all(class_="portfolio-card")]


def _parse_card(card) -> dict:
    raw: dict = {}

    name_el = card.find(class_="text-block-10")
    raw["name"] = name_el.get_text(strip=True) if name_el else ""

    logo_el = card.find("img", class_="image-57")
    raw["logo_url"] = logo_el.get("src") or None if logo_el else None

    acq_el = card.find(class_="acquired-text")
    raw["is_acquired"] = bool(acq_el and "w-condition-invisible" not in acq_el.get("class", []))

    acq_name_el = card.find(class_="text-block-7")
    raw["acquirer"] = (
        acq_name_el.get_text(strip=True) or None
        if raw["is_acquired"] and acq_name_el
        else None
    )

    popup = card.find(class_="pop-up-wrapper")
    raw.update(_parse_popup(popup) if popup else _empty_popup())

    nest = card.find(class_="nest-item-holder")
    link = nest.find("a") if nest else None
    raw["fund_path"] = link.get("href", "") if link else ""

    return raw


def _parse_popup(popup) -> dict:
    out: dict = {"description": None, "website": None,
                 "initial_investment": None, "founded_year_str": None,
                 "founders": [], "sectors": []}

    pop_left = popup.find(class_="pop-up-left")
    if pop_left:
        desc_el = pop_left.find("p", class_="text-color-black")
        out["description"] = desc_el.get_text(strip=True) or None if desc_el else None

        website_el = pop_left.find("a", class_="black-bg")
        out["website"] = website_el.get("href") or None if website_el else None

    for holder in popup.find_all(class_="pop-up-right-content-holder"):
        if "w-condition-invisible" in holder.get("class", []):
            continue
        title_el = holder.find(class_="invaestment-title")
        val_el = holder.find("p")
        if not title_el or not val_el:
            continue
        title = title_el.get_text(strip=True)
        val = val_el.get_text(strip=True)
        if not val:
            continue
        if title == "Initial Investment":
            out["initial_investment"] = val
        elif title == "Year Founded":
            out["founded_year_str"] = val
        elif title in ("Founder", "Co-Founders"):
            out["founders"].append(val)

    popup_top = popup.find(class_="pop-up-top")
    if popup_top:
        outer = popup_top.find("div", class_="collection-list-3")
        if outer:
            dyn_lists = outer.find_all("div", class_="w-dyn-list", recursive=False)
            if dyn_lists:
                out["sectors"] = [
                    el.get_text(strip=True)
                    for el in dyn_lists[0].find_all("div", class_="sub-category")
                ]

    return out


def _empty_popup() -> dict:
    return {"description": None, "website": None,
            "initial_investment": None, "founded_year_str": None,
            "founders": [], "sectors": []}
```

- [ ] **Step 2.5: Run parser tests — expect all to pass**

```bash
.venv/bin/python -m pytest tests/test_owl_parser.py -v
```

Expected: all tests PASS.

- [ ] **Step 2.6: Commit**

```bash
git add vc_crawler/crawlers/owl_ventures/__init__.py \
        vc_crawler/crawlers/owl_ventures/parser.py \
        tests/test_owl_parser.py
git commit -m "feat: add Owl Ventures HTML parser"
```

---

## Task 3: Normalizer

**Files:**
- Create: `vc_crawler/crawlers/owl_ventures/normalizer.py`
- Create: `tests/test_owl_normalizer.py`

- [ ] **Step 3.1: Write failing normalizer tests**

Create `tests/test_owl_normalizer.py`:

```python
from vc_crawler.crawlers.owl_ventures.normalizer import normalize
from vc_crawler.models import Company


def _amira():
    return {
        "name": "Amira Learning",
        "logo_url": "https://cdn.example.com/amira.svg",
        "is_acquired": False,
        "acquirer": None,
        "description": "Amira listens to young students read aloud.",
        "website": "https://amiralearning.com/",
        "initial_investment": "Led Series A in 2019",
        "founded_year_str": "2017",
        "founders": ["Pete Jungwirth"],
        "sectors": ["Pre K-12"],
        "fund_path": "/portfolio/amira",
    }


def _abl():
    return {
        "name": "Abl",
        "logo_url": "https://cdn.example.com/abl.svg",
        "is_acquired": True,
        "acquirer": "BetterLesson",
        "description": "Abl offers a cloud-based platform for school scheduling.",
        "website": "https://www.ablschools.com/",
        "initial_investment": "Led Series A in 2016",
        "founded_year_str": "2015",
        "founders": ["Adam Pisoni"],
        "sectors": ["Pre K-12"],
        "fund_path": "/portfolio/abl",
    }


def _apna():
    return {
        "name": "Apna",
        "logo_url": "https://cdn.example.com/apna.svg",
        "is_acquired": False,
        "acquirer": None,
        "description": "India's largest professional networking platform.",
        "website": "https://apna.co/",
        "initial_investment": None,
        "founded_year_str": "2019",
        "founders": [],
        "sectors": ["Future of Work"],
        "fund_path": "/portfolio/apna",
    }


# --- basic ---

def test_returns_company_instance():
    assert isinstance(normalize(_amira(), 1), Company)


def test_fund_is_owl_ventures():
    assert normalize(_amira(), 1).fund == "owl-ventures"


def test_id_assigned():
    assert normalize(_amira(), 42).id == 42


def test_name():
    assert normalize(_amira(), 1).name == "Amira Learning"


# --- slug / fund_url ---

def test_slug_from_path():
    assert normalize(_amira(), 1).slug == "amira"


def test_slug_abl():
    assert normalize(_abl(), 1).slug == "abl"


def test_fund_url():
    assert normalize(_amira(), 1).fund_url == "https://www.owlvc.com/portfolio/amira"


# --- sectors ---

def test_sectors_single():
    assert normalize(_amira(), 1).sectors == ["Pre K-12"]


def test_sectors_future_of_work():
    assert normalize(_apna(), 1).sectors == ["Future of Work"]


# --- website / description ---

def test_website():
    assert normalize(_amira(), 1).website == "https://amiralearning.com/"


def test_website_none_when_missing():
    raw = _amira()
    raw["website"] = None
    assert normalize(raw, 1).website is None


def test_description():
    assert normalize(_amira(), 1).description == "Amira listens to young students read aloud."


# --- stage / acquirer ---

def test_stage_none_when_active():
    assert normalize(_amira(), 1).stage is None


def test_stage_acquired_when_acquired():
    assert normalize(_abl(), 1).stage == "Acquired"


def test_acquirer_set():
    assert normalize(_abl(), 1).acquirer == "BetterLesson"


def test_acquirer_none_when_active():
    assert normalize(_amira(), 1).acquirer is None


# --- years ---

def test_founded_year():
    assert normalize(_amira(), 1).founded_year == 2017


def test_founded_year_abl():
    assert normalize(_abl(), 1).founded_year == 2015


def test_founded_year_none_when_missing():
    raw = _amira()
    raw["founded_year_str"] = None
    assert normalize(raw, 1).founded_year is None


def test_invested_year_from_investment_string():
    assert normalize(_amira(), 1).invested_year == 2019


def test_invested_year_abl():
    assert normalize(_abl(), 1).invested_year == 2016


def test_invested_year_from_plain_year_string():
    raw = _amira()
    raw["initial_investment"] = "2025"
    assert normalize(raw, 1).invested_year == 2025


def test_invested_year_none_when_no_investment():
    assert normalize(_apna(), 1).invested_year is None


# --- logo ---

def test_logo_url():
    assert normalize(_amira(), 1).logo_url == "https://cdn.example.com/amira.svg"


def test_logo_url_none_when_missing():
    raw = _amira()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


# --- founders ---

def test_founders():
    assert normalize(_amira(), 1).founders == ["Pete Jungwirth"]


def test_founders_none_when_empty():
    assert normalize(_apna(), 1).founders is None


def test_founders_multiple():
    raw = _amira()
    raw["founders"] = ["Alice Smith", "Bob Jones"]
    assert normalize(raw, 1).founders == ["Alice Smith", "Bob Jones"]


# --- always-None fields ---

def test_stage_year_none():
    assert normalize(_amira(), 1).stage_year is None


def test_ticker_symbol_none():
    assert normalize(_amira(), 1).ticker_symbol is None


def test_source_modified_none():
    assert normalize(_amira(), 1).source_modified is None
```

- [ ] **Step 3.2: Run tests — expect ImportError**

```bash
.venv/bin/python -m pytest tests/test_owl_normalizer.py -v 2>&1 | head -10
```

Expected: `ImportError: cannot import name 'normalize'`

- [ ] **Step 3.3: Implement `normalizer.py`**

Create `vc_crawler/crawlers/owl_ventures/normalizer.py`:

```python
from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

FUND_URL_BASE = "https://www.owlvc.com"
_YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')


def normalize(raw: dict, company_id: int) -> Company:
    href = raw.get("fund_path", "")
    slug = href.rstrip("/").rsplit("/", 1)[-1] if href else ""
    founders = raw.get("founders") or []

    return Company(
        id=company_id,
        fund="owl-ventures",
        name=raw.get("name", ""),
        slug=slug,
        fund_url=f"{FUND_URL_BASE}{href}" if href else "",
        sectors=raw.get("sectors") or [],
        website=raw.get("website") or None,
        description=raw.get("description") or None,
        stage="Acquired" if raw.get("is_acquired") else None,
        stage_year=None,
        founded_year=_parse_int(raw.get("founded_year_str")),
        invested_year=_parse_year(raw.get("initial_investment")),
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=raw.get("acquirer") or None,
        founders=founders if founders else None,
    )


def _parse_year(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    m = _YEAR_RE.search(text)
    return int(m.group()) if m else None


def _parse_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    try:
        return int(text.strip())
    except ValueError:
        return None
```

- [ ] **Step 3.4: Run normalizer tests — expect all to pass**

```bash
.venv/bin/python -m pytest tests/test_owl_normalizer.py -v
```

Expected: all tests PASS.

- [ ] **Step 3.5: Commit**

```bash
git add vc_crawler/crawlers/owl_ventures/normalizer.py \
        tests/test_owl_normalizer.py
git commit -m "feat: add Owl Ventures normalizer"
```

---

## Task 4: Crawler, registration, and CLI test

**Files:**
- Create: `vc_crawler/crawlers/owl_ventures/crawler.py`
- Create: `tests/test_owl_crawler.py`
- Modify: `vc_crawler/__main__.py` — add one line to `_FUND_REGISTRY`
- Modify: `tests/test_vc_main.py` — add CLI smoke test

- [ ] **Step 4.1: Write failing crawler tests**

Create `tests/test_owl_crawler.py`:

```python
from pathlib import Path
from vc_crawler.crawlers.owl_ventures.crawler import OwlCrawler
from vc_crawler.models import Company

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "owl_ventures_portfolio.html"


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
    companies = OwlCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    assert len(OwlCrawler(_make_client()).run()) == 4


def test_sequential_ids():
    companies = OwlCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3, 4]


def test_all_fund_owl_ventures():
    companies = OwlCrawler(_make_client()).run()
    assert all(c.fund == "owl-ventures" for c in companies)


def test_limit_truncates():
    companies = OwlCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = OwlCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    OwlCrawler(client).run()
    assert any("owlvc.com/portfolio" in u for u in client.calls)


def test_enrich_false_accepted():
    companies = OwlCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 4


def test_workers_param_accepted():
    companies = OwlCrawler(_make_client()).run(workers=10)
    assert len(companies) == 4
```

- [ ] **Step 4.2: Run tests — expect ImportError**

```bash
.venv/bin/python -m pytest tests/test_owl_crawler.py -v 2>&1 | head -10
```

Expected: `ImportError: cannot import name 'OwlCrawler'`

- [ ] **Step 4.3: Implement `crawler.py`**

Create `vc_crawler/crawlers/owl_ventures/crawler.py`:

```python
from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company
from .parser import PORTFOLIO_URL, parse_portfolio_page
from .normalizer import normalize

log = logging.getLogger(__name__)


class OwlCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching Owl Ventures portfolio page ...")
        resp = self.client.get(PORTFOLIO_URL)
        raw_records = parse_portfolio_page(resp.text)
        log.info("Parsed %d companies", len(raw_records))

        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]

        if limit:
            companies = companies[:limit]
        return companies
```

- [ ] **Step 4.4: Run crawler tests — expect all to pass**

```bash
.venv/bin/python -m pytest tests/test_owl_crawler.py -v
```

Expected: all tests PASS.

- [ ] **Step 4.5: Register the fund in `__main__.py`**

In `vc_crawler/__main__.py`, add one line to `_FUND_REGISTRY`:

```python
_FUND_REGISTRY = {
    "sequoia": "vc_crawler.crawlers.sequoia.crawler.SequoiaCrawler",
    "a16z": "vc_crawler.crawlers.a16z.crawler.A16ZCrawler",
    "a16z-speedrun": "vc_crawler.crawlers.a16z_speedrun.crawler.SpeedrunCrawler",
    "owl-ventures": "vc_crawler.crawlers.owl_ventures.crawler.OwlCrawler",
}
```

- [ ] **Step 4.6: Add CLI smoke test to `tests/test_vc_main.py`**

Append to `tests/test_vc_main.py`:

```python
def test_main_writes_owl_ventures_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.owl_ventures.crawler as owl_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="owl-ventures", name="Amira Learning",
                            slug="amira", fund_url="https://www.owlvc.com/portfolio/amira")]
    monkeypatch.setattr(owl_mod, "OwlCrawler", Fake)
    rc = cli.main(["--fund", "owl-ventures", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "owl-ventures" / "companies.json").exists()
    assert (tmp_path / "owl-ventures" / "companies.csv").exists()
```

- [ ] **Step 4.7: Run the full test suite — expect all to pass**

```bash
.venv/bin/python -m pytest -v
```

Expected: all existing tests PASS plus the new owl tests.

- [ ] **Step 4.8: Final commit**

```bash
git add vc_crawler/crawlers/owl_ventures/crawler.py \
        vc_crawler/__main__.py \
        tests/test_owl_crawler.py \
        tests/test_vc_main.py
git commit -m "feat: add Owl Ventures portfolio crawler"
```
