from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

PORTFOLIO_URL = "https://gsv.ventures/portfolio/"
_YEAR_RE = re.compile(r'\b(19|20)\d{2}\b')
_NON_ALNUM_RE = re.compile(r'[^a-z0-9]+')


def normalize(raw: dict, company_id: int) -> Company:
    stage, invested_year = _parse_investment(raw.get("investment"))
    founders = raw.get("founders") or []
    sector = raw.get("sector")

    return Company(
        id=company_id,
        fund="gsv-ventures",
        name=raw.get("name", ""),
        slug=_slugify(raw.get("name", "")),
        fund_url=PORTFOLIO_URL,
        sectors=[sector] if sector else [],
        website=raw.get("website") or None,
        description=raw.get("description") or raw.get("tagline") or None,
        stage=stage,
        stage_year=None,
        founded_year=_parse_int(raw.get("founded_year_str")),
        invested_year=invested_year,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=founders if founders else None,
    )


def _slugify(name: str) -> str:
    return _NON_ALNUM_RE.sub("-", name.lower()).strip("-")


def _parse_investment(text: Optional[str]) -> tuple[Optional[str], Optional[int]]:
    if not text:
        return None, None
    parts = text.split(",", 1)
    stage = parts[0].strip() or None
    year: Optional[int] = None
    if len(parts) > 1:
        m = _YEAR_RE.search(parts[1])
        if m:
            year = int(m.group())
    return stage, year


def _parse_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    try:
        return int(text.strip())
    except ValueError:
        return None
