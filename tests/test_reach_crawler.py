from pathlib import Path
from vc_crawler.crawlers.reach_capital.crawler import ReachCrawler
from vc_crawler.crawlers.reach_capital.parser import PORTFOLIO_URL, AJAX_URL, NONCE_URL
from vc_crawler.models import Company

PORTFOLIO_HTML = (
    Path(__file__).parent / "fixtures" / "reach_capital_portfolio.html"
).read_text(encoding="utf-8")

AJAX_HTML = (
    Path(__file__).parent / "fixtures" / "reach_capital_ajax.html"
).read_text(encoding="utf-8")

NONCE_JSON = '{"success":true,"data":{"nonce":"test-nonce-123"}}'


class _FakeResp:
    def __init__(self, text: str):
        self.text = text


class _FakeClient:
    """
    get_responses: popped in order for each client.get() call.
    post_responses: popped in order for each client.post() call.
    """
    def __init__(self, get_responses: list[str], post_responses: list[str]):
        self._gets = list(get_responses)
        self._posts = list(post_responses)
        self.get_calls: list[str] = []
        self.post_calls: list[str] = []
        self.post_data: list = []

    def get(self, url, **kw):
        self.get_calls.append(url)
        return _FakeResp(self._gets.pop(0))

    def post(self, url, **kw):
        self.post_calls.append(url)
        self.post_data.append(kw.get("data", ""))
        return _FakeResp(self._posts.pop(0))


def _make_client(extra_ajax_pages: int = 0):
    """
    Standard client: page HTML + nonce + one AJAX batch + empty stop signal.
    extra_ajax_pages adds additional AJAX batches before the stop signal.
    """
    return _FakeClient(
        get_responses=[PORTFOLIO_HTML, NONCE_JSON],
        post_responses=[AJAX_HTML] * (1 + extra_ajax_pages) + [""],
    )


def test_returns_list_of_companies():
    companies = ReachCrawler(_make_client()).run()
    assert all(isinstance(c, Company) for c in companies)


def test_returns_combined_companies():
    # 3 from portfolio page + 2 from AJAX batch
    companies = ReachCrawler(_make_client()).run()
    assert len(companies) == 5


def test_all_fund_reach_capital():
    companies = ReachCrawler(_make_client()).run()
    assert all(c.fund == "reach-capital" for c in companies)


def test_sequential_ids():
    companies = ReachCrawler(_make_client()).run()
    assert [c.id for c in companies] == [1, 2, 3, 4, 5]


def test_limit_truncates():
    companies = ReachCrawler(_make_client()).run(limit=2)
    assert len(companies) == 2


def test_limit_preserves_sequential_ids():
    companies = ReachCrawler(_make_client()).run(limit=2)
    assert [c.id for c in companies] == [1, 2]


def test_fetches_portfolio_page():
    client = _make_client()
    ReachCrawler(client).run()
    assert PORTFOLIO_URL in client.get_calls


def test_fetches_nonce():
    client = _make_client()
    ReachCrawler(client).run()
    assert NONCE_URL in client.get_calls


def test_posts_to_ajax_url():
    client = _make_client()
    ReachCrawler(client).run()
    assert AJAX_URL in client.post_calls


def test_stops_when_ajax_returns_empty():
    # Empty response after first batch — should stop and return 3+2=5 companies
    client = _make_client()
    companies = ReachCrawler(client).run()
    assert len(companies) == 5
    assert len(client.post_calls) == 2  # one real batch + one empty stop


def test_offset_increments_in_ajax_posts():
    client = _make_client(extra_ajax_pages=1)
    ReachCrawler(client).run()
    # First POST: offset=16, second POST: offset=32, third POST (empty stop): offset=48
    assert "args%5Boffset%5D=16" in client.post_data[0]
    assert "args%5Boffset%5D=32" in client.post_data[1]


def test_enrich_false_accepted():
    companies = ReachCrawler(_make_client()).run(enrich=False)
    assert len(companies) == 5


def test_workers_param_accepted():
    companies = ReachCrawler(_make_client()).run(workers=10)
    assert len(companies) == 5
