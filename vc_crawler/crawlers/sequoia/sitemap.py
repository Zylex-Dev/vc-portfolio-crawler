from __future__ import annotations

import re

SITEMAP_URL = "https://sequoiacap.com/company-sitemap.xml"
_SLUG_RE = re.compile(r"/companies/([^/]+)/")


def fetch_company_slugs(client, url: str = SITEMAP_URL) -> set[str]:
    """Return the set of company slugs listed in the company sitemap."""
    resp = client.get(url)
    return set(_SLUG_RE.findall(resp.text))
