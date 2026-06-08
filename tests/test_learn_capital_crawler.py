from pathlib import Path

from vc_crawler.crawlers.learn_capital.crawler import LearnCrawler
from vc_crawler.models import Company

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "learn_capital_ventures.html"


class _FakeResp:
    def __init__(self, text: str):
        self.text = text


class _FakeClient:
    def __init__(self, html: str):
        self._html = html
        self.calls: list[str] = []

    def get(self, url, **kw):
        self.calls.append(url)
        return _FakeResp(self._html)


def _make_client():
    return _FakeClient(FIXTURE_HTML.read_text(encoding="utf-8"))


def test_returns_list_of_companies():
    companies = LearnCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    assert len(LearnCrawler(_make_client()).run()) == 3


def test_sequential_ids():
    companies = LearnCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3]


def test_all_fund_learn_capital():
    companies = LearnCrawler(_make_client()).run()
    assert all(c.fund == "learn-capital" for c in companies)


def test_limit_truncates():
    companies = LearnCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = LearnCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    LearnCrawler(client).run()
    assert any("learn.vc/ventures" in u for u in client.calls)


def test_enrich_false_accepted():
    companies = LearnCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 3


def test_workers_param_accepted():
    companies = LearnCrawler(_make_client()).run(workers=10)
    assert len(companies) == 3
