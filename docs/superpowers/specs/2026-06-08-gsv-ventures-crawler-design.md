# GSV Ventures Crawler — Design Spec

**Date:** 2026-06-08  
**Fund:** GSV Ventures (`gsv-ventures`)  
**Source:** `https://gsv.ventures/portfolio/`  
**Companies:** ~87

---

## 1. Website Analysis

### Data loading method
Fully static HTML — all 87 companies are embedded in a single GET request to the portfolio page. No AJAX, no pagination, no JavaScript rendering required. Identical loading model to Owl Ventures.

### HTML structure (per card)
```
div.c-grid--item.fund{N}                   ← fund class: fund1 / fund2 / fund3
├── div.c-grid--item-image
│   └── img.lazyload[data-src]             ← small logo URL
└── div.c-grid--item-content
    ├── div.c-grid--item-hero
    │   └── img.lazyload[data-src]         ← hero image (ignored)
    └── div.c-grid--item-copy
        ├── main
        │   ├── div.company-tags
        │   │   ├── span.company-name      ← company name
        │   │   └── span.company-location  ← city/country (not in model)
        │   ├── h2                         ← tagline / short description
        │   ├── p                          ← longer description (optional)
        │   └── p > a[href]                ← company website ("Learn more")
        └── aside > ul.company-info
            ├── "Founders/Leadership"      ← comma-separated founder names
            ├── "Investment"               ← e.g. "Seed, 2020"
            ├── "Year Founded"             ← e.g. "2019"
            └── "Segment"                  ← e.g. "Pre-K-12"
```

**Fund distribution:** fund1=28, fund2=26, fund3=29 (87 total).  
Some cards have no `aside` section — all `company-info` fields are optional.

---

## 2. Field Mapping

| `Company` field   | Source                                                    |
|-------------------|-----------------------------------------------------------|
| `fund`            | `"gsv-ventures"` (constant)                               |
| `name`            | `span.company-name`                                       |
| `slug`            | `slugify(name)` — lowercase, non-alnum → `-`             |
| `fund_url`        | `https://gsv.ventures/portfolio/` (no individual pages)   |
| `sectors`         | `company-info` "Segment" → `[value]` or `[]`             |
| `website`         | `<a href>` in "Learn more" paragraph                      |
| `description`     | First non-learn-more `<p>`, fallback to `<h2>` text       |
| `stage`           | Stage part of "Investment" (e.g. `"Seed"` from `"Seed, 2020"`) |
| `invested_year`   | Year part of "Investment" (e.g. `2020` from `"Seed, 2020"`) |
| `founded_year`    | `company-info` "Year Founded" → `int`                     |
| `logo_url`        | `img.lazyload[data-src]` inside `.c-grid--item-image`     |
| `founders`        | `company-info` "Founders/Leadership" split by `,`         |
| `stage_year`      | `None` (not available)                                    |
| `ticker_symbol`   | `None` (not available)                                    |
| `acquirer`        | `None` (not available)                                    |
| `source_modified` | `None` (not available)                                    |

---

## 3. Architecture

Pattern: **single-stage, no enrichment** — identical to `owl_ventures`.

```
GSVCrawler.run()
  → client.get(PORTFOLIO_URL)          # one HTTP request
  → parse_portfolio_page(html)         # list[dict] of raw records
  → normalize(raw, i) for each record  # list[Company]
  → return companies[:limit]
```

### Modules

| File | Responsibility |
|------|----------------|
| `parser.py` | `parse_portfolio_page(html) -> list[dict]`; `_parse_card(card) -> dict` |
| `normalizer.py` | `normalize(raw, id) -> Company`; `_slugify()`; `_parse_investment()` |
| `crawler.py` | `class GSVCrawler(BaseCrawler)` |
| `__init__.py` | empty |

### `_parse_investment(text)` logic
Input: `"Seed, 2020"` | `"Series A, 2018"` | `None`  
Output: `(stage: str|None, year: int|None)`  
- Split on `,`, strip whitespace
- Stage = first part if non-empty
- Year = extract `\b(19|20)\d{2}\b` from remaining text

### `_slugify(name)` logic
`re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')`

---

## 4. Files to Create / Modify

**New files:**
```
vc_crawler/crawlers/gsv_ventures/__init__.py
vc_crawler/crawlers/gsv_ventures/parser.py
vc_crawler/crawlers/gsv_ventures/normalizer.py
vc_crawler/crawlers/gsv_ventures/crawler.py
tests/fixtures/gsv_ventures_portfolio.html
tests/test_gsv_parser.py
tests/test_gsv_normalizer.py
tests/test_gsv_crawler.py
```

**Modified files:**
```
vc_crawler/__main__.py          ← add "gsv-ventures" to _FUND_REGISTRY
tests/test_vc_main.py           ← add test_main_writes_gsv_ventures_outputs
README.md                       ← add fund to table, usage, output schema, how-it-works
```

---

## 5. Test Strategy

Each module has its own test file backed by a minimal HTML fixture (`gsv_ventures_portfolio.html`) with 3 representative cards:
- **Card A** — full data (name, description, founders, investment, year, segment, logo, website)
- **Card B** — minimal data (only name + tagline, no aside)
- **Card C** — multiple founders, no description paragraph (only h2 tagline)

**Parser tests:** URL constant, returns list of dicts, count, empty page, field values per card.  
**Normalizer tests:** Company instance, fund constant, id, name, slug, fund_url, sectors, website, description fallback, stage, invested_year, founded_year, logo_url, founders, None fields.  
**Crawler tests:** returns Company instances, count, limit, sequential ids, fund constant, correct URL fetched.  
**main tests:** `test_main_writes_gsv_ventures_outputs` added to `test_vc_main.py`.
