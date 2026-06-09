from pathlib import Path

from vc_crawler.crawlers.brighteye.crawler import BrighteyeCrawler
from vc_crawler.models import Company

FIXTURE_HTML = Path(__file__).parent / "fixtures" / "brighteye_portfolio.html"


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
    companies = BrighteyeCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_all_fixture_companies():
    assert len(BrighteyeCrawler(_make_client()).run()) == 4


def test_sequential_ids():
    companies = BrighteyeCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3, 4]


def test_all_fund_brighteye():
    companies = BrighteyeCrawler(_make_client()).run()
    assert all(c.fund == "brighteye" for c in companies)


def test_limit_truncates():
    companies = BrighteyeCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = BrighteyeCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    BrighteyeCrawler(client).run()
    assert any("brighteyevc.com/portfolio" in u for u in client.calls)


def test_enrich_false_accepted():
    companies = BrighteyeCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 4


def test_workers_param_accepted():
    companies = BrighteyeCrawler(_make_client()).run(workers=10)
    assert len(companies) == 4
