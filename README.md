# VC Portfolio Crawler

Crawls company portfolio data from venture capital fund websites and exports to JSON and CSV.

**Supported funds:**
| Fund | Source | Companies |
|------|--------|-----------|
| [Sequoia Capital](https://sequoiacap.com/our-companies/) | WordPress REST API + detail pages | ~400 |
| [Andreessen Horowitz (a16z)](https://a16z.com/portfolio/) | JS-embedded JSON in portfolio page | ~840 |

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

# Quick test: first 5 companies, JSON only, verbose logging
.venv/bin/python -m vc_crawler --fund a16z --limit 5 --format json --verbose

# Sequoia index only — skip detail page enrichment (fast)
.venv/bin/python -m vc_crawler --fund sequoia --no-enrich
```

Output files are written to `output/`:
- `output/a16z_companies.json` / `output/a16z_companies.csv`
- `output/sequoia_companies.json` / `output/sequoia_companies.csv`

### All Options

| Flag | Default | Description |
|------|---------|-------------|
| `--fund {sequoia,a16z}` | *(required)* | Which fund to crawl |
| `--out DIR` | `output` | Output directory |
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
| `fund` | str | `"sequoia"` or `"a16z"` |
| `name` | str | Company name |
| `slug` | str | URL-friendly identifier |
| `fund_url` | str | Link to company page on fund site |
| `sectors` | list[str] | Business sectors / verticals |
| `website` | str? | Company website |
| `description` | str? | Short company description |
| `stage` | str? | Current stage (e.g. `"Growth"`, `"IPO"`, `"Acquired"`) |
| `stage_year` | int? | Year of exit milestone |
| `founded_year` | int? | Year company was founded |
| `invested_year` | int? | Year the fund invested |
| `logo_url` | str? | Company logo URL |
| `ticker_symbol` | str? | Stock ticker (a16z exits) |
| `acquirer` | str? | Acquiring company (a16z M&A) |
| `founders` | list[str]? | Founder names (a16z) |

## How It Works

### a16z
Single HTTP request to `https://a16z.com/portfolio/`. All company data is embedded in the page HTML as a JavaScript global (`window.a16z_portfolio_companies`). No JS rendering required.

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

## Tests

```bash
.venv/bin/python -m pytest -v
```
