from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company

from .normalizer import normalize
from .parser import PORTFOLIO_URL, parse_portfolio_page

log = logging.getLogger(__name__)


class EduCapitalCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching EduCapital portfolio page ...")
        resp = self.client.get(PORTFOLIO_URL)
        raw_records = parse_portfolio_page(resp.text)
        log.info("Parsed %d companies", len(raw_records))
        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]
        if limit:
            companies = companies[:limit]
        return companies
