from __future__ import annotations

import re

from vc_crawler.models import Company

PORTFOLIO_URL = "https://www.brighteyevc.com/portfolio"

_COPY_RE = re.compile(r"-copy$")


def normalize(raw: dict, company_id: int) -> Company:
    clean_slug = _COPY_RE.sub("", raw.get("slug", ""))
    name = raw.get("name") or _slug_to_name(clean_slug)

    return Company(
        id=company_id,
        fund="brighteye",
        name=name,
        slug=clean_slug,
        fund_url=PORTFOLIO_URL,
        sectors=raw.get("categories") or [],
        website=raw.get("website") or None,
        description=raw.get("description") or None,
        stage="Exited" if raw.get("is_exited") else None,
        stage_year=None,
        founded_year=None,
        invested_year=None,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=None,
    )


def _slug_to_name(slug: str) -> str:
    return " ".join(word.capitalize() for word in slug.split("-") if word)
