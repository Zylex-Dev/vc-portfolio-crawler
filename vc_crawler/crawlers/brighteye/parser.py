from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.brighteyevc.com/portfolio"


def parse_portfolio_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    featured = _parse_featured(soup)
    cards = soup.select(".portfolio-companies-collection-item")
    return [_parse_card(card, featured) for card in cards]


def _parse_featured(soup) -> dict[str, dict]:
    """Returns dict keyed by website URL with enriched data from featured modals."""
    result = {}
    for item in soup.select(".featured-companies-collection-item"):
        website_el = item.select_one("a.is-tertiary.is-icon")
        if not website_el:
            continue
        website = website_el.get("href") or None
        if not website:
            continue

        name_el = item.select_one(".heading-style-h4")
        name = name_el.get_text(strip=True) if name_el else None

        desc_el = item.select_one(".featured-portfolio-description")
        description = desc_el.get_text(strip=True) if desc_el else None

        # Deduplicate — the same chip appears in content area and modal
        cats = list(dict.fromkeys(
            el.get_text(strip=True)
            for el in item.select(".dark-chip:not(.is-outline) .sub-head-small")
        ))

        result[website] = {
            "name": name,
            "description": description,
            "categories": cats,
        }
    return result


def _parse_card(card, featured: dict[str, dict]) -> dict:
    link = card.select_one("a[href*='/portfolio-companies/']")
    slug = link["href"].split("/portfolio-companies/")[-1] if link else ""

    loc_el = card.select_one(".dark-chip.is-outline .sub-head-small")
    location = loc_el.get_text(strip=True) if loc_el else None

    logo = card.select_one("img.portfolio-card-logo")
    logo_url = logo.get("src") or None if logo else None

    website_link = card.select_one("a.is-tertiary.is-icon")
    website = website_link.get("href") or None if website_link else None

    exit_tag = card.select_one(".exit-tag")
    is_exited = bool(
        exit_tag and "w-condition-invisible" not in exit_tag.get("class", [])
    )

    enriched = featured.get(website, {})
    return {
        "slug": slug,
        "location": location,
        "logo_url": logo_url,
        "website": website,
        "is_exited": is_exited,
        "name": enriched.get("name"),
        "description": enriched.get("description"),
        "categories": enriched.get("categories", []),
    }
