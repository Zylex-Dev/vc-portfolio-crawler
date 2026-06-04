from __future__ import annotations

import html
from typing import Iterator

from vc_crawler.models import Company

BASE = "https://sequoiacap.com/wp-json/wp/v2"
_DROP_SECTORS = {"Uncategorized"}


def _paginate(client, url: str, params: dict) -> Iterator[dict]:
    page = 1
    while True:
        resp = client.get(url, params={**params, "page": page})
        items = resp.json()
        if not items:
            break
        for item in items:
            yield item
        total_pages = int(resp.headers.get("X-WP-TotalPages", 1))
        if page >= total_pages:
            break
        page += 1


def fetch_categories(client, base: str = BASE) -> dict[int, str]:
    """Return {term_id: sector_name} for the company category taxonomy."""
    mapping: dict[int, str] = {}
    for term in _paginate(client, f"{base}/categories", {"per_page": 100}):
        mapping[term["id"]] = term["name"]
    return mapping


def iter_companies(client, base: str = BASE) -> Iterator[dict]:
    """Yield raw company JSON objects across all pages."""
    yield from _paginate(
        client,
        f"{base}/company",
        {"per_page": 100, "orderby": "title", "order": "asc"},
    )


def to_company(raw: dict, sectors_map: dict[int, str], company_id: int) -> Company:
    sectors = [
        sectors_map[cid]
        for cid in raw.get("categories", [])
        if cid in sectors_map and sectors_map[cid] not in _DROP_SECTORS
    ]
    return Company(
        id=company_id,
        fund="sequoia",
        name=html.unescape(raw["title"]["rendered"]).strip(),
        slug=raw["slug"],
        fund_url=raw["link"],
        sectors=sectors,
        source_modified=raw.get("modified"),
    )
