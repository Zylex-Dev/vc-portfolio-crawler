# Sequoia Capital Companies Crawler

Collects all companies listed on
[Sequoia's Our Companies page](https://sequoiacap.com/our-companies/#all-panel)
and exports them to JSON and CSV.

## How it works

1. Enumerates the full company list from the WordPress REST API
   (`/wp-json/wp/v2/company`, paginated).
2. Resolves sector names from the categories taxonomy.
3. Enriches each company from its server-rendered detail page
   (`/companies/<slug>/`): website, description, status, founded/partnered years, logo.
4. Writes `output/companies.json` and `output/companies.csv`.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

```bash
# Full crawl (index + enrichment) -> output/companies.json + .csv
.venv/bin/python -m sequoia_crawler

# Index only (fast, no detail pages)
.venv/bin/python -m sequoia_crawler --no-enrich

# Quick test on 5 companies, JSON only, verbose
.venv/bin/python -m sequoia_crawler --limit 5 --format json --verbose
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--out DIR` | `output` | Output directory |
| `--format {json,csv,both}` | `both` | Output format(s) |
| `--workers N` | `5` | Enrichment concurrency |
| `--delay SECONDS` | `0.2` | Min spacing between request starts |
| `--limit N` | — | Process only the first N companies |
| `--no-enrich` | off | Index only; skip detail pages |
| `--verbose` | off | Debug logging |

## Tests

```bash
.venv/bin/python -m pytest -v
```
