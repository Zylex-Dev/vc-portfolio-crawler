from __future__ import annotations

from typing import Optional

from vc_crawler.models import Company

FUND_URL_BASE = "https://speedrun.a16z.com/companies/"


def _founders(founder_set: list[dict]) -> Optional[list[str]]:
    names = [
        f"{f.get('first_name', '')} {f.get('last_name', '')}".strip()
        for f in founder_set
    ]
    return names if names else None


def normalize(raw: dict, company_id: int) -> Company:
    slug = raw["slug"]
    return Company(
        id=company_id,
        fund="a16z-speedrun",
        name=raw["name"],
        slug=slug,
        fund_url=f"{FUND_URL_BASE}{slug}",
        sectors=raw.get("industries") or [],
        website=raw.get("website_url") or None,
        description=raw.get("description") or None,
        stage=raw.get("cohort") or None,
        stage_year=None,
        founded_year=raw.get("founded_year"),
        invested_year=None,
        logo_url=raw.get("logo") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=_founders(raw.get("founder_set") or []),
    )
