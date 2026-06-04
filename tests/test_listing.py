from pathlib import Path

from sequoia_crawler.listing import (
    fetch_stage_map,
    normalize_name,
    parse_stage_map,
    total_pages,
)

FIXTURE = Path(__file__).parent / "fixtures" / "our_companies_listing.html"


def test_parse_stage_map_extracts_current_stage():
    html = FIXTURE.read_text(encoding="utf-8")
    stages = parse_stage_map(html)
    assert stages[normalize_name("[24]7.ai")] == "Growth"
    assert stages[normalize_name("Abby Care")] == "Early"
    assert stages[normalize_name("AdMob")] == "Acquired"
    assert stages[normalize_name("Apex")] == "Pre-Seed/Seed"


def test_parse_stage_map_uses_current_stage_not_first_partnered():
    # Airbnb's "First Partnered" cell reads "Pre-Seed/Seed (2009)";
    # the Current Stage column must win.
    html = FIXTURE.read_text(encoding="utf-8")
    stages = parse_stage_map(html)
    assert stages[normalize_name("Airbnb")] == "IPO"


def test_total_pages_reads_from_settings():
    html = FIXTURE.read_text(encoding="utf-8")
    assert total_pages(html) == 8


def test_total_pages_defaults_to_one_when_absent():
    assert total_pages("<html><body>no settings</body></html>") == 1


def test_normalize_name_unescapes_and_casefolds():
    assert normalize_name("AdMob &amp; Co") == normalize_name("admob & co")
    assert normalize_name("  Spaced   Out  ") == "spaced out"


class FakeResp:
    def __init__(self, text):
        self.text = text


class FakeClient:
    def __init__(self, by_page):
        self.by_page = by_page
        self.calls = []

    def get(self, url, params=None, **kwargs):
        self.calls.append(params)
        page = (params or {}).get("_paged", 1)
        return FakeResp(self.by_page[page])


def _page(total, name, stage):
    return (
        '<html><head><script>window.FWP_JSON = {"settings":{"pager":'
        f'{{"total_pages":{total}}}}}}};</script></head><body>'
        '<div class="company-listing">'
        f'<tr><th class="company-listing__head" scope="row">{name}</th>'
        f'<td class="u-lg-hide" data-order="2">{stage}</td></tr>'
        "</div></body></html>"
    )


def test_fetch_stage_map_paginates_and_merges():
    client = FakeClient({
        1: _page(2, "Alpha", "Growth"),
        2: _page(2, "Beta", "Early"),
    })
    stages = fetch_stage_map(client, base="https://example.test/our-companies/")
    assert stages[normalize_name("Alpha")] == "Growth"
    assert stages[normalize_name("Beta")] == "Early"
    # Page 1 fetched plain; page 2 fetched via ?_paged=2.
    assert client.calls == [None, {"_paged": 2}]
