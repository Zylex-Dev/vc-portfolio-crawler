from sequoia_crawler.api import fetch_categories, iter_companies, to_company


class FakeResp:
    def __init__(self, payload, headers=None):
        self._payload = payload
        self.headers = headers or {}

    def json(self):
        return self._payload


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params=None, **kwargs):
        self.calls.append((url, params))
        return self.responses.pop(0)


def test_fetch_categories_builds_id_name_map():
    resp = FakeResp(
        [{"id": 189, "name": "AI"}, {"id": 196, "name": "Fintech"}],
        headers={"X-WP-TotalPages": "1"},
    )
    mapping = fetch_categories(FakeClient([resp]))
    assert mapping == {189: "AI", 196: "Fintech"}


def test_iter_companies_paginates_via_total_pages_header():
    page1 = FakeResp([{"id": 1}, {"id": 2}], headers={"X-WP-TotalPages": "2"})
    page2 = FakeResp([{"id": 3}], headers={"X-WP-TotalPages": "2"})
    client = FakeClient([page1, page2])
    ids = [c["id"] for c in iter_companies(client)]
    assert ids == [1, 2, 3]
    assert len(client.calls) == 2


def test_to_company_maps_fields_and_assigns_given_id():
    raw = {
        "id": 22119, "slug": "admob",
        "link": "https://sequoiacap.com/companies/admob/",
        "title": {"rendered": "AdMob &amp; Co"},
        "categories": [186, 1],
        "modified": "2026-06-02T21:10:47",
    }
    c = to_company(raw, {186: "GTM", 1: "Uncategorized"}, company_id=7)
    # Sequential id, not the WordPress post id from the API.
    assert c.id == 7
    assert c.name == "AdMob & Co"
    assert c.slug == "admob"
    assert c.sequoia_url == "https://sequoiacap.com/companies/admob/"
    assert c.sectors == ["GTM"]
    assert c.source_modified == "2026-06-02T21:10:47"
