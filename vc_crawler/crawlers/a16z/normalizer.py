from __future__ import annotations

import re
from typing import Optional

from vc_crawler.models import Company
from .parser import PORTFOLIO_URL

_STAGE_PRIORITY = {"IPO": 5, "M&A": 4, "Growth": 3, "Venture": 2}
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _pick_stage(stages: list[str]) -> Optional[str]:
    if not stages:
        return None
    return max(stages, key=lambda s: _STAGE_PRIORITY.get(s, 0))


def _make_slug(name: str) -> str:
    return _SLUG_RE.sub("-", name.lower()).strip("-")


def _website(raw: dict) -> Optional[str]:
    for key in ("web", "url", "external_url"):
        val = raw.get(key)
        if val:
            return val
    return None


def _year(val: Optional[str]) -> Optional[int]:
    if not val:
        return None
    try:
        return int(str(val)[:4])
    except (ValueError, TypeError):
        return None


def normalize(raw: dict, company_id: int) -> Company:
    announcement = raw.get("announcement") or {}
    founders_raw: list[str] = raw.get("founders_list") or []
    status = raw.get("status", "")
    exit_date = raw.get("exit_date")

    return Company(
        id=company_id,
        fund="a16z",
        name=raw["name"],
        slug=_make_slug(raw["name"]),
        fund_url=announcement.get("permalink") or PORTFOLIO_URL,
        sectors=raw.get("focus_areas") or [],
        website=_website(raw),
        description=raw.get("overview") or None,
        stage=_pick_stage(raw.get("stages") or []),
        stage_year=_year(exit_date) if status == "Exits" else None,
        founded_year=_year(raw.get("year_founded")),
        invested_year=_year(raw.get("initial_a16z_date_funded")),
        logo_url=raw.get("logo") or None,
        source_modified=None,
        ticker_symbol=raw.get("ticker_symbol") or None,
        acquirer=raw.get("acquirer") or None,
        founders=founders_raw if founders_raw else None,
    )
