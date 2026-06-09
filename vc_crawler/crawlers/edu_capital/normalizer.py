from __future__ import annotations

import re
from urllib.parse import urlparse

from vc_crawler.models import Company

PORTFOLIO_URL = "https://www.educapitalvc.com/portfolio"
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def normalize(raw: dict, company_id: int) -> Company:
    name = _name_from_url(raw.get("website") or "")
    return Company(
        id=company_id,
        fund="edu-capital",
        name=name,
        slug=_slugify(name),
        fund_url=PORTFOLIO_URL,
        sectors=[raw["category"]] if raw.get("category") else [],
        website=raw.get("website") or None,
        description=raw.get("description") or None,
        stage="Acquired" if raw.get("acquired") else None,
        stage_year=None,
        founded_year=None,
        invested_year=None,
        logo_url=raw.get("logo_url") or None,
        source_modified=None,
        ticker_symbol=None,
        acquirer=None,
        founders=None,
    )


def _name_from_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    host = parsed.netloc
    host = re.sub(r"^www\.", "", host)
    if host == "apps.apple.com":
        m = re.search(r"/app/([^/]+)/", parsed.path)
        if m:
            return m.group(1).split("-")[0]
        return ""
    return host.split(".")[0]


def _slugify(name: str) -> str:
    return _NON_ALNUM_RE.sub("-", name.lower()).strip("-")
