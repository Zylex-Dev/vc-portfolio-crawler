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
and status/milestone data.

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
  - Status / milestone: `Acquired 2010` (also seen as `IPO`, `Public`, year suffix)
  - `Founded 2006`, `Partnered 2006`
  - Sector label (`GTM`)
- **Completeness cross-check:** `https://sequoiacap.com/company-sitemap.xml` lists
  ~490 company URLs (last modified 2026-06-02).

## 3. Strategy

| Need | Source |
|---|---|
| Full list of all companies (id, name, slug, Sequoia URL, sector IDs) | REST API `/wp-json/wp/v2/company` (paginate, `per_page=100`) |
| Sector ID → name map | REST API `/wp-json/wp/v2/categories` (fetched once) |
| website, description, status(+year), founded year, partnered year, logo | HTML of `/companies/<slug>/` (plain HTTP GET + HTML parser) |
| Completeness verification | `company-sitemap.xml` count compared to API count |

Rationale: the REST API gives a reliable, fast, paginated index (~5 requests). The
selected output fields (description/status/website) live only in detail-page HTML, so
each company is enriched by fetching its detail page with a plain HTTP GET and parsing
the server-rendered HTML — **no headless browser required**.

## 4. Architecture

Small, single-responsibility modules; each independently testable.

```
sequoia_crawler/
├── http_client.py   # configured requests.Session: User-Agent, timeout,
│                    #   retry + exponential backoff, polite delay
├── api.py           # REST API client: fetch_categories(), iter_companies() (pagination)
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
2. `api.fetch_categories()` builds `{id: sector_name}`; map each company's
   `categories` IDs to sector names.
3. `enrich.enrich(company)` GETs `/companies/<slug>/`, runs `detail_parser` to extract
   website / description / status / status_year / founded_year / partnered_year /
   logo_url, and merges.
4. Assemble each into a `Company` dataclass; `export` writes `companies.json` and
   `companies.csv`.
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
  "status": "Acquired",
  "status_year": 2010,
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
- Fields: identity + sector + status + description + remaining detail-page fields
  (website, logo, founded/partnered years).
- Output: **JSON + CSV**.
