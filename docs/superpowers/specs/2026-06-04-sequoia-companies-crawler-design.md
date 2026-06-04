# Sequoia Capital Companies Crawler — Design

- **Date:** 2026-06-04
- **Status:** Approved (design), ready for implementation planning
- **Goal:** Spider that collects ALL current companies listed on Sequoia Capital's
  "Our Companies" page (https://sequoiacap.com/our-companies/#all-panel) and exports
  them as structured JSON + CSV.

## 1. Problem & Scope

Parse **all ~490 companies** shown in the "All" panel of Sequoia's Our Companies page,
including those that have IPO'd / been acquired (the full list, not only the active
portfolio). For each company capture identity, sector, external website, description,
and stage data (Current Stage + exit-milestone year).

Out of scope: founders directory, blog/press content, partner funds (SCGE, SCHF, Atlas,
Outliers), non-company post types.

## 2. Key Technical Findings (reconnaissance)

The site is **WordPress + Yoast SEO**; `robots.txt` allows all crawlers
(`User-agent: *` / empty `Disallow:`). Relevant data sources:

- **REST API custom post type `company`:** `https://sequoiacap.com/wp-json/wp/v2/company`
  - Returns clean JSON, paginated. Useful fields per item:
    `id`, `slug`, `link` (Sequoia page URL), `title.rendered`, `categories` (sector
    term IDs), `tags`, `modified`, `class_list`.
  - **`acf` is empty** and there is **no `content`/`excerpt`** → website, description,
    and status are NOT available from this endpoint.
- **Sector taxonomy:** `https://sequoiacap.com/wp-json/wp/v2/categories?per_page=100`
  - 18 sectors, e.g. `189=AI, 196=Fintech, 197=Healthcare, 192=Infrastructure,
    188=Consumer, 199=Crypto, 195=Data & Analytics, 202=Defense, 200=Developer Tools,
    186=GTM, 193=Hardware, 201=Legal, 190=Marketplace, 187=Operations,
    191=Productivity, 198=Security, 194=Climate, 1=Uncategorized`.
  - The `company.categories` IDs map to these sector names.
  - (`tags` taxonomy is mostly blog tags and largely irrelevant for companies; ignored
    except optional passthrough.)
- **Company detail pages** `https://sequoiacap.com/companies/<slug>/` are
  **server-rendered HTML** (no JS needed). They expose the rich fields. Confirmed on
  AdMob:
  - Website: `https://www.admob.com`
  - Description: full paragraph text
  - Exit-milestone year: `Acquired 2010` / `IPO 2019` → only the year is kept as
    `stage_year` (the label duplicates the listing's Current Stage)
  - `Founded 2006`, `Partnered 2006`
  - Sector label (`GTM`)
- **Company directory listing** `https://sequoiacap.com/our-companies/` is a
  **server-rendered FacetWP table** (52 rows/page, paged via `?_paged=N`; page count
  in an inline `window.FWP_JSON` settings blob). Each row exposes a **Current Stage**
  cell — `Pre-Seed/Seed`, `Early`, `Growth`, `Acquired`, `IPO` — which is NOT in the
  REST API (`acf` empty) nor on the detail page. Rows carry the company display name
  (no slug/link), so stage is matched to the REST index by normalized name.
  - Note the distinct "First Partnered" column (e.g. `Early (2003)`); the parser must
    take the Current Stage cell (`td.u-lg-hide[data-order]`), not that one.
- **Completeness cross-check:** `https://sequoiacap.com/company-sitemap.xml` lists
  ~490 company URLs (last modified 2026-06-02).

## 3. Strategy

| Need | Source |
|---|---|
| Full list of all companies (id, name, slug, Sequoia URL, sector IDs) | REST API `/wp-json/wp/v2/company` (paginate, `per_page=100`) |
| Sector ID → name map | REST API `/wp-json/wp/v2/categories` (fetched once) |
| Current Stage (Pre-Seed/Seed, Early, Growth, Acquired, IPO) | HTML of `/our-companies/` (paged `?_paged=N`), matched by name |
| website, description, stage_year (exit year), founded year, partnered year, logo | HTML of `/companies/<slug>/` (plain HTTP GET + HTML parser) |
| Completeness verification | `company-sitemap.xml` count compared to API count |

Rationale: the REST API gives a reliable, fast, paginated index (~5 requests). The
selected output fields (description/website/stage_year) live only in detail-page HTML, so
each company is enriched by fetching its detail page with a plain HTTP GET and parsing
the server-rendered HTML — **no headless browser required**.

## 4. Architecture

Small, single-responsibility modules; each independently testable.

```
sequoia_crawler/
├── http_client.py   # configured requests.Session: User-Agent, timeout,
│                    #   retry + exponential backoff, polite delay
├── api.py           # REST API client: fetch_categories(), iter_companies() (pagination)
├── listing.py       # /our-companies/ pager + parse_stage_map() (name -> Current Stage)
├── detail_parser.py # pure function: detail-page HTML string -> dict of fields
├── enrich.py        # per company: GET detail page -> detail_parser -> merge
├── models.py        # @dataclass Company (schema + to_dict normalization)
├── export.py        # write JSON (nested) and CSV (flat)
└── __main__.py      # CLI entry: orchestration + arguments
tests/               # unit tests over saved HTML/JSON fixtures
requirements.txt
README.md
output/              # results land here
```

- `detail_parser.py` is a **pure function** (HTML → dict) verified against saved
  fixtures (e.g. AdMob page), so parsing logic is tested without network.
- `http_client.py` is the single place that defines HTTP behaviour (retries, timeouts,
  rate limiting, headers).

## 5. Data Flow

1. `api.iter_companies()` walks all pages of the company endpoint → raw company dicts.
   Each company is assigned a **sequential `id` (1, 2, 3, …)** in listing order, not
   the WordPress post id.
2. `api.fetch_categories()` builds `{id: sector_name}`; map each company's
   `categories` IDs to sector names.
3. `listing.fetch_stage_map()` reads `/our-companies/` and sets each company's
   `stage` (Current Stage) by matching on name.
4. `enrich.enrich(company)` GETs `/companies/<slug>/`, runs `detail_parser` to extract
   website / description / stage_year / founded_year / partnered_year /
   logo_url, and merges.
5. Assemble each into a `Company` dataclass; `export` writes `sequoia_companies.json`
   and `sequoia_companies.csv`.
5. Log a summary: API count vs sitemap count, enriched count, error count.

## 6. Output Schema (per company)

```json
{
  "id": 12345,
  "name": "AdMob",
  "slug": "admob",
  "sequoia_url": "https://sequoiacap.com/companies/admob/",
  "sectors": ["GTM"],
  "website": "https://www.admob.com",
  "description": "AdMob built a pay-per-click marketplace...",
  "stage": "Acquired",
  "stage_year": 2010,
  "founded_year": 2006,
  "partnered_year": 2006,
  "logo_url": "https://sequoiacap.com/.../admob-logo.svg",
  "source_modified": "2026-06-02T21:10:47"
}
```

- **JSON:** array of these objects (nested `sectors` list).
- **CSV:** same fields, flat; list fields (`sectors`) joined with `;`.
- Any field absent on a given page → `null` / empty string. Missing data never aborts
  the run.

## 7. Reliability & Politeness

- **Retry + exponential backoff** on HTTP 429 / 5xx (urllib3 `Retry`); per-request
  timeouts.
- **Rate limiting:** small inter-request delay + a modest thread pool
  (default 4–6 workers) for the ~490 detail pages — fast but courteous. `robots.txt`
  permits crawling.
- **Error isolation:** a single failed detail page is logged and skipped; it does not
  fail the whole run. The company still appears with index-level fields populated.
- **CLI flags:**
  - `--no-enrich` — index only (API), fast, skips detail pages
  - `--limit N` — process only N companies (for quick testing)
  - `--workers N` — enrichment concurrency (default 5)
  - `--out DIR` — output directory (default `output/`)
  - `--format {json,csv,both}` — default `both`
  - `--verbose` — debug logging

## 8. Testing (TDD)

- `detail_parser` — parse a saved fixture (AdMob HTML); assert every field, including
  gracefully-missing ones.
- `api` — pagination logic against mocked paged responses; category map building.
- `export` — JSON and CSV correctness on a small sample of `Company` objects.
- `models` — `to_dict` / CSV-flattening normalization.
- Optional: one live smoke test behind a `--run-live` / env flag (needs network).

## 9. Dependencies & Environment Constraint

- **Dependencies:** `requests`, `beautifulsoup4`, `lxml`. Installed in a virtualenv.
- **Environment constraint:** the local Bash sandbox here has **no outbound network**
  (verified — `curl` is blocked). Logic is therefore verified via unit tests over saved
  fixtures. A real end-to-end run against the live site requires network: either the
  user runs `! python -m sequoia_crawler ...` in-session, or Bash is run with the
  sandbox disabled for that single verification step.

## 10. Decisions (resolved during brainstorming)

- Approach: **WordPress REST API** for the index (not headless browser); detail pages
  fetched via plain HTTP for the rich fields.
- Scope: **all companies in the All panel (~490)**, including IPO'd / acquired.
- Fields: identity (sequential id) + sector + stage (+ exit year) + description +
  remaining detail-page fields
  (website, logo, founded/partnered years).
- Output: **JSON + CSV**.
