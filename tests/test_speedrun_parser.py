import json
from pathlib import Path
import pytest
from vc_crawler.crawlers.a16z_speedrun.parser import (
    parse_portfolio_page,
    PORTFOLIO_URL,
    fetch_cohort_companies,
    API_BASE,
)

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "speedrun_portfolio.html"


def test_returns_cohort_list():
    cohorts = parse_portfolio_page(FIXTURE_HTML.read_text(encoding="utf-8"))
    assert cohorts == ["SR001", "SR002"]


def test_returns_list_of_strings():
    cohorts = parse_portfolio_page(FIXTURE_HTML.read_text(encoding="utf-8"))
    assert all(isinstance(c, str) for c in cohorts)


def test_raises_on_missing_next_data():
    with pytest.raises(ValueError, match="__NEXT_DATA__"):
        parse_portfolio_page("<html><body>nothing</body></html>")


def test_raises_on_missing_cohorts_key():
    html = """<html><body>
    <script id="__NEXT_DATA__" type="application/json">
    {"props":{"pageProps":{}}}
    </script></body></html>"""
    with pytest.raises(ValueError, match="cohorts"):
        parse_portfolio_page(html)


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://speedrun.a16z.com/companies/"


FIXTURE_SR001 = Path(__file__).parent / "fixtures" / "speedrun_api_sr001.json"
FIXTURE_SR002_P1 = Path(__file__).parent / "fixtures" / "speedrun_api_sr002_p1.json"
FIXTURE_SR002_P2 = Path(__file__).parent / "fixtures" / "speedrun_api_sr002_p2.json"


class _FakeResp:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class _FakeClient:
    def __init__(self, responses: dict):
        # keys are URL substrings; first match wins
        self._responses = responses
        self.calls: list[str] = []

    def get(self, url, **kw):
        self.calls.append(url)
        for key, val in self._responses.items():
            if key in url:
                return _FakeResp(val)
        raise KeyError(f"No fixture for URL: {url}")


def test_fetch_cohort_returns_all_records_single_page():
    client = _FakeClient({"cohort=SR001": json.loads(FIXTURE_SR001.read_text())})
    results = fetch_cohort_companies(client, "SR001")
    assert len(results) == 2


def test_fetch_cohort_paginates_until_next_is_null():
    client = _FakeClient({
        "offset=1": json.loads(FIXTURE_SR002_P2.read_text()),
        "cohort=SR002": json.loads(FIXTURE_SR002_P1.read_text()),
    })
    results = fetch_cohort_companies(client, "SR002")
    assert len(results) == 2


def test_fetch_cohort_returns_raw_dicts():
    client = _FakeClient({"cohort=SR001": json.loads(FIXTURE_SR001.read_text())})
    results = fetch_cohort_companies(client, "SR001")
    assert isinstance(results[0], dict)
    assert "name" in results[0]


def test_fetch_cohort_makes_at_least_one_request():
    client = _FakeClient({"cohort=SR001": json.loads(FIXTURE_SR001.read_text())})
    fetch_cohort_companies(client, "SR001")
    assert len(client.calls) >= 1


def test_fetch_cohort_first_url_contains_cohort_param():
    client = _FakeClient({"cohort=SR001": json.loads(FIXTURE_SR001.read_text())})
    fetch_cohort_companies(client, "SR001")
    assert "cohort=SR001" in client.calls[0]


def test_api_base_constant():
    assert API_BASE == "https://speedrun-be.a16z.com/api/companies/companies/"
