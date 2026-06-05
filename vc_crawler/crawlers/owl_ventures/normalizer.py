from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

FUND_URL_BASE = "https://www.owlvc.com"
_YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')


def normalize(raw: dict, company_id: int) -> Company:
    href = raw.get("fund_path", "")
    slug = href.rstrip("/").rsplit("/", 1)[-1] if href else ""
    founders = raw.get("founders") or []

    return Company(
        id=company_id,
        fund="owl-ventures",
        name=raw.get("name", ""),
        slug=slug,
        fund_url=f"{FUND_URL_BASE}{href}" if href else "",
        sectors=raw.get("sectors") or [],
        website=raw.get("website") or None,
        description=raw.get("description") or None,
        stage="Acquired" if raw.get("is_acquired") else None,
        stage_year=None,
        founded_year=_parse_int(raw.get("founded_year_str")),
        invested_year=_parse_year(raw.get("initial_investment")),
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=raw.get("acquirer") or None,
        founders=founders if founders else None,
    )


def _parse_year(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    m = _YEAR_RE.search(text)
    return int(m.group()) if m else None


def _parse_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    try:
        return int(text.strip())
    except ValueError:
        return None
