import json
from pathlib import Path
from vc_crawler.crawlers.y_combinator.crawler import YCCrawler
from vc_crawler.models import Company

FIXTURE = Path(__file__).parent / "fixtures" / "yc_algolia_response.json"


class _FakeResp:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class _FakeClient:
    def __init__(self, response):
        self._response = response
        self.calls: list[tuple] = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _FakeResp(self._response)


def _make_client():
    return _FakeClient(json.loads(FIXTURE.read_text()))


def test_returns_list_of_companies():
    companies = YCCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    companies = YCCrawler(_make_client()).run()
    assert len(companies) == 3


def test_sequential_ids():
    companies = YCCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3]


def test_all_have_fund_y_combinator():
    companies = YCCrawler(_make_client()).run()
    assert all(c.fund == "y-combinator" for c in companies)


def test_limit_truncates():
    companies = YCCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = YCCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_makes_one_post_request():
    client = _make_client()
    YCCrawler(client).run()
    assert len(client.calls) == 1


def test_enrich_false_accepted():
    companies = YCCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 3


def test_workers_param_accepted():
    companies = YCCrawler(_make_client()).run(workers=10)
    assert len(companies) == 3


def test_first_company_name():
    companies = YCCrawler(_make_client()).run()
    assert companies[0].name == "Codecademy"


def test_acquired_stage():
    companies = YCCrawler(_make_client()).run()
    codecademy = next(c for c in companies if c.slug == "codecademy")
    assert codecademy.stage == "Acquired"


def test_invested_year_from_batch():
    companies = YCCrawler(_make_client()).run()
    codecademy = next(c for c in companies if c.slug == "codecademy")
    assert codecademy.invested_year == 2011
