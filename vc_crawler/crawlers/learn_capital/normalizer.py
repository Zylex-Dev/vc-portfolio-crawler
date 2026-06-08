from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company

PORTFOLIO_URL = "https://learn.vc/ventures"
_NON_ALNUM_RE = re.compile(r'[^a-z0-9]+')


def normalize(raw: dict, company_id: int) -> Company:
    founders = _parse_founders(raw.get("founders_text", ""))
    stage = _parse_stage(raw)

    return Company(
        id=company_id,
        fund="learn-capital",
        name=raw.get("name", ""),
        slug=_slugify(raw.get("name", "")),
        fund_url=PORTFOLIO_URL,
        sectors=raw.get("tags", []),
        website=raw.get("website") or None,
        description=raw.get("description") or raw.get("headline") or None,
        stage=stage,
        stage_year=None,
        founded_year=None,
        invested_year=None,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=founders if founders else None,
    )


def _parse_stage(raw: dict) -> Optional[str]:
    if raw.get("acquired"):
        return "Acquired"
    if raw.get("public"):
        return "Public"
    return None


def _parse_founders(text: str) -> list[str]:
    if not text:
        return []
    return [f.strip() for f in text.split(",") if f.strip()]


def _slugify(name: str) -> str:
    return _NON_ALNUM_RE.sub("-", name.lower()).strip("-")
