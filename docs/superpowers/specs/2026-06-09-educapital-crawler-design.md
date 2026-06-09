# EduCapital Crawler — Design Spec
_Date: 2026-06-09_

## Overview

Add a crawler for EduCapital (`https://www.educapitalvc.com/portfolio`) that extracts all 41 portfolio companies from a single static Webflow CMS page and saves them to `data/edu-capital/`.

## Site Analysis

- **Type:** Webflow CMS, static HTML (no JS rendering required)
- **Source URL:** `https://www.educapitalvc.com/portfolio`
- **Company count:** 41 (confirmed via scrape)
- **No individual company pages** (confirmed via sitemap)
- **Company name not available as text** — derived from website URL domain

### HTML Structure per company card

```
div.portfolio_content.w-dyn-item
  div.portfolio_card
    div.tag.is-portfolio          # "Acquired" label; hidden when w-condition-invisible present
    img.portfolio_logo[src]       # logo CDN URL
    p.text-color-purple           # description/tagline
    div[fs-cmsfilter-field=category]  # "Future of work" | "Future of education"
    a.portfolio_card-back[href]   # external company website URL
```

## Architecture

Follows the established 3-file pattern (parser / normalizer / crawler):

```
vc_crawler/crawlers/edu_capital/
  __init__.py
  parser.py       # parse_portfolio_page(html) → list[dict]
  normalizer.py   # normalize(raw, id) → Company
  crawler.py      # EduCapitalCrawler(BaseCrawler).run()
```

Registry key: `"edu-capital"` in `__main__.py`.  
Output directory: `data/edu-capital/`.

## Components

### parser.py

- `PORTFOLIO_URL = "https://www.educapitalvc.com/portfolio"`
- `parse_portfolio_page(html: str) -> list[dict]`
  - Selects all `.portfolio_content.w-dyn-item` elements
  - Per item extracts:
    - `logo_url`: `img.portfolio_logo` → `src` attribute
    - `description`: `p.text-color-purple` → stripped text
    - `category`: `[fs-cmsfilter-field="category"]` → stripped text
    - `website`: first `a.portfolio_card-back[href]` (deduplicated)
    - `acquired`: True if `.tag.is-portfolio` exists **without** `w-condition-invisible` class

### normalizer.py

- `normalize(raw: dict, company_id: int) -> Company`
- `name`: `_name_from_url(website)` — strips `www.`/subdomain, removes TLD, result as-is lowercase (e.g. `360learning.com` → `"360learning"`, `buddy.ai` → `"buddy"`, `apps.apple.com/fr/app/emma-parler-anglais/...` → `"emma"` from URL path slug)
- `slug`: standard `_slugify(name)`
- `fund`: `"edu-capital"`
- `fund_url`: `PORTFOLIO_URL`
- `sectors`: `[raw["category"]]` when category present, else `[]`
- `description`: `raw["description"]`
- `stage`: `"Acquired"` if `raw["acquired"]` else `None`
- `logo_url`: `raw["logo_url"]`
- All date/financial fields: `None` (not available on site)

### crawler.py

- `EduCapitalCrawler(BaseCrawler).run(*, limit, workers, enrich) -> list[Company]`
- Single GET to `PORTFOLIO_URL`
- Calls `parse_portfolio_page` → `normalize` for each record
- Applies `limit` slice if set
- Ignores `workers` and `enrich` (no detail pages, no enrichment needed)

## Tests

| File | What it covers |
|------|----------------|
| `tests/fixtures/educapital_portfolio.html` | Snapshot of live page |
| `tests/test_educapital_parser.py` | 41 records parsed; spot-check fields for 3 companies; acquired flag |
| `tests/test_educapital_normalizer.py` | name derivation, Apple URL edge case, stage=Acquired, sectors list |
| `tests/test_educapital_crawler.py` | mocked HTTP client, returns list[Company], limit respected |

## CLI Usage

```bash
python -m vc_crawler --fund edu-capital
python -m vc_crawler --fund edu-capital --format csv --limit 5
```
