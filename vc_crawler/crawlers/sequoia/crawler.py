from __future__ import annotations

import logging

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company
from . import api
from .enrich import enrich_all
from .listing import fetch_stage_map, normalize_name
from .sitemap import fetch_company_slugs

log = logging.getLogger(__name__)


class SequoiaCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        sectors = api.fetch_categories(self.client)
        log.info("Loaded %d sector categories", len(sectors))
        companies = [
            api.to_company(raw, sectors, company_id=i)
            for i, raw in enumerate(api.iter_companies(self.client), start=1)
        ]
        log.info("Index: %d companies", len(companies))
        self._check_completeness(companies)

        if limit:
            companies = companies[:limit]
            log.info("Limited to %d companies", limit)

        self._apply_stages(companies)

        if enrich:
            log.info("Enriching %d companies (workers=%d) ...", len(companies), workers)
            companies = enrich_all(self.client, companies, workers=workers)

        return companies

    def _check_completeness(self, companies: list[Company]) -> None:
        try:
            sitemap_slugs = fetch_company_slugs(self.client)
        except Exception as exc:
            log.warning("sitemap check skipped: %s", exc)
            return
        have = {c.slug for c in companies}
        missing = sitemap_slugs - have
        extra = have - sitemap_slugs
        log.info(
            "Completeness: api=%d sitemap=%d missing=%d extra=%d",
            len(have), len(sitemap_slugs), len(missing), len(extra),
        )
        if missing:
            log.warning("Slugs in sitemap but not in API: %s", sorted(missing)[:20])

    def _apply_stages(self, companies: list[Company]) -> None:
        try:
            stage_map = fetch_stage_map(self.client)
        except Exception as exc:
            log.warning("stage enrichment skipped: %s", exc)
            return
        matched = 0
        for c in companies:
            stage = stage_map.get(normalize_name(c.name))
            if stage:
                c.stage = stage
                matched += 1
        log.info("Stage: matched %d/%d companies", matched, len(companies))
