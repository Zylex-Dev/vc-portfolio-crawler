from __future__ import annotations

import html
import re

from bs4 import BeautifulSoup


LISTING_URL = "https://sequoiacap.com/our-companies/"

_TOTAL_PAGES_RE = re.compile(r'"total_pages"\s*:\s*(\d+)')


def normalize_name(name: str) -> str:
    """Canonical key for matching a listing row to a REST company by name."""
    return re.sub(r"\s+", " ", html.unescape(name)).strip().casefold()


def total_pages(html_text: str) -> int:
    m = _TOTAL_PAGES_RE.search(html_text)
    return int(m.group(1)) if m else 1


def parse_stage_map(html_text: str) -> dict[str, str]:
    """Map normalized company name -> Current Stage for one listing page."""
    soup = BeautifulSoup(html_text, "lxml")
    stages: dict[str, str] = {}
    for head in soup.select(".company-listing__head"):
        row = head.find_parent("tr")
        if row is None:
            continue
        cell = row.select_one("td.u-lg-hide[data-order]")
        if cell is None:
            continue
        name = normalize_name(head.get_text(" ", strip=True))
        stage = cell.get_text(" ", strip=True)
        if name and stage:
            stages[name] = stage
    return stages


def fetch_stage_map(client, base: str = LISTING_URL) -> dict[str, str]:
    """Fetch every listing page and merge their name -> stage maps."""
    first = client.get(base).text
    stages = dict(parse_stage_map(first))
    for page in range(2, total_pages(first) + 1):
        html_text = client.get(base, params={"_paged": page}).text
        stages.update(parse_stage_map(html_text))
    return stages
