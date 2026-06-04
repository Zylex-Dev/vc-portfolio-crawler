from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company
from .parser import PORTFOLIO_URL, parse_portfolio_page
from .normalizer import normalize

log = logging.getLogger(__name__)


class A16ZCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching a16z portfolio page ...")
        resp = self.client.get(PORTFOLIO_URL)
        raw = parse_portfolio_page(resp.text)
        log.info("Found %d companies in JS global", len(raw))
        companies = [normalize(r, i) for i, r in enumerate(raw, start=1)]
        if limit:
            companies = companies[:limit]
        return companies
