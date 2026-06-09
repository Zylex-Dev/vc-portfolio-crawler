from pathlib import Path

from vc_crawler.crawlers.new_schools.crawler import NewSchoolsCrawler
from vc_crawler.crawlers.new_schools.parser import (
    PORTFOLIO_URL, INIT_YEAR_API,
)
from vc_crawler.models import Company

LISTING_HTML = (Path(__file__).parent / "fixtures" / "newschools_listing.html").read_text(encoding="utf-8")
DETAIL_HTML  = (Path(__file__).parent / "fixtures" / "newschools_detail.html").read_text(encoding="utf-8")

INIT_YEAR_JSON = '[{"id": 714, "name": "2024"}, {"id": 720, "name": "2023"}]'


class _FakeResp:
    def __init__(self, text: str):
        self.text = text


class _FakeClient:
    def __init__(self, responses: dict[str, str]):
        self._responses = responses
        self.calls: list[str] = []

    def get(self, url, **kw):
        self.calls.append(url)
        return _FakeResp(self._responses.get(url, "<html></html>"))


def _make_client(extra_listing: dict[str, str] | None = None) -> _FakeClient:
    responses = {
        INIT_YEAR_API: INIT_YEAR_JSON,
        PORTFOLIO_URL: LISTING_HTML,
        "https://www.newschools.org/venture/acme-edu/":   DETAIL_HTML,
        "https://www.newschools.org/venture/beta-learn/": DETAIL_HTML,
    }
    if extra_listing:
        responses.update(extra_listing)
    return _FakeClient(responses)


# ── basic shape ───────────────────────────────────────────────────────────────

def test_returns_list_of_companies():
    companies = NewSchoolsCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)

def test_returns_two_companies():
    assert len(NewSchoolsCrawler(_make_client()).run()) == 2

def test_sequential_ids():
    ids = [c.id for c in NewSchoolsCrawler(_make_client()).run()]
    assert ids == [1, 2]

def test_all_fund_new_schools():
    companies = NewSchoolsCrawler(_make_client()).run()
    assert all(c.fund == "new-schools" for c in companies)

# ── limit ─────────────────────────────────────────────────────────────────────

def test_limit_truncates():
    assert len(NewSchoolsCrawler(_make_client()).run(limit=1)) == 1

def test_limit_preserves_sequential_ids():
    ids = [c.id for c in NewSchoolsCrawler(_make_client()).run(limit=1)]
    assert ids == [1]

# ── URL calls ─────────────────────────────────────────────────────────────────

def test_fetches_init_year_api():
    client = _make_client()
    NewSchoolsCrawler(client).run()
    assert INIT_YEAR_API in client.calls

def test_fetches_portfolio_page():
    client = _make_client()
    NewSchoolsCrawler(client).run()
    assert PORTFOLIO_URL in client.calls

def test_fetches_detail_pages_when_enrich_true():
    client = _make_client()
    NewSchoolsCrawler(client).run(enrich=True)
    assert "https://www.newschools.org/venture/acme-edu/" in client.calls
    assert "https://www.newschools.org/venture/beta-learn/" in client.calls

def test_skips_detail_pages_when_enrich_false():
    client = _make_client()
    NewSchoolsCrawler(client).run(enrich=False)
    assert "https://www.newschools.org/venture/acme-edu/" not in client.calls

# ── enrichment content ────────────────────────────────────────────────────────

def test_website_populated_after_enrich():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=True)
    assert all(c.website is not None for c in companies)

def test_description_populated_after_enrich():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=True)
    assert all(c.description is not None for c in companies)

def test_website_none_without_enrich():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert all(c.website is None for c in companies)

# ── pagination ────────────────────────────────────────────────────────────────

def test_pagination_fetches_page_2():
    """Listing with max_page=2 → crawler must fetch PORTFOLIO_URL + '2/'."""
    two_page_listing = LISTING_HTML.replace('data-max-page="1"', 'data-max-page="2"')
    page2_url = PORTFOLIO_URL + "2/"
    client = _make_client(extra_listing={
        PORTFOLIO_URL: two_page_listing,
        page2_url: LISTING_HTML,
    })
    NewSchoolsCrawler(client).run(enrich=False)
    assert page2_url in client.calls

def test_pagination_accumulates_companies():
    """Two pages of 2 each → 4 companies total."""
    two_page_listing = LISTING_HTML.replace('data-max-page="1"', 'data-max-page="2"')
    page2_url = PORTFOLIO_URL + "2/"
    client = _make_client(extra_listing={
        PORTFOLIO_URL: two_page_listing,
        page2_url: LISTING_HTML,
    })
    companies = NewSchoolsCrawler(client).run(enrich=False)
    assert len(companies) == 4

# ── normalizer integration ────────────────────────────────────────────────────

def test_invested_year_resolved():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert companies[0].invested_year == 2024   # acme-edu: init_year_ids=[714] → 2024
    assert companies[1].invested_year == 2023   # beta-learn: init_year_ids=[720] → 2023

def test_stage_past_for_first_company():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert companies[0].stage == "Past"

def test_stage_none_for_second_company():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert companies[1].stage is None

# ── param acceptance ──────────────────────────────────────────────────────────

def test_enrich_false_accepted():
    companies = NewSchoolsCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 2

def test_workers_param_accepted():
    companies = NewSchoolsCrawler(_make_client()).run(workers=10)
    assert len(companies) == 2
