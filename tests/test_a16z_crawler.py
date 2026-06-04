from pathlib import Path
from vc_crawler.crawlers.a16z.crawler import A16ZCrawler
from vc_crawler.models import Company

FIXTURE = Path(__file__).parent / "fixtures" / "a16z_portfolio.html"


class _FakeResp:
    def __init__(self, text): self.text = text

class _FakeClient:
    def __init__(self, html):
        self._html = html
        self.calls: list[str] = []
    def get(self, url, **kw):
        self.calls.append(url)
        return _FakeResp(self._html)


def test_returns_list_of_companies():
    c = A16ZCrawler(_FakeClient(FIXTURE.read_text())).run(enrich=False)
    assert all(isinstance(x, Company) for x in c)

def test_returns_all_fixture_companies():
    c = A16ZCrawler(_FakeClient(FIXTURE.read_text())).run(enrich=False)
    assert len(c) == 3

def test_sequential_ids():
    c = A16ZCrawler(_FakeClient(FIXTURE.read_text())).run(enrich=False)
    assert [x.id for x in c] == [1, 2, 3]

def test_all_have_fund_a16z():
    c = A16ZCrawler(_FakeClient(FIXTURE.read_text())).run(enrich=False)
    assert all(x.fund == "a16z" for x in c)

def test_limit_truncates():
    c = A16ZCrawler(_FakeClient(FIXTURE.read_text())).run(enrich=False, limit=2)
    assert len(c) == 2

def test_fetches_portfolio_url():
    client = _FakeClient(FIXTURE.read_text())
    A16ZCrawler(client).run(enrich=False)
    assert any("a16z.com/portfolio" in u for u in client.calls)
