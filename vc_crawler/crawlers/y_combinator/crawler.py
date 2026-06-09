from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company
from .parser import fetch_education_companies
from .normalizer import normalize

log = logging.getLogger(__name__)


class YCCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching Y Combinator Education portfolio via Algolia ...")
        raw_records = fetch_education_companies(self.client)
        log.info("Parsed %d companies", len(raw_records))

        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]

        if limit:
            companies = companies[:limit]
        return companies
