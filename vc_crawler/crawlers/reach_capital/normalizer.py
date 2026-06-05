from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

FUND_URL = "https://www.reachcapital.com/companies/?sector=learning"
_SECTOR = "Learning"
_SLUG_STRIP_RE = re.compile(r"[^a-z0-9]+")


def normalize(raw: dict, company_id: int) -> Company:
    founders = raw.get("founders") or []
    return Company(
        id=company_id,
        fund="reach-capital",
        name=raw.get("name", ""),
        slug=_slugify(raw.get("name", "")),
        fund_url=FUND_URL,
        sectors=[_SECTOR],
        website=raw.get("website") or None,
        description=raw.get("description") or None,
        stage="Exit" if raw.get("is_exited") else None,
        stage_year=None,
        founded_year=_parse_int(raw.get("founded_year_str")),
        invested_year=None,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=founders if founders else None,
    )


def _slugify(name: str) -> str:
    return _SLUG_STRIP_RE.sub("-", name.lower()).strip("-")


def _parse_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    try:
        return int(text.strip())
    except ValueError:
        return None
