from __future__ import annotations

import json
import re

PORTFOLIO_URL = "https://a16z.com/portfolio/"

_JS_GLOBAL_RE = re.compile(
    r"window\.a16z_portfolio_companies\s*=\s*(\[.*?\])\s*;",
    re.DOTALL,
)


def parse_portfolio_page(html_text: str) -> list[dict]:
    """Extract the JS-embedded company array from the a16z portfolio page."""
    m = _JS_GLOBAL_RE.search(html_text)
    if not m:
        raise ValueError(
            "Could not find window.a16z_portfolio_companies in page HTML. "
            "The page structure may have changed."
        )
    return json.loads(m.group(1))
