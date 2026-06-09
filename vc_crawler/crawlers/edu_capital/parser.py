from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.educapitalvc.com/portfolio"


def parse_portfolio_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    items = soup.select(".portfolio_content.w-dyn-item")
    return [_parse_item(item) for item in items]


def _parse_item(item) -> dict:
    logo_img = item.find("img", class_="portfolio_logo")
    logo_url = logo_img["src"] if logo_img else None

    desc_el = item.find("p", class_="text-color-purple")
    description = desc_el.get_text(strip=True) if desc_el else None

    cat_el = item.find(attrs={"fs-cmsfilter-field": "category"})
    category = cat_el.get_text(strip=True) if cat_el else None

    back_links = item.select("a.portfolio_card-back")
    website = back_links[0].get("href") if back_links else None

    tag_el = item.find("div", class_="tag")
    acquired = bool(
        tag_el and "w-condition-invisible" not in tag_el.get("class", [])
    )

    return {
        "logo_url": logo_url,
        "description": description,
        "category": category,
        "website": website,
        "acquired": acquired,
    }
