# Reach Capital Crawler — Design Spec
**Date:** 2026-06-05  
**Scope:** Learning sector only (~95 companies)

---

## Goal

Add a Reach Capital crawler to the vc-portfolio-crawler project, following the existing fund pattern (parser / normalizer / crawler), targeting `https://www.reachcapital.com/companies/?sector=learning`.

---

## Site Structure

- WordPress with custom ACF theme
- `portfolio` custom post type, `sector` taxonomy (Learning = ID 10)
- 95 companies in Learning sector (confirmed via WP REST API)
- Initial page renders 16 cards as static HTML
- Remaining companies loaded via WordPress AJAX infinite scroll:
  - Action: `reach_portfolio_filter` on `admin-ajax.php`
  - Requires nonce (GET `admin-ajax.php?action=reach_get_nonce`)
  - Args sent as PHP-style array encoding (not JSON), with `offset` incrementing by 16
  - Empty string response signals end of results
- No individual company detail pages (slugs redirect to homepage)

### Card HTML Structure

```html
<div class="reach-portfolio-card">
  <div class="reach-portfolio-card__grid">
    <div class="reach-portfolio-card__title">Company Name</div>
    <div class="reach-portfolio-card__tags">
      <div class="reach-portfolio-card__tag">Learning</div>
      <div class="reach-portfolio-card__tag reach-portfolio-card__tag_exited">Exit</div>  <!-- optional -->
    </div>
    <div class="reach-portfolio-card__desc"><p>Description</p></div>
    <div class="reach-portfolio-card__investor-list">
      <a href="...">Investor Name</a>
    </div>
  </div>
  <div class="reach-portfolio-card__spoiler">
    <div class="reach-portfolio-card__info-item_year">
      <div class="reach-portfolio-card__info-item-title">Founded</div>
      <div class="reach-portfolio-card__info-item-desc">2015</div>
    </div>
    <div class="reach-portfolio-card__info-item_location">
      <div class="reach-portfolio-card__info-item-title">Headquarters</div>
      <div class="reach-portfolio-card__info-item-desc">San Francisco, CA</div>
    </div>
    <div class="reach-portfolio-card__info-item_founders">
      <div class="reach-portfolio-card__info-item-title">Leadership</div>
      <div class="reach-portfolio-card__info-item-desc">
        <span>Name One</span><span>Name Two</span>
      </div>
    </div>
    <div class="reach-portfolio-card__logo">
      <a href="https://company.com/" class="reach-logo-card">
        <img src="https://reachcapital.com/wp-content/.../logo.png" />
      </a>
    </div>
  </div>
</div>
```

---

## Architecture

### Files

```
vc_crawler/crawlers/reach_capital/
├── __init__.py
├── parser.py       # HTML string → list[dict]
├── normalizer.py   # dict → Company
└── crawler.py      # HTTP orchestration: page + nonce + AJAX loop
```

One line added to `_FUND_REGISTRY` in `vc_crawler/__main__.py`:
```python
"reach-capital": "vc_crawler.crawlers.reach_capital.crawler.ReachCrawler",
```

One method added to `vc_crawler/http_client.py`:
```python
def post(self, url: str, **kwargs) -> requests.Response: ...
```

### Data Flow

```
GET /?sector=learning       → parse_cards(html) → batch_0 (16 cards)
GET admin-ajax.php?nonce    → nonce string
POST admin-ajax.php, offset=16  → parse_cards(html) → batch_1
POST admin-ajax.php, offset=32  → parse_cards(html) → batch_2
...
POST admin-ajax.php, offset=N   → "" (empty)        → stop

all batches → normalize(raw, id) → Company
```

### AJAX Request Format

```
POST https://www.reachcapital.com/wp-admin/admin-ajax.php
Content-Type: application/x-www-form-urlencoded
X-Requested-With: XMLHttpRequest

action=reach_portfolio_filter
&nonce=<nonce>
&args[post_type]=portfolio
&args[posts_per_page]=16
&args[post_status]=publish
&args[fields]=ids
&args[add_args][sector]=learning
&args[orderby]=title
&args[order]=ASC
&args[tax_query][0][taxonomy]=sector
&args[tax_query][0][field]=slug
&args[tax_query][0][terms]=learning
&args[offset]=<offset>
```

---

## Field Mapping

| HTML source | `Company` field | Notes |
|---|---|---|
| `reach-portfolio-card__title` | `name` | stripped text |
| slugify(name) | `slug` | lowercase, spaces→hyphens, strip non-alphanumeric (regex, no external dep) |
| `reach-portfolio-card__tag_exited` present | `stage = "Exit"` | else `None` |
| `reach-portfolio-card__desc p` | `description` | first `<p>` |
| spoiler `_year` `.info-item-desc` | `founded_year` | int or None |
| spoiler `_founders` `.info-item-desc span` | `founders` | list[str] |
| `reach-logo-card` href | `website` | |
| spoiler `img` src | `logo_url` | |
| hardcoded `["Learning"]` | `sectors` | all cards on this URL are Learning |
| `"reach-capital"` | `fund` | |
| `https://www.reachcapital.com/companies/?sector=learning` | `fund_url` | no per-company pages |
| `None` | `invested_year`, `stage_year`, `ticker_symbol`, `acquirer` | not available |

---

## Error Handling

- HTTP errors / retries: handled by `PoliteClient` (4 retries, backoff) — no extra logic needed
- Cards with empty `name` → skip with `log.warning`
- `founded_year` parse failure → `None`, no exception
- Nonce failure → exception propagates (fail fast)
- Empty AJAX response (`""`) → stop loop (not an error)

---

## Testing

### Fixtures

| File | Contents |
|---|---|
| `tests/fixtures/reach_capital_portfolio.html` | Minimal page with 2–3 cards (1 normal, 1 with Exit tag) |
| `tests/fixtures/reach_capital_ajax.html` | AJAX fragment with 2 cards (no wrapper page HTML) |

### Test files

**`test_reach_parser.py`**
- `parse_cards()` returns list of dicts
- Parses: name, description, website, logo_url, founded_year, founders
- Exit tag → `is_exited=True`; absent → `is_exited=False`
- Empty HTML → empty list
- Works identically on full page and AJAX fragment

**`test_reach_normalizer.py`**
- Returns `Company` instance
- `fund == "reach-capital"`, `sectors == ["Learning"]`
- `stage == "Exit"` when `is_exited=True`, else `None`
- `founded_year` is int or None
- Invalid year string → `None`

**`test_reach_crawler.py`**
- Mocked `PoliteClient`: `get()` returns page then nonce JSON; `post()` returns AJAX fragment then `""`
- Correct number of requests made
- `--limit` truncates result

---

## Out of Scope

- Other sectors (Health, Work) — not required
- Headquarters / location field — no mapping in `Company` schema
- Investor names — not mapped (no field in schema)
