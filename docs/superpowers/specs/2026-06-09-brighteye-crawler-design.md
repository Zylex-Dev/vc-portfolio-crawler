# BrightEye Ventures Crawler — Design

**Date:** 2026-06-09  
**Fund URL:** https://www.brighteyevc.com/portfolio  
**Status:** Approved

---

## Architecture

Same 3-file pattern as all other fund crawlers:

```
vc_crawler/crawlers/brighteye/
├── __init__.py
├── crawler.py      # BrighteyeCrawler(BaseCrawler)
├── parser.py       # parse_portfolio_page(html) → list[dict]
└── normalizer.py   # normalize(raw, id) → Company
```

Registered in `__main__.py` as `"brighteye": "vc_crawler.crawlers.brighteye.crawler.BrighteyeCrawler"`.

---

## Site Structure

- **Platform:** Webflow CMS, server-side rendered — no JS execution required
- **Total companies:** 51 portfolio cards on one page (no pagination)
- **Featured section:** 4 companies with richer modal-popup data (name, description, category)
- **Main grid:** 51 companies including the 4 featured ones

---

## Parser

`parse_portfolio_page(html: str) → list[dict]`

**Step 1 — Extract featured data (4 companies):**
- Selector: `.featured-companies-collection-item`
- Name: `.heading-style-h4` inside modal
- Description: `.featured-portfolio-description`
- Categories: `.dark-chip:not(.is-outline) .sub-head-small` (deduped)
- Website: `a.is-tertiary.is-icon[href]`
- Build lookup dict keyed by website URL

**Step 2 — Extract all 51 portfolio cards:**
- Selector: `.portfolio-companies-collection-item`
- Slug: `a[href*="/portfolio-companies/"]` → last path segment
- Location: `.dark-chip.is-outline .sub-head-small`
- Logo: `img.portfolio-card-logo[src]`
- Website: `a.is-tertiary.is-icon[href]`
- Exit status: `.exit-tag` visible when no `w-condition-invisible` class

**Step 3 — Merge:**
- If card website matches a featured entry → attach name, description, categories

---

## Normalizer

`normalize(raw: dict, company_id: int) → Company`

| Company field | Source |
|---|---|
| `id` | sequence counter |
| `fund` | `"brighteye"` |
| `name` | featured name or `_slug_to_name(slug)` |
| `slug` | slug with `-copy` suffix removed |
| `fund_url` | `https://www.brighteyevc.com/portfolio` |
| `sectors` | categories list from featured, else `[]` |
| `website` | card website URL |
| `description` | featured description or `None` |
| `stage` | `"Exited"` if exit tag visible, else `None` |
| `logo_url` | `img.portfolio-card-logo[src]` |
| `stage_year` | `None` |
| `founded_year` | `None` |
| `invested_year` | `None` |
| `source_modified` | `None` |
| `ticker_symbol` | `None` |
| `acquirer` | `None` |
| `founders` | `None` |

**`_slug_to_name(slug)`:** strip `-copy` suffix → split on `-` → Title Case each word.

---

## Crawler

`BrighteyeCrawler(BaseCrawler).run(limit, workers, enrich)` — single GET, no enrichment loop (all data on one page).

---

## Tests

- `tests/fixtures/brighteye_portfolio.html` — saved snapshot of live page
- `tests/test_brighteye_parser.py` — unit tests for `parse_portfolio_page`
- `tests/test_brighteye_normalizer.py` — unit tests for `normalize` and `_slug_to_name`
- `tests/test_brighteye_crawler.py` — crawler integration test with mocked HTTP client
