from __future__ import annotations

import json
from urllib.parse import urlparse

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.newschools.org/ventures/"
INIT_YEAR_API = "https://www.newschools.org/wp-json/wp/v2/initial-investment-year?per_page=100"


def parse_term_map(json_text: str) -> dict[int, int]:
    return {t["id"]: int(t["name"]) for t in json.loads(json_text)}


def parse_listing_page(html: str) -> tuple[list[dict], int]:
    soup = BeautifulSoup(html, "lxml")
    anchor = soup.select_one(".e-load-more-anchor")
    max_page = int(anchor["data-max-page"]) if anchor else 1
    records = [_parse_card(card) for card in soup.select(".e-loop-item")]
    return records, max_page


def _parse_card(card) -> dict:
    classes = card.get("class", [])

    link = card.select_one("a[href]")
    fund_url = link["href"] if link else ""
    slug = urlparse(fund_url).path.strip("/").split("/")[-1] if fund_url else ""

    img = card.select_one("img")
    logo_url = img.get("src") or None if img else None

    title = card.select_one(".elementor-heading-title")
    name = title.get_text(strip=True) if title else ""

    sectors = [el.get_text(strip=True) for el in card.select(".elementor-post-info__item")]

    init_year_ids = [
        int(c.replace("initial-investment-year-", ""))
        for c in classes if c.startswith("initial-investment-year-")
    ]

    return {
        "name": name,
        "fund_url": fund_url,
        "slug": slug,
        "logo_url": logo_url,
        "sectors": sectors,
        "init_year_ids": init_year_ids,
        "is_past": "status-past-venture" in classes,
    }


def parse_detail_page(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    description = None
    for block in soup.select(".elementor-widget-text-editor"):
        text = block.get_text(strip=True)
        if len(text) >= 50:
            description = text
            break

    website = None
    for a in soup.select("a[href]"):
        if "website" in a.get_text(strip=True).lower():
            href = a.get("href", "")
            if href.startswith("http"):
                website = href
                break

    founded_year = None
    for h in soup.select("h2.elementor-heading-title"):
        text = h.get_text(strip=True)
        if text.startswith("Founded:"):
            try:
                founded_year = int(text.split(":")[-1].strip())
            except ValueError:
                pass
            break

    return {"description": description, "website": website, "founded_year": founded_year}
