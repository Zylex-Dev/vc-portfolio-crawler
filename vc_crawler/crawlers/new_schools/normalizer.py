from __future__ import annotations

from vc_crawler.models import Company


def normalize(
    listing: dict,
    detail: dict,
    init_map: dict[int, int],
    company_id: int,
) -> Company:
    init_ids = listing.get("init_year_ids", [])
    invested_year = init_map.get(init_ids[0]) if init_ids else None

    return Company(
        id=company_id,
        fund="new-schools",
        name=listing["name"],
        slug=listing.get("slug", ""),
        fund_url=listing.get("fund_url", ""),
        sectors=listing.get("sectors") or [],
        website=detail.get("website"),
        description=detail.get("description"),
        stage="Past" if listing.get("is_past") else None,
        stage_year=None,
        founded_year=None,
        invested_year=invested_year,
        logo_url=listing.get("logo_url"),
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=None,
    )
