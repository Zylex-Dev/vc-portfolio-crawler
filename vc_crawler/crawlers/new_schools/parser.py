from __future__ import annotations

import json
from urllib.parse import urlparse

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.newschools.org/ventures/"
INV_YEAR_API  = "https://www.newschools.org/wp-json/wp/v2/investment-year?per_page=100"
INIT_YEAR_API = "https://www.newschools.org/wp-json/wp/v2/initial-investment-year?per_page=100"


def parse_term_map(json_text: str) -> dict[int, int]:
    return {t["id"]: int(t["name"]) for t in json.loads(json_text)}


def parse_listing_page(html: str) -> tuple[list[dict], int]:
    raise NotImplementedError


def parse_detail_page(html: str) -> dict:
    raise NotImplementedError
