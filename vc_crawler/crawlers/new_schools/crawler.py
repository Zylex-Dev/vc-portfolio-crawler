from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company

from .normalizer import normalize
from .parser import (
    INIT_YEAR_API,
    PORTFOLIO_URL,
    parse_detail_page,
    parse_listing_page,
    parse_term_map,
)

log = logging.getLogger(__name__)


class NewSchoolsCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        init_map = parse_term_map(self.client.get(INIT_YEAR_API).text)
        log.info("Loaded init year map: %d terms", len(init_map))

        records, max_page = parse_listing_page(self.client.get(PORTFOLIO_URL).text)
        log.info("Page 1/%d: %d companies", max_page, len(records))

        for page in range(2, max_page + 1):
            url = f"{PORTFOLIO_URL}{page}/"
            page_records, _ = parse_listing_page(self.client.get(url).text)
            records.extend(page_records)
            log.info("Page %d/%d: %d companies", page, max_page, len(page_records))

        log.info("Total from listings: %d companies", len(records))

        if limit:
            records = records[:limit]

        detail_list = self._enrich_all(records, workers) if enrich else [{} for _ in records]

        return [
            normalize(rec, det, init_map, i)
            for i, (rec, det) in enumerate(zip(records, detail_list), 1)
        ]

    def _enrich_all(self, records: list[dict], workers: int) -> list[dict]:
        def fetch(record: dict) -> dict:
            try:
                resp = self.client.get(record["fund_url"])
                return parse_detail_page(resp.text)
            except Exception as exc:
                log.warning("enrich failed for %s: %s", record.get("slug"), exc)
                return {}

        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(fetch, records))
