from __future__ import annotations

import json
import logging
import urllib.parse

from vc_crawler.crawlers.base import BaseCrawler
from vc_crawler.models import Company

from .normalizer import normalize
from .parser import AJAX_URL, NONCE_URL, PORTFOLIO_URL, parse_cards

log = logging.getLogger(__name__)

_BATCH_SIZE = 16
_BASE_ARGS: list[tuple[str, str]] = [
    ("args[post_type]", "portfolio"),
    ("args[posts_per_page]", str(_BATCH_SIZE)),
    ("args[post_status]", "publish"),
    ("args[fields]", "ids"),
    ("args[add_args][sector]", "learning"),
    ("args[orderby]", "title"),
    ("args[order]", "ASC"),
    ("args[tax_query][0][taxonomy]", "sector"),
    ("args[tax_query][0][field]", "slug"),
    ("args[tax_query][0][terms]", "learning"),
]


class ReachCrawler(BaseCrawler):
    def run(
        self,
        *,
        limit: int | None = None,
        workers: int = 5,
        enrich: bool = True,
    ) -> list[Company]:
        log.info("Fetching Reach Capital portfolio page ...")
        resp = self.client.get(PORTFOLIO_URL)
        raw_records = parse_cards(resp.text)
        log.info("Parsed %d companies from page", len(raw_records))

        nonce_resp = self.client.get(NONCE_URL)
        nonce = json.loads(nonce_resp.text)["data"]["nonce"]

        offset = _BATCH_SIZE
        while True:
            data = urllib.parse.urlencode(
                _BASE_ARGS + [
                    ("action", "reach_portfolio_filter"),
                    ("nonce", nonce),
                    ("args[offset]", str(offset)),
                ]
            )
            ajax_resp = self.client.post(
                AJAX_URL,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                },
            )
            if not ajax_resp.text.strip():
                break
            batch = parse_cards(ajax_resp.text)
            if not batch:
                break
            raw_records.extend(batch)
            log.info("Loaded batch at offset %d: %d companies", offset, len(batch))
            offset += _BATCH_SIZE

        companies = [normalize(r, i) for i, r in enumerate(raw_records, start=1)]
        if limit:
            companies = companies[:limit]
        return companies
