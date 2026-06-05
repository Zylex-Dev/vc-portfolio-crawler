from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company
from .parser import PORTFOLIO_URL, parse_portfolio_page, fetch_cohort_companies
from .normalizer import normalize

log = logging.getLogger(__name__)


class SpeedrunCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching speedrun portfolio page to discover cohorts ...")
        resp = self.client.get(PORTFOLIO_URL)
        cohorts = parse_portfolio_page(resp.text)
        log.info("Found cohorts: %s", cohorts)

        raw_records: list[dict] = []
        for cohort in cohorts:
            records = fetch_cohort_companies(self.client, cohort)
            log.info("Cohort %s: %d companies", cohort, len(records))
            raw_records.extend(records)

        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]
        log.info("Total: %d companies", len(companies))

        if limit:
            companies = companies[:limit]
        return companies
