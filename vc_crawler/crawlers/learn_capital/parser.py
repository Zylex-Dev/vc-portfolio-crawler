from __future__ import annotations

import json
import re

PORTFOLIO_URL = "https://learn.vc/ventures"
_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
    re.DOTALL,
)


def parse_ventures_page(html: str) -> list[dict]:
    m = _NEXT_DATA_RE.search(html)
    if not m:
        return []
    data = json.loads(m.group(1))
    ventures = data.get("props", {}).get("pageProps", {}).get("ventures", [])
    return [_extract(v) for v in ventures]


def _extract(v: dict) -> dict:
    d = v.get("data", {})

    name_nodes = d.get("name") or []
    name = name_nodes[0].get("text", "") if name_nodes else ""

    desc_nodes = d.get("description") or []
    description_text = desc_nodes[0].get("text", "") if desc_nodes else ""

    headline_nodes = d.get("headline") or []
    headline_text = headline_nodes[0].get("text", "") if headline_nodes else ""

    visit = d.get("visit") or {}
    website = visit.get("url") if visit.get("link_type") == "Web" else None

    color_logo = d.get("color_logo") or {}
    logo_url = color_logo.get("url") or None

    founders_nodes = d.get("founders") or []
    founders_text = founders_nodes[0].get("text", "") if founders_nodes else ""

    return {
        "name": name,
        "description": description_text or None,
        "headline": headline_text or None,
        "website": website,
        "logo_url": logo_url,
        "founders_text": founders_text,
        "tags": v.get("tags", []),
        "acquired": bool(d.get("acquired", False)),
        "public": bool(d.get("public", False)),
    }
