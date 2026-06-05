# Owl Ventures Crawler — Design Spec

**Date:** 2026-06-05  
**Fund:** Owl Ventures (`owl-ventures`)  
**Source:** https://www.owlvc.com/portfolio

---

## Context

This crawler adds Owl Ventures as a fourth supported fund in the vc-portfolio-crawler project. Owl Ventures is the largest dedicated EdTech VC fund (~$2.2B AUM), making it a high-priority source for EdTech startup discovery. The existing codebase supports Sequoia, a16z, and a16z Speedrun.

---

## Site Analysis

**Stack:** Webflow CMS — static HTML, no JS rendering required.

**Data delivery:** A single GET request to `https://www.owlvc.com/portfolio` returns a ~700KB page containing all 92 portfolio companies fully embedded as HTML (`div.portfolio-card` elements). No pagination, no API keys needed.

**Key HTML landmarks:**
- `div.portfolio-card` — one per company (92 total)
- `.text-block-10` — company name
- `img.image-57[src]` — logo URL
- `.acquired-text` — present without `w-condition-invisible` when company is acquired
- `.text-block-7` — acquirer name (inside hover block)
- `p.porfolio-card-para` — short hover description
- `.pop-up-wrapper` — hidden popup with full data:
  - `.pop-up-left p.text-color-black.mobile-1rem` — full description
  - `a.button.black-bg.width[href]` — company website ("Visit Website")
  - `.pop-up-right-content-holder` sections with titles: Initial Investment, Year Founded, Headquarters, Founder, Co-Founders, CEO
- `div.collection-list-3 > div.w-dyn-list` (first) — subcategory tags (education type)
- `div.collection-list-3 > div.w-dyn-list` (second) — geography tags (discarded)
- `.nest-item-holder a[href]` — portfolio page path (e.g. `/portfolio/amira`)

**Webflow visibility pattern:** Elements hidden due to missing CMS data carry the class `w-condition-invisible`. Parser must skip these.

---

## Architecture

Follows the `a16z_speedrun` pattern (minimal single-stage crawler):

```
vc_crawler/crawlers/owl_ventures/
├── __init__.py
├── crawler.py     — OwlCrawler(BaseCrawler)
├── parser.py      — parse_portfolio_page(html: str) → list[dict]
└── normalizer.py  — normalize(raw: dict, company_id: int) → Company
```

One line added to `_FUND_REGISTRY` in `vc_crawler/__main__.py`:
```python
"owl-ventures": "vc_crawler.crawlers.owl_ventures.crawler.OwlCrawler"
```

Output directory: `data/owl-ventures/`

---

## Data Flow

```
GET https://www.owlvc.com/portfolio  (single request)
    ↓
parse_portfolio_page(html)
    BeautifulSoup → find_all(class_="portfolio-card")
    → list of raw dicts (92 items)
    ↓
[normalize(raw, i) for i, raw in enumerate(raws, start=1)]
    ↓
list[Company]  (92 items)
```

---

## Field Mapping

| `Company` field | HTML source | Notes |
|-----------------|-------------|-------|
| `id` | sequential 1-based | |
| `fund` | `"owl-ventures"` | literal |
| `name` | `.text-block-10` text | |
| `slug` | last path segment of `.nest-item-holder a[href]` | `/portfolio/amira` → `amira` |
| `fund_url` | `https://www.owlvc.com` + href above | |
| `logo_url` | `img.image-57[src]` | CDN URL |
| `description` | popup `.pop-up-left p.text-color-black.mobile-1rem` | full description |
| `website` | popup `a.button.black-bg.width[href]` | "Visit Website" button |
| `sectors` | `.sub-category` in first `w-dyn-list` | Pre K-12 / Post-Secondary / Future of Work; up to 2 per company |
| `stage` | `"Acquired"` when `.acquired-text` lacks `w-condition-invisible`; else `None` | |
| `acquirer` | `.text-block-7` in hover block (acquired companies only) | |
| `founded_year` | "Year Founded" right-panel field → `int` | |
| `invested_year` | regex `\b(19\|20)\d{2}\b` on "Initial Investment" field text | present for ~44/92 |
| `founders` | non-hidden "Founder" + "Co-Founders" right-panel values | `list[str]`, may be empty |
| `stage_year` | `None` | not available |
| `ticker_symbol` | `None` | not available |
| `source_modified` | `None` | not available |

Geography tags (Africa, Asia, Europe, North America, South America) are parsed but discarded — not mapped to any field.

---

## Parser Design (`parser.py`)

```python
PORTFOLIO_URL = "https://www.owlvc.com/portfolio"

def parse_portfolio_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    return [_parse_card(card) for card in soup.find_all(class_="portfolio-card")]

def _parse_card(card) -> dict:
    # name, logo, acquired status, acquirer, short desc
    # popup: full description, website, right-panel fields by title
    # subcategories from first w-dyn-list
    # fund_url from nest-item-holder
    ...
```

Right-panel fields are parsed by matching the `.invaestment-title` text (note: Webflow typo in class name). Fields with `w-condition-invisible` on their `pop-up-right-content-holder` parent are skipped.

---

## Normalizer Design (`normalizer.py`)

```python
FUND_URL_BASE = "https://www.owlvc.com"
YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')

def normalize(raw: dict, company_id: int) -> Company:
    href = raw.get("fund_path", "")
    slug = href.rstrip("/").rsplit("/", 1)[-1]
    ...
```

`invested_year` extracted via `YEAR_RE` on the "Initial Investment" string.  
`founders` built from non-empty "Founder" and "Co-Founders" values combined.

---

## Edge Cases

| Case | Handling |
|------|----------|
| `w-condition-invisible` on any element | Skip that element — Webflow marks missing CMS fields this way |
| Multiple subcategories (e.g. Quizlet: Pre K-12 + Post-Secondary) | Collect all → `sectors` list |
| `Initial Investment` absent or blank | `invested_year = None` |
| `website` missing (some acquired companies) | `None` |
| "Visit Website" href is relative or empty | Normalizer returns `None` |

---

## Tests

Snapshot test with a minimal hand-crafted HTML fixture covering:
- Active company (no acquired status)
- Acquired company (with acquirer name)
- Company with multiple subcategories
- Company with missing optional fields (`w-condition-invisible`)

Located at `tests/crawlers/owl_ventures/`.

---

## Registration

```python
# vc_crawler/__main__.py  — _FUND_REGISTRY
"owl-ventures": "vc_crawler.crawlers.owl_ventures.crawler.OwlCrawler"
```

CLI usage:
```bash
.venv/bin/python -m vc_crawler --fund owl-ventures
.venv/bin/python -m vc_crawler --fund owl-ventures --limit 5 --verbose
```
