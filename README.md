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
| [GSV Ventures](https://gsv.ventures/portfolio/) | Static HTML (single request) | ~87 |
| [Learn Capital](https://learn.vc/ventures) | Next.js `__NEXT_DATA__` JSON (single request) | ~78 |
| [BrightEye Ventures](https://www.brighteyevc.com/portfolio) | Webflow CMS HTML (single request) | ~51 |
| [EduCapital](https://www.educapitalvc.com/portfolio) | Webflow CMS HTML (single request) | ~41 |
| [NewSchools Venture Fund](https://www.newschools.org/ventures/) | WordPress + Elementor paginated HTML + detail pages | ~300 |
| [Y Combinator](https://www.ycombinator.com/companies?industry=Education) | Algolia REST API (public, single request) | ~125 |

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

# Crawl GSV Ventures portfolio (~87 companies, single static-HTML request)
.venv/bin/python -m vc_crawler --fund gsv-ventures

# Crawl Learn Capital portfolio (~78 companies, single Next.js page request)
.venv/bin/python -m vc_crawler --fund learn-capital

# Crawl BrightEye Ventures portfolio (~51 companies, single Webflow request)
.venv/bin/python -m vc_crawler --fund brighteye

# Crawl EduCapital portfolio (~41 companies, single Webflow request)
.venv/bin/python -m vc_crawler --fund edu-capital

# Crawl NewSchools Venture Fund portfolio (~300 companies, paginated HTML + detail enrichment)
.venv/bin/python -m vc_crawler --fund new-schools

# Crawl Y Combinator Education portfolio (~125 companies, single Algolia API request)
.venv/bin/python -m vc_crawler --fund y-combinator

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
- `data/gsv-ventures/companies.json` / `data/gsv-ventures/companies.csv`
- `data/learn-capital/companies.json` / `data/learn-capital/companies.csv`
- `data/brighteye/companies.json` / `data/brighteye/companies.csv`
- `data/edu-capital/companies.json` / `data/edu-capital/companies.csv`
- `data/new-schools/companies.json` / `data/new-schools/companies.csv`
- `data/y-combinator/companies.json` / `data/y-combinator/companies.csv`

### All Options

| Flag | Default | Description |
|------|---------|-------------|
| `--fund {sequoia,a16z,a16z-speedrun,owl-ventures,reach-capital,gsv-ventures,learn-capital,brighteye,edu-capital,new-schools,y-combinator}` | *(required)* | Which fund to crawl |
| `--out DIR` | `data` | Output directory |
| `--format {json,csv,both}` | `both` | Output format(s) |
| `--workers N` | `5` | Enrichment threads (Sequoia, NewSchools) |
| `--delay SECONDS` | `0.2` | Min spacing between requests |
| `--limit N` | — | Process only the first N companies |
| `--no-enrich` | off | Skip detail page enrichment (Sequoia, NewSchools) |
| `--verbose` | off | Debug logging |

## Output Schema

Both funds export a unified schema:

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Sequential ID (1-based) |
| `fund` | str | `"sequoia"`, `"a16z"`, `"a16z-speedrun"`, `"owl-ventures"`, `"reach-capital"`, `"gsv-ventures"`, `"learn-capital"`, `"brighteye"`, `"edu-capital"`, `"new-schools"`, or `"y-combinator"` |
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

### GSV Ventures
Single HTTP request to `https://gsv.ventures/portfolio/`. All ~87 portfolio companies are fully embedded in the static HTML as `div.c-grid--item` elements — no JS rendering required. Each card contains the company name, logo (`img.lazyload[data-src]`), tagline (`h2`), optional description (`p`), website ("Learn more" link), and a `ul.company-info` aside with investment round, year founded, segment, and founders/leadership.

### Learn Capital
Single HTTP request to `https://learn.vc/ventures`. The site is built with Next.js + Prismic CMS — all ~78 portfolio companies are embedded in the page as `props.pageProps.ventures` inside a `<script id="__NEXT_DATA__">` JSON blob. No JS rendering required. Each venture record contains name, logo URL (`color_logo.url`), description, headline, website (`visit.url`), sector tags, founder names, and acquisition/IPO status flags.

### BrightEye Ventures
Single HTTP request to `https://www.brighteyevc.com/portfolio`. The site is built on Webflow CMS — all ~51 portfolio companies are embedded in the static HTML as `.portfolio-companies-collection-item` elements. No JS rendering required.

The page has two tiers of data: 4 featured companies (with modals containing full name, description, and sector tags) and a full grid of all 51 companies (with slug, logo, location, website, and exit status). The parser merges featured data into the grid by matching on website URL. Company names for non-featured cards are derived from the URL slug (Title Case, with Webflow `-copy` suffixes stripped).

### EduCapital
Single HTTP request to `https://www.educapitalvc.com/portfolio`. The site is built on Webflow CMS — all 41 portfolio companies are embedded in the static HTML as `.portfolio_content.w-dyn-item` elements. No JS rendering required.

Each card contains a logo, tagline, category (`Future of education` or `Future of work`), company website link, and an acquisition status tag. The HTML contains no text company name — names are derived from the website domain (`360learning.com` → `"360learning"`, `buddy.ai` → `"buddy"`). For Apple App Store links the app slug is used (`/app/emma-parler-anglais/…` → `"emma"`).

### NewSchools Venture Fund
Multi-stage pipeline:
1. Fetch the initial-investment-year taxonomy from the public WP REST API (`/wp-json/wp/v2/initial-investment-year`) — maps WordPress term IDs to calendar years
2. Paginate all listing pages at `/ventures/`, `/ventures/2/`, … — the total page count is read dynamically from the `.e-load-more-anchor[data-max-page]` attribute on page 1, so new pages are picked up automatically. Each page is static HTML with `.e-loop-item` cards containing company name, logo, investment area, and investment/initial-year term IDs in CSS classes
3. Concurrently fetch each venture's detail page (`/venture/{slug}/`) for description and website URL (skipped with `--no-enrich`)

### Sequoia
Multi-stage pipeline:
1. Enumerate companies from the WordPress REST API (`/wp-json/wp/v2/company`)
2. Resolve sector names from the categories taxonomy
3. Fetch the listing page to get Current Stage values
4. Enrich each company from its detail page (website, description, years, logo) — concurrent with configurable workers
5. Validate against the company sitemap

### Y Combinator
Single HTTP POST to the Algolia REST API (`https://45bwzj1sgc-dsn.algolia.net/1/indexes/YCCompany_production/query`) with filter `industries:Education` and `hitsPerPage=1000`. The public Algolia key is embedded in the YC companies page HTML (`window.AlgoliaOpts`). All ~125 EdTech company records are returned inline — no pagination or detail-page requests needed.

## Extending: Adding a New Fund

1. Create `vc_crawler/crawlers/{fund}/` with `parser.py`, `normalizer.py`, `crawler.py`
2. Implement `class YourCrawler(BaseCrawler)` with `run(*, limit, workers, enrich) -> list[Company]`
3. Add one line to `_FUND_REGISTRY` in `vc_crawler/__main__.py`

See `vc_crawler/crawlers/owl_ventures/` or `vc_crawler/crawlers/a16z_speedrun/` for a minimal single-stage example, or `vc_crawler/crawlers/sequoia/` for a multi-stage enrichment example.

## PMO Analyzer

Scores all startups in `data/all_companies.csv` against the **PMO (Персонализированная Модель Образования)** framework using DeepSeek API. Each startup gets a `pmo_score` (0–10) and sub-scores for 5 instruments: trajectory, materials, collaboration, gamification, feedback.

**Cost:** ~2348 startups via `deepseek-v4-pro` (reasoning enabled), concurrency 10. Reasoning mode costs more per call than the earlier flash run.

### Prerequisites

Скопируй `.env.example` в `.env` и вставь свой ключ:

```bash
cp .env.example .env
# открой .env и заполни DEEPSEEK_API_KEY=sk-...
```

Получить ключ: [platform.deepseek.com](https://platform.deepseek.com) → API Keys.

### Score all startups

```bash
.venv/bin/python -m pmo_analyzer.scorer
```

Reads `data/all_companies.csv` and sends one prompt per startup (name + sectors + stage + description) to `deepseek-v4-pro` (reasoning enabled) concurrently, merges the scores into the source rows, and writes **only** `data/all_companies_pmo.csv`.

### Output columns added

| Column | Type | Description |
|--------|------|-------------|
| `pmo_score` | float | Average of 5 sub-scores (0–10) |
| `pmo_traj` | int | Персонализированная Траектория |
| `pmo_mat` | int | Учебные Материалы |
| `pmo_collab` | int | Совместная Деятельность |
| `pmo_game` | int | Геймификация и Визуализация |
| `pmo_feedback` | int | Обратная Связь |
| `pmo_notes` | str | One-sentence reasoning (Russian) |

Rows with `pmo_score == -1` are API/parse errors — re-run or review manually.

## Agent Matcher

Сопоставляет EdTech-стартапы из `data/edu_companies_pmo.csv` с каталогом из **44 наших ИИ-агентов** (`data/agents.json`, сгруппированы по 5 средствам ПМО). Каждому стартапу назначается один наиболее подходящий агент (жёсткий матч — `relevance ≥ 7`), либо он попадает в группу `unmatched` («новые идеи / решения, которых у нас пока нет»). Использует `deepseek-v4-pro` с включённым thinking-режимом, один вызов на стартап.

**Prerequisites:** тот же `.env` с `DEEPSEEK_API_KEY`, что и для PMO Analyzer (см. выше). Каталог агентов уже лежит в `data/agents.json` — отдельной сборки не требуется.

### Запуск

```bash
.venv/bin/python -m agent_matcher.matcher
```

Читает `data/edu_companies_pmo.csv` (698 стартапов) и `data/agents.json`, классифицирует каждый стартап параллельно (concurrency 10), затем пишет два файла:

| Файл | Содержание |
|------|------------|
| `data/startup_agent_assignment.csv` | 1 строка = 1 стартап: `assigned_agent`, `agent_sredstvo`, `agent_status`, `relevance`, `rationale` (либо `unmatched` / `error`) |
| `data/agent_startups.csv` | агент-центричный пивот: все 44 агента + строки `unmatched` и `error`, с колонкой `startups` («Имя (relevance); …» по убыванию релевантности) |

Порог `relevance` задаётся константой `THRESHOLD` в `agent_matcher/assemble.py` — его можно изменить и пересобрать CSV без повторных вызовов API. Строки с `assigned_agent == "error"` — это сбои API/парсинга, перезапускаемы.

## Tests

```bash
.venv/bin/python -m pytest -v
```
