# VC Portfolio Crawler

Crawls company portfolio data from venture capital fund websites and exports to JSON and CSV.

**Supported funds:**
| Fund | Source | Companies |
|------|--------|-----------|
| [Sequoia Capital](https://sequoiacap.com/our-companies/) | WordPress REST API + detail pages | ~400 |
| [Andreessen Horowitz (a16z)](https://a16z.com/portfolio/) | JS-embedded JSON in portfolio page | ~840 |
| [a16z Speedrun](https://speedrun.a16z.com/companies/) | Public REST API, cohorts SR001–SR006 | ~240 |
| [Owl Ventures](https://www.owlvc.com/portfolio) | Webflow CMS HTML (single request) | ~92 |
| [Reach Capital](https://www.reachcapital.com/companies/?sector=learning) | WordPress AJAX infinite-scroll (Learning sector) | ~95 |

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

```bash
# Crawl a16z portfolio (single request, all data included)
.venv/bin/python -m vc_crawler --fund a16z

# Crawl Sequoia portfolio (multi-stage: API + detail page enrichment)
.venv/bin/python -m vc_crawler --fund sequoia

# Crawl a16z Speedrun — all cohorts SR001–SR006 (~240 companies)
.venv/bin/python -m vc_crawler --fund a16z-speedrun

# Crawl Owl Ventures portfolio (single request, ~92 EdTech companies)
.venv/bin/python -m vc_crawler --fund owl-ventures

# Crawl Reach Capital Learning portfolio (~95 companies, AJAX pagination)
.venv/bin/python -m vc_crawler --fund reach-capital

# Quick test: first 5 companies, JSON only, verbose logging
.venv/bin/python -m vc_crawler --fund a16z --limit 5 --format json --verbose

# Sequoia index only — skip detail page enrichment (fast)
.venv/bin/python -m vc_crawler --fund sequoia --no-enrich
```

Output files are written to `data/{fund}/`:
- `data/a16z/companies.json` / `data/a16z/companies.csv`
- `data/sequoia/companies.json` / `data/sequoia/companies.csv`
- `data/a16z-speedrun/companies.json` / `data/a16z-speedrun/companies.csv`
- `data/owl-ventures/companies.json` / `data/owl-ventures/companies.csv`
- `data/reach-capital/companies.json` / `data/reach-capital/companies.csv`

### All Options

| Flag | Default | Description |
|------|---------|-------------|
| `--fund {sequoia,a16z,a16z-speedrun,owl-ventures,reach-capital}` | *(required)* | Which fund to crawl |
| `--out DIR` | `data` | Output directory |
| `--format {json,csv,both}` | `both` | Output format(s) |
| `--workers N` | `5` | Enrichment threads (Sequoia only) |
| `--delay SECONDS` | `0.2` | Min spacing between requests |
| `--limit N` | — | Process only the first N companies |
| `--no-enrich` | off | Skip detail page enrichment (Sequoia only) |
| `--verbose` | off | Debug logging |

## Output Schema

Both funds export a unified schema:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Sequential ID (1-based) |
| `fund` | str | `"sequoia"`, `"a16z"`, `"a16z-speedrun"`, `"owl-ventures"`, or `"reach-capital"` |
| `name` | str | Company name |
| `slug` | str | URL-friendly identifier |
| `fund_url` | str | Link to company page on fund site |
| `sectors` | list[str] | Business sectors / verticals |
| `website` | str? | Company website |
| `description` | str? | Short company description |
| `stage` | str? | Current stage (e.g. `"Growth"`, `"IPO"`, `"Acquired"`) or cohort (e.g. `"SR006"` for Speedrun) |
| `stage_year` | int? | Year of exit milestone |
| `founded_year` | int? | Year company was founded |
| `invested_year` | int? | Year the fund invested |
| `logo_url` | str? | Company logo URL |
| `ticker_symbol` | str? | Stock ticker (a16z exits) |
| `acquirer` | str? | Acquiring company (a16z M&A, Owl Ventures) |
| `founders` | list[str]? | Founder names (a16z, Owl Ventures) |

## How It Works

### a16z
Single HTTP request to `https://a16z.com/portfolio/`. All company data is embedded in the page HTML as a JavaScript global (`window.a16z_portfolio_companies`). No JS rendering required.

### a16z Speedrun
Two-step pipeline:
1. Fetch `https://speedrun.a16z.com/companies/` and extract cohort list (SR001–SR006) from embedded `__NEXT_DATA__` JSON — auto-discovers new cohorts when they launch
2. For each cohort paginate `https://speedrun-be.a16z.com/api/companies/companies/?cohort=SRxxx` (public REST API, no auth) until `next` is `null`

All company data (description, industries, founders, website, logo) is returned inline — no detail-page requests needed. The `stage` field holds the cohort name.

### Owl Ventures
Single HTTP request to `https://www.owlvc.com/portfolio`. The site is built on Webflow CMS — all 92 portfolio companies are fully embedded in the static HTML as `div.portfolio-card` elements. No JS rendering required. Each card contains the company name, logo, description, website, education sector tags (Pre K-12, Post-Secondary, Future of Work), acquisition status, founded year, investment round, and founder names.

### Reach Capital
Two-step pipeline:
1. Fetch `https://www.reachcapital.com/companies/?sector=learning` — first 16 companies are in the static HTML
2. Obtain a WordPress nonce via `admin-ajax.php?action=reach_get_nonce`, then POST to `admin-ajax.php` with action `reach_portfolio_filter` and PHP-array-encoded args, incrementing `offset` by 16 until the response is empty

All company data (name, description, website, logo, founded year, leadership) is embedded in the HTML card markup. No detail-page requests needed.

### Sequoia
Multi-stage pipeline:
1. Enumerate companies from the WordPress REST API (`/wp-json/wp/v2/company`)
2. Resolve sector names from the categories taxonomy
3. Fetch the listing page to get Current Stage values
4. Enrich each company from its detail page (website, description, years, logo) — concurrent with configurable workers
5. Validate against the company sitemap

## Extending: Adding a New Fund

1. Create `vc_crawler/crawlers/{fund}/` with `parser.py`, `normalizer.py`, `crawler.py`
2. Implement `class YourCrawler(BaseCrawler)` with `run(*, limit, workers, enrich) -> list[Company]`
3. Add one line to `_FUND_REGISTRY` in `vc_crawler/__main__.py`

See `vc_crawler/crawlers/owl_ventures/` or `vc_crawler/crawlers/a16z_speedrun/` for a minimal single-stage example, or `vc_crawler/crawlers/sequoia/` for a multi-stage enrichment example.

## Tests

```bash
.venv/bin/python -m pytest -v
```
