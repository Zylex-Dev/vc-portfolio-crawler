from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

FUND_URL_BASE = "https://www.ycombinator.com/companies"
_YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')


def normalize(raw: dict, company_id: int) -> Company:
    slug = raw.get("slug", "")
    status = raw.get("status", "")

    if status == "Acquired":
        stage = "Acquired"
    elif status == "Inactive":
        stage = "Inactive"
    else:
        stage = raw.get("stage") or None

    return Company(
        id=company_id,
        fund="y-combinator",
        name=raw.get("name", ""),
        slug=slug,
        fund_url=f"{FUND_URL_BASE}/{slug}",
        sectors=raw.get("industries") or [],
        website=raw.get("website") or None,
        description=raw.get("long_description") or raw.get("one_liner") or None,
        stage=stage,
        stage_year=None,
        founded_year=None,
        invested_year=_parse_batch_year(raw.get("batch")),
        logo_url=raw.get("small_logo_thumb_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=None,
    )


def _parse_batch_year(batch: Optional[str]) -> Optional[int]:
    if not batch:
        return None
    m = _YEAR_RE.search(batch)
    return int(m.group()) if m else None
