from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace

from vc_crawler.crawlers.sequoia.detail_parser import parse_detail
from vc_crawler.models import Company

log = logging.getLogger(__name__)


def enrich_company(client, company: Company) -> Company:
    """Fetch a company's detail page and merge parsed fields. Never raises."""
    try:
        resp = client.get(company.fund_url)
    except Exception as exc:  # noqa: BLE001 - isolate per-page failures
        log.warning("enrich failed for %s: %s", company.slug, exc)
        return company
    fields = parse_detail(resp.text)
    updates = {k: v for k, v in fields.items() if v is not None}
    return replace(company, **updates)


def enrich_all(client, companies: list[Company], workers: int = 5) -> list[Company]:
    """Enrich all companies concurrently, preserving input order."""
    order = {c.slug: i for i, c in enumerate(companies)}
    results: list[Company] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(enrich_company, client, c) for c in companies]
        for fut in as_completed(futures):
            results.append(fut.result())
    results.sort(key=lambda c: order[c.slug])
    return results
