from __future__ import annotations

ALGOLIA_URL = "https://45bwzj1sgc-dsn.algolia.net/1/indexes/YCCompany_production/query"
ALGOLIA_APP_ID = "45BWZJ1SGC"
# Public read-only search key — embedded in YC's own frontend JS, no write permissions
ALGOLIA_API_KEY = (
    "NzllNTY5MzJiZGM2OTY2ZTQwMDEzOTNhYWZiZGRjODlhYzVkNjBmOGRjNzJiMWM4ZTU0ZDlhYT"
    "ZjOTJiMjlhMWFuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3By"
    "b2R1Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZX"
    "JzPSU1QiUyMnljZGNfcHVibGljJTIyJTVE"
)


def fetch_education_companies(client) -> list[dict]:
    """POST to Algolia and return raw hit dicts for all Education companies."""
    resp = client.post(
        ALGOLIA_URL,
        headers={
            "x-algolia-application-id": ALGOLIA_APP_ID,
            "x-algolia-api-key": ALGOLIA_API_KEY,
        },
        json={
            "query": "",
            "hitsPerPage": 1000,
            "filters": "industries:Education",
        },
    )
    data = resp.json()
    assert len(data["hits"]) < data.get("hitsPerPage", 1000), (
        "Algolia returned a full page; results may be truncated. "
        "Increase hitsPerPage or add pagination."
    )
    return data["hits"]
