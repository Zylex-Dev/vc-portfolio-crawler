from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://gsv.ventures/portfolio/"


def parse_portfolio_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    return [_parse_card(card) for card in soup.find_all("div", class_="c-grid--item")]


def _parse_card(card) -> dict:
    raw: dict = {
        "name": "",
        "tagline": None,
        "description": None,
        "website": None,
        "logo_url": None,
        "founders": [],
        "investment": None,
        "founded_year_str": None,
        "sector": None,
    }

    img_wrapper = card.find(class_="c-grid--item-image")
    if img_wrapper:
        logo = img_wrapper.find("img")
        if logo:
            raw["logo_url"] = logo.get("data-src") or None

    content = card.find(class_="c-grid--item-content")
    if not content:
        return raw

    main = content.find("main")
    if main:
        tags = main.find(class_="company-tags")
        if tags:
            name_el = tags.find(class_="company-name")
            raw["name"] = name_el.get_text(strip=True) if name_el else ""

        h2 = main.find("h2")
        if h2:
            raw["tagline"] = h2.get_text(strip=True)

        for p in main.find_all("p"):
            a = p.find("a")
            if a and a.get_text(strip=True).lower().startswith("learn more"):
                raw["website"] = a.get("href") or None
            elif not raw["description"]:
                text = p.get_text(strip=True)
                if text:
                    raw["description"] = text

    aside = content.find("aside")
    if aside:
        for li in aside.find_all("li"):
            title_el = li.find(class_="company-info--title")
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            val = li.get_text(strip=True)[len(title):].strip()
            if not val:
                continue
            if title == "Founders/Leadership":
                raw["founders"] = [f.strip() for f in val.split(",") if f.strip()]
            elif title == "Investment":
                raw["investment"] = val
            elif title == "Year Founded":
                raw["founded_year_str"] = val
            elif title == "Segment":
                raw["sector"] = val

    return raw
