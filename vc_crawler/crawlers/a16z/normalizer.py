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


def _name(raw: dict) -> str:
    """Return company name, supporting both 'title' (live) and 'name' (fixture) keys."""
    return raw.get("title") or raw["name"]


def _founders(raw: dict) -> Optional[list[str]]:
    """Return founders list, supporting both 'founders_list' (fixture) and 'founders' (live) keys."""
    # fixture: founders_list is a list
    fl = raw.get("founders_list")
    if fl is not None:
        return fl if fl else None
    # live site: founders is a string (comma-separated) or empty string
    fv = raw.get("founders")
    if fv and isinstance(fv, str):
        return [f.strip() for f in fv.split(",") if f.strip()]
    return None


def _is_exit(raw: dict) -> bool:
    """Return True when the entry represents an exited company."""
    # fixture field
    if raw.get("status") == "Exits":
        return True
    # live field: non-empty string "1" or truthy value
    if raw.get("display_exit_info_on_a16z_website"):
        return True
    return False


def normalize(raw: dict, company_id: int) -> Company:
    announcement = raw.get("announcement") or {}
    name = _name(raw)
    exit_date = raw.get("exit_date")
    invested_date = raw.get("initial_a16z_date_funded") or raw.get("invest_date")

    return Company(
        id=company_id,
        fund="a16z",
        name=name,
        slug=_make_slug(name),
        fund_url=announcement.get("permalink") or PORTFOLIO_URL,
        sectors=raw.get("focus_areas") or [],
        website=_website(raw),
        description=raw.get("overview") or None,
        stage=_pick_stage(raw.get("stages") or []),
        stage_year=_year(exit_date) if _is_exit(raw) else None,
        founded_year=_year(raw.get("year_founded")),
        invested_year=_year(invested_date),
        logo_url=raw.get("logo") or None,
        source_modified=None,
        ticker_symbol=raw.get("ticker_symbol") or None,
        acquirer=raw.get("acquirer") or None,
        founders=_founders(raw),
    )
