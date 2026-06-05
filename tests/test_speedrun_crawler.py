import json
from pathlib import Path
from vc_crawler.crawlers.a16z_speedrun.crawler import SpeedrunCrawler
from vc_crawler.models import Company

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "speedrun_portfolio.html"
FIXTURE_SR001 = Path(__file__).parent / "fixtures" / "speedrun_api_sr001.json"
FIXTURE_SR002_P1 = Path(__file__).parent / "fixtures" / "speedrun_api_sr002_p1.json"
FIXTURE_SR002_P2 = Path(__file__).parent / "fixtures" / "speedrun_api_sr002_p2.json"


class _FakeResp:
    def __init__(self, data):
        self._data = data

    @property
    def text(self):
        return self._data if isinstance(self._data, str) else json.dumps(self._data)

    def json(self):
        return self._data if isinstance(self._data, dict) else json.loads(self._data)


class _FakeClient:
    def __init__(self, responses: dict):
        self._responses = responses
        self.calls: list[str] = []

    def get(self, url, **kw):
        self.calls.append(url)
        for key, val in self._responses.items():
            if key in url:
                return _FakeResp(val)
        raise KeyError(f"No fixture for URL: {url}")


def _make_client():
    return _FakeClient({
        "speedrun.a16z.com/companies": FIXTURE_HTML.read_text(encoding="utf-8"),
        "offset=1": json.loads(FIXTURE_SR002_P2.read_text()),
        "cohort=SR001": json.loads(FIXTURE_SR001.read_text()),
        "cohort=SR002": json.loads(FIXTURE_SR002_P1.read_text()),
    })


def test_returns_list_of_companies():
    companies = SpeedrunCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    companies = SpeedrunCrawler(_make_client()).run()
    assert len(companies) == 4


def test_sequential_ids():
    companies = SpeedrunCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3, 4]


def test_all_have_fund_a16z_speedrun():
    companies = SpeedrunCrawler(_make_client()).run()
    assert all(c.fund == "a16z-speedrun" for c in companies)


def test_limit_truncates():
    companies = SpeedrunCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = SpeedrunCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    SpeedrunCrawler(client).run()
    assert any("speedrun.a16z.com/companies" in u for u in client.calls)


def test_fetches_all_cohorts():
    client = _make_client()
    SpeedrunCrawler(client).run()
    assert any("cohort=SR001" in u for u in client.calls)
    assert any("cohort=SR002" in u for u in client.calls)


def test_stage_contains_cohort():
    companies = SpeedrunCrawler(_make_client()).run()
    stages = {c.stage for c in companies}
    assert "SR001" in stages
    assert "SR002" in stages


def test_enrich_false_accepted():
    companies = SpeedrunCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 4


def test_workers_param_accepted():
    companies = SpeedrunCrawler(_make_client()).run(workers=10)
    assert len(companies) == 4
