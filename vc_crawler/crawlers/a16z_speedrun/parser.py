from __future__ import annotations

import json
import re

PORTFOLIO_URL = "https://speedrun.a16z.com/companies/"
API_BASE = "https://speedrun-be.a16z.com/api/companies/companies/"

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def parse_portfolio_page(html: str) -> list[str]:
    """Return ordered list of cohort names from the portfolio page __NEXT_DATA__."""
    m = _NEXT_DATA_RE.search(html)
    if not m:
        raise ValueError(
            "Could not find __NEXT_DATA__ script tag in the speedrun portfolio page. "
            "The page structure may have changed."
        )
    data = json.loads(m.group(1))
    try:
        cohorts = data["props"]["pageProps"]["cohorts"]
    except KeyError as exc:
        raise ValueError(
            f"Expected props.pageProps.cohorts in __NEXT_DATA__ but key {exc} was missing."
        ) from exc
    return [c["name"] for c in cohorts]


def fetch_cohort_companies(client, cohort: str) -> list[dict]:
    """Fetch all companies for a cohort, following pagination until next is null."""
    results: list[dict] = []
    url: str | None = f"{API_BASE}?cohort={cohort}&limit=50&ordering=name"
    while url:
        resp = client.get(url)
        page = resp.json()
        results.extend(page["results"])
        url = page.get("next")
    return results
