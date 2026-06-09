# NewSchools Venture Fund Crawler — Design Spec

**Date:** 2026-06-09  
**Fund:** NewSchools Venture Fund  
**Portfolio URL:** https://www.newschools.org/ventures/

---

## Overview

Add a `new-schools` crawler to the existing `vc-portfolio-crawler` project following the established 3-file pattern (`parser.py` / `normalizer.py` / `crawler.py`). The crawler collects ~300 portfolio companies via 15 paginated listing pages plus optional concurrent detail-page enrichment for description and website.

---

## Site Structure

| Property | Value |
|----------|-------|
| CMS | WordPress + Elementor page builder |
| Listing URL pattern | `/ventures/`, `/ventures/2/`, …, `/ventures/{max_page}/` |
| Items per page | 20 |
| Total pages | 15 (read from `data-max-page` on `.e-load-more-anchor`) |
| Estimated companies | ~300 |
| JS rendering required | No — full HTML in static response |

### Listing card element: `.e-loop-item`

Each card exposes:

| Data | HTML location |
|------|---------------|
| Company name | `.elementor-heading-title` text |
| Detail page URL | first `<a href>` on the card |
| Logo URL | `img[src]` |
| Investment area (text) | `.elementor-post-info__item` text |
| Investment year term IDs | CSS classes matching `investment-year-\d+` |
| Initial investment year term IDs | CSS classes matching `initial-investment-year-\d+` |
| Status (past/current) | presence of `status-past-venture` in CSS classes |

### Detail page: `/venture/{slug}/`

| Data | HTML location |
|------|---------------|
| Description | first `.elementor-widget-text-editor` block with ≥50 chars of text that does not match site navigation text |
| Website URL | first `<a href>` pointing to an external domain (not newschools.org) within the main content area |

### WP REST API (taxonomy term maps)

Both endpoints are publicly accessible without authentication:

| Taxonomy | Endpoint | Fields used |
|----------|----------|-------------|
| `investment-year` | `/wp-json/wp/v2/investment-year?per_page=100` | `id` → `name` (year string) |
| `initial-investment-year` | `/wp-json/wp/v2/initial-investment-year?per_page=100` | `id` → `name` (year string) |

---

## Module Layout

```
vc_crawler/crawlers/new_schools/
├── __init__.py
├── parser.py
├── normalizer.py
└── crawler.py
```

---

## parser.py

```python
PORTFOLIO_URL = "https://www.newschools.org/ventures/"
TERM_API_URL  = "https://www.newschools.org/wp-json/wp/v2/{taxonomy}?per_page=100"
```

### `parse_term_map(json_text: str) -> dict[int, int]`

Parses a WP REST API term list response. Returns `{term_id: year_int}`.

```
input:  '[{"id": 709, "name": "2024", ...}, ...]'
output: {709: 2024, 711: 2022, ...}
```

### `parse_listing_page(html: str) -> tuple[list[dict], int]`

Parses one listing page. Returns `(records, max_page)`.

- `max_page` from `soup.select_one(".e-load-more-anchor")["data-max-page"]` (int); default 1 if element absent.
- For each `.e-loop-item`:
  - `name` — `.elementor-heading-title` text (strip)
  - `fund_url` — `a[href]` (first anchor on card)
  - `slug` — last path segment of `fund_url`
  - `logo_url` — `img[src]` or `None`
  - `sectors` — list of texts from `.elementor-post-info__item` elements
  - `inv_year_ids` — list[int] extracted from `investment-year-(\d+)` class pattern
  - `init_year_ids` — list[int] extracted from `initial-investment-year-(\d+)` class pattern
  - `is_past` — bool, `"status-past-venture" in classes`

### `parse_detail_page(html: str) -> dict`

Parses a venture detail page. Returns `{"description": str|None, "website": str|None}`.

- `description`: iterate `.elementor-widget-text-editor` blocks; take first whose stripped text length ≥ 50 and does not appear in a known navigation blocklist (`["Our Vision", "Our People", ...]`).
- `website`: find `<a href>` whose link text contains "Website" (case-insensitive). Detail pages label the company link "Website →". Return the href of the first match, or `None` if not found.

---

## normalizer.py

### `normalize(listing: dict, detail: dict, inv_map: dict[int,int], init_map: dict[int,int], company_id: int) -> Company`

Field mapping:

| Company field | Source | Rule |
|---|---|---|
| `id` | param | sequential 1-based |
| `fund` | constant | `"new-schools"` |
| `name` | `listing["name"]` | direct |
| `slug` | `listing["slug"]` | strip trailing `/` |
| `fund_url` | `listing["fund_url"]` | detail page URL |
| `sectors` | `listing["sectors"]` | list as-is |
| `logo_url` | `listing["logo_url"]` | `None` if absent |
| `invested_year` | `listing["init_year_ids"][0]` via `init_map` | first initial-investment-year term; `None` if missing |
| `stage` | `listing["is_past"]` | `"Past"` if True, else `None` |
| `description` | `detail["description"]` | `None` if not enriched |
| `website` | `detail["website"]` | `None` if not enriched |
| `stage_year` | — | always `None` (not available) |
| `founded_year` | — | always `None` (not available) |
| `ticker_symbol` | — | always `None` |
| `acquirer` | — | always `None` |
| `founders` | — | always `None` |
| `source_modified` | — | always `None` |

---

## crawler.py — `NewSchoolsCrawler(BaseCrawler)`

### `run(*, limit, workers, enrich) -> list[Company]`

```
1.  GET /wp-json/wp/v2/investment-year?per_page=100       → inv_map
    GET /wp-json/wp/v2/initial-investment-year?per_page=100 → init_map
    (sequential — only 2 requests, PoliteClient delay applies)

2.  GET /ventures/
    → records_page1, max_page

3.  GET /ventures/2/ … /ventures/{max_page}/ (sequential, polite delay)
    → accumulate all listing records

4.  Apply limit (slice records if set)

5.  if enrich:
        ThreadPoolExecutor(max_workers=workers):
            for each record: GET fund_url → parse_detail_page
        → dict keyed by fund_url

6.  for i, record in enumerate(records, 1):
        detail = enrich_map.get(record["fund_url"], {})
        company = normalize(record, detail, inv_map, init_map, i)

7.  return companies
```

The two taxonomy fetches in step 1 are sequential; their combined payload is tiny so parallelism adds no meaningful speedup and avoids PoliteClient contention.

---

## Registration

In `vc_crawler/__main__.py`, add to `_FUND_REGISTRY`:

```python
"new-schools": "vc_crawler.crawlers.new_schools.crawler.NewSchoolsCrawler",
```

---

## Output

- `data/new-schools/companies.json`
- `data/new-schools/companies.csv`

Estimated company count: ~300.

---

## Tests

Follow the existing test pattern. Create `tests/test_new_schools.py` with:

1. `test_parse_term_map` — parse a minimal JSON fixture, assert `{709: 2024}`.
2. `test_parse_listing_page` — parse a minimal HTML fixture with two cards, assert names, slugs, `inv_year_ids`, `is_past`.
3. `test_parse_detail_page` — parse a minimal HTML fixture, assert `description` and `website` extracted correctly.
4. `test_normalize` — call `normalize()` with fixture dicts, assert key fields on the returned `Company`.

---

## Non-goals

- No support for filter parameters (investment area, year) — full portfolio only.
- `financial_model` (for-profit/nonprofit) is available in CSS classes but has no field in the `Company` schema; it is silently dropped.
- `founded_year`, `acquirer`, `founders`, `ticker_symbol` are not present anywhere on the site.
