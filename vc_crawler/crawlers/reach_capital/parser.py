from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.reachcapital.com/companies/?sector=learning"
AJAX_URL = "https://www.reachcapital.com/wp-admin/admin-ajax.php"
NONCE_URL = f"{AJAX_URL}?action=reach_get_nonce"


def parse_cards(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.find_all("div", class_="reach-portfolio-card")
    result = []
    for card in cards:
        raw = _parse_card(card)
        if raw["name"]:
            result.append(raw)
    return result


def _parse_card(card) -> dict:
    raw: dict = {}

    title_el = card.find(class_="reach-portfolio-card__title")
    raw["name"] = title_el.get_text(strip=True) if title_el else ""

    raw["is_exited"] = bool(card.find(class_="reach-portfolio-card__tag_exited"))

    desc_el = card.find(class_="reach-portfolio-card__desc")
    p = desc_el.find("p") if desc_el else None
    raw["description"] = (p.get_text(strip=True) or None) if p else None

    spoiler = card.find(class_="reach-portfolio-card__spoiler")
    raw.update(_parse_spoiler(spoiler) if spoiler else _empty_spoiler())

    return raw


def _parse_spoiler(spoiler) -> dict:
    out: dict = {"founded_year_str": None, "founders": [], "website": None, "logo_url": None}

    year_item = spoiler.find(class_="reach-portfolio-card__info-item_year")
    if year_item:
        desc = year_item.find(class_="reach-portfolio-card__info-item-desc")
        out["founded_year_str"] = desc.get_text(strip=True) or None if desc else None

    founders_item = spoiler.find(class_="reach-portfolio-card__info-item_founders")
    if founders_item:
        desc = founders_item.find(class_="reach-portfolio-card__info-item-desc")
        if desc:
            out["founders"] = [
                s.get_text(strip=True)
                for s in desc.find_all("span")
                if s.get_text(strip=True)
            ]

    logo_div = spoiler.find(class_="reach-portfolio-card__logo")
    if logo_div:
        link = logo_div.find("a", class_="reach-logo-card")
        out["website"] = link.get("href") or None if link else None
        img = logo_div.find("img")
        out["logo_url"] = img.get("src") or None if img else None

    return out


def _empty_spoiler() -> dict:
    return {"founded_year_str": None, "founders": [], "website": None, "logo_url": None}
