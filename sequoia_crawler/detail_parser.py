from __future__ import annotations

import html
import re
from typing import Optional

from bs4 import BeautifulSoup

# Milestone label + optional year (e.g. "Acquired 2010", "IPO 2019", "Public").
_STATUS_RE = re.compile(
    r"\b(Acquired|Acquisition|IPO|Public|Merged)\b\s*(\d{4})?", re.IGNORECASE
)
_FOUNDED_RE = re.compile(r"Founded\s+(\d{4})", re.IGNORECASE)
_PARTNERED_RE = re.compile(r"Partnered\s+(\d{4})", re.IGNORECASE)

# Canonical spelling for the milestone labels Sequoia uses.
_STATUS_NORMALIZE = {
    "acquired": "Acquired",
    "acquisition": "Acquired",
    "ipo": "IPO",
    "public": "Public",
    "merged": "Merged",
}

# Hosts that are never the company's own marketing site.
_SKIP_HOSTS = (
    "sequoiacap.com", "twitter.com", "x.com", "facebook.com",
    "linkedin.com", "instagram.com", "youtube.com", "t.co", "medium.com",
)


def _meta(soup: BeautifulSoup, prop: Optional[str] = None,
          name: Optional[str] = None) -> Optional[str]:
    if prop:
        tag = soup.find("meta", property=prop)
        if tag and tag.get("content"):
            return tag["content"].strip()
    if name:
        tag = soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return None


def _is_external(href: str) -> bool:
    return href.startswith("http") and not any(h in href for h in _SKIP_HOSTS)


def _find_website(soup: BeautifulSoup) -> Optional[str]:
    # 1) An explicit "visit website"-style call to action.
    for a in soup.find_all("a", href=True):
        label = a.get_text(" ", strip=True).lower()
        if ("website" in label or "visit" in label) and _is_external(a["href"]):
            return a["href"]
    # 2) Fallback: the first external, non-social link on the page.
    for a in soup.find_all("a", href=True):
        if _is_external(a["href"]):
            return a["href"]
    return None


def _search_year(pattern: re.Pattern, text: str) -> Optional[int]:
    m = pattern.search(text)
    return int(m.group(1)) if m else None


def _find_description(soup: BeautifulSoup) -> Optional[str]:
    # The company blurb is rendered in a `div.wysiwyg` block on the detail page.
    node = soup.select_one("div.wysiwyg")
    if node:
        text = node.get_text(" ", strip=True)
        if text:
            return text
    return _meta(soup, prop="og:description", name="description")


def _find_logo(soup: BeautifulSoup) -> Optional[str]:
    img = soup.select_one("img.company__logo-image")
    if img and img.get("src"):
        return img["src"].strip()
    return _meta(soup, prop="og:image")


def parse_detail(html_text: str) -> dict:
    soup = BeautifulSoup(html_text, "lxml")
    text = soup.get_text(" ", strip=True)

    description = _find_description(soup)

    status = None
    status_year = None
    m = _STATUS_RE.search(text)
    if m:
        status = _STATUS_NORMALIZE.get(m.group(1).lower(), m.group(1).title())
        if m.group(2):
            status_year = int(m.group(2))

    return {
        "website": _find_website(soup),
        "description": html.unescape(description) if description else None,
        "status": status,
        "status_year": status_year,
        "founded_year": _search_year(_FOUNDED_RE, text),
        "partnered_year": _search_year(_PARTNERED_RE, text),
        "logo_url": _find_logo(soup),
    }
