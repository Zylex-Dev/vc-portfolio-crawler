# Design: a16z Speedrun Crawler

**Date:** 2026-06-05  
**Fund:** a16z speedrun — seed-stage accelerator (AI, games, media, etc.)  
**Source site:** https://speedrun.a16z.com/companies/

---

## Overview

Add `a16z-speedrun` as a new fund in the vc_crawler project. Crawls ~240 portfolio companies across all cohorts (SR001–SR006) from a public REST API.

---

## Architecture

Follows the existing `crawlers/{fund}/` pattern:

```
vc_crawler/crawlers/a16z_speedrun/
    __init__.py
    parser.py       # HTML page parse (cohort list) + API pagination
    normalizer.py   # raw API dict → Company
    crawler.py      # SpeedrunCrawler(BaseCrawler)
```

Registered in `_FUND_REGISTRY` in `vc_crawler/__main__.py`:
```python
"a16z-speedrun": "vc_crawler.crawlers.a16z_speedrun.crawler.SpeedrunCrawler"
```

Output files: `output/a16z-speedrun_companies.json` / `.csv`

---

## Data Source

### Step 1 — Discover cohorts (single HTML request)

`GET https://speedrun.a16z.com/companies/`

Extract `<script id="__NEXT_DATA__">` JSON:
```json
{
  "props": {
    "pageProps": {
      "cohorts": [{"name": "SR001"}, ..., {"name": "SR006"}]
    }
  }
}
```

This auto-discovers future cohorts (SR007, SR008, etc.) without code changes.

### Step 2 — Paginate per cohort (JSON API, no auth)

`GET https://speedrun-be.a16z.com/api/companies/companies/?cohort=SR001&limit=50&offset=0&ordering=name`

Response shape:
```json
{
  "count": 25,
  "next": "...?cohort=SR001&limit=50&offset=50&ordering=name",
  "previous": null,
  "results": [...]
}
```

Repeat while `next != null`. No detail-page fetches required — all data is present in the list API response.

### Known cohorts and company counts (as of 2026-06-05)

| Cohort | Companies |
|--------|-----------|
| SR001  | 25        |
| SR002  | 25        |
| SR003  | 32        |
| SR004  | 41        |
| SR005  | 58        |
| SR006  | 59        |
| **Total** | **~240** |

---

## Field Mapping

| API field | Company field | Notes |
|-----------|---------------|-------|
| (sequential) | `id` | 1-based, across all cohorts |
| — | `fund` | `"a16z-speedrun"` |
| `name` | `name` | |
| `slug` | `slug` | |
| — | `fund_url` | `"https://speedrun.a16z.com/companies/{slug}"` |
| `industries` | `sectors` | list of strings |
| `website_url` | `website` | |
| `description` | `description` | full text (not `preamble`) |
| `cohort` | `stage` | `"SR001"` … `"SR006"` |
| — | `stage_year` | `None` |
| `founded_year` | `founded_year` | |
| — | `invested_year` | `None` (not in API) |
| `logo` | `logo_url` | |
| — | `source_modified` | `None` |
| — | `ticker_symbol` | `None` |
| — | `acquirer` | `None` |
| `founder_set[].first_name + last_name` | `founders` | joined with space |

`stage` is repurposed to hold the cohort identifier — semantically different from Growth/IPO/Acquired but makes cohort queryable in exports.

`preamble` (short pitch teaser) is intentionally ignored; `description` contains the full company description and is the more complete field.

---

## Module Responsibilities

### `parser.py`

- `PORTFOLIO_URL = "https://speedrun.a16z.com/companies/"`
- `API_BASE = "https://speedrun-be.a16z.com/api/companies/companies/"`
- `parse_portfolio_page(html: str) -> list[str]` — extracts cohort names from `__NEXT_DATA__`
- `fetch_cohort(client, cohort: str, limit: int = 50) -> list[dict]` — paginates API, returns all raw records for a cohort

### `normalizer.py`

- `normalize(raw: dict, company_id: int) -> Company` — maps API dict to Company dataclass
- `_make_slug(name: str) -> str` — fallback slug from name (API provides slug already)
- `_founders(founder_set: list) -> list[str]` — joins first + last name

### `crawler.py`

- `class SpeedrunCrawler(BaseCrawler)`
- `run(*, limit, workers, enrich) -> list[Company]`
  1. Fetch portfolio page → cohort list
  2. For each cohort: `fetch_cohort()` → accumulate records
  3. Normalize all records with sequential IDs (cohorts in discovery order SR001→SR006; within each cohort, API `ordering=name`)
  4. Apply `limit` if set
  5. `workers` and `enrich` params accepted but unused (single-stage, no enrichment needed)

---

## Error Handling

- `__NEXT_DATA__` not found → `ValueError` with descriptive message (mirrors a16z parser)
- API returns empty `results` for a cohort → `log.warning`, continue to next cohort
- HTTP errors → handled by `PoliteClient` retry logic (existing)

---

## Tests

```
tests/
    fixtures/
        speedrun_portfolio.html     # __NEXT_DATA__ with 2 cohorts (SR001, SR002), ~5 companies each
        speedrun_api_sr001.json     # one-page API response for SR001 (3 companies, next=null)
        speedrun_api_sr002_p1.json  # first page for SR002 (2 companies, next=URL)
        speedrun_api_sr002_p2.json  # second page for SR002 (1 company, next=null)
    test_speedrun_parser.py     # parse_portfolio_page, fetch_cohort pagination
    test_speedrun_normalizer.py # field mapping, founders join, None defaults
    test_speedrun_crawler.py    # SpeedrunCrawler with FakeClient, limit, IDs
```

`tests/test_vc_main.py` extended to include `a16z-speedrun` in the fund registry assertions.

---

## CLI

No new flags required. Uses existing interface:

```bash
# Crawl all cohorts (full portfolio)
.venv/bin/python -m vc_crawler --fund a16z-speedrun

# Quick test: first 5 companies, verbose
.venv/bin/python -m vc_crawler --fund a16z-speedrun --limit 5 --verbose
```

`--no-enrich` and `--workers` flags are silently ignored (no enrichment stage).
