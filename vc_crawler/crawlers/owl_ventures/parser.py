from __future__ import annotations

from bs4 import BeautifulSoup

PORTFOLIO_URL = "https://www.owlvc.com/portfolio"


def parse_portfolio_page(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    return [_parse_card(card) for card in soup.find_all(class_="portfolio-card")]


def _parse_card(card) -> dict:
    raw: dict = {}

    name_el = card.find(class_="text-block-10")
    raw["name"] = name_el.get_text(strip=True) if name_el else ""

    logo_el = card.find("img", class_="image-57")
    raw["logo_url"] = logo_el.get("src") or None if logo_el else None

    acq_el = card.find(class_="acquired-text")
    raw["is_acquired"] = bool(acq_el and "w-condition-invisible" not in acq_el.get("class", []))

    acq_name_el = card.find(class_="text-block-7")
    raw["acquirer"] = (
        acq_name_el.get_text(strip=True) or None
        if raw["is_acquired"] and acq_name_el
        else None
    )

    popup = card.find(class_="pop-up-wrapper")
    raw.update(_parse_popup(popup) if popup else _empty_popup())

    nest = card.find(class_="nest-item-holder")
    link = nest.find("a") if nest else None
    raw["fund_path"] = link.get("href", "") if link else ""

    return raw


def _parse_popup(popup) -> dict:
    out: dict = {"description": None, "website": None,
                 "initial_investment": None, "founded_year_str": None,
                 "founders": [], "sectors": []}

    pop_left = popup.find(class_="pop-up-left")
    if pop_left:
        desc_el = pop_left.find("p", class_="text-color-black")
        out["description"] = desc_el.get_text(strip=True) or None if desc_el else None

        website_el = pop_left.find("a", class_="black-bg")
        out["website"] = website_el.get("href") or None if website_el else None

    for holder in popup.find_all(class_="pop-up-right-content-holder"):
        if "w-condition-invisible" in holder.get("class", []):
            continue
        title_el = holder.find(class_="invaestment-title")  # sic: upstream Webflow typo
        val_el = holder.find("p")
        if not title_el or not val_el:
            continue
        title = title_el.get_text(strip=True)
        val = val_el.get_text(strip=True)
        if not val:
            continue
        if title == "Initial Investment":
            out["initial_investment"] = val
        elif title == "Year Founded":
            out["founded_year_str"] = val
        elif title in ("Founder", "Co-Founders"):
            out["founders"].append(val)

    popup_top = popup.find(class_="pop-up-top")
    if popup_top:
        outer = popup_top.find("div", class_="collection-list-3")
        if outer:
            dyn_lists = outer.find_all("div", class_="w-dyn-list", recursive=False)
            if dyn_lists:
                out["sectors"] = [
                    el.get_text(strip=True)
                    for el in dyn_lists[0].find_all("div", class_="sub-category")
                ]

    return out


def _empty_popup() -> dict:
    return {"description": None, "website": None,
            "initial_investment": None, "founded_year_str": None,
            "founders": [], "sectors": []}
