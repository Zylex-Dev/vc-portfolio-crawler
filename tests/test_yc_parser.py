import json
from pathlib import Path
import pytest
from vc_crawler.crawlers.y_combinator.parser import (
    fetch_education_companies,
    ALGOLIA_URL,
    ALGOLIA_APP_ID,
    ALGOLIA_API_KEY,
)

FIXTURE = Path(__file__).parent / "fixtures" / "yc_algolia_response.json"


class _FakeResp:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class _FakeClient:
    def __init__(self, response):
        self._response = response
        self.calls: list[tuple] = []  # (url, kwargs)

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return _FakeResp(self._response)


def _make_client():
    return _FakeClient(json.loads(FIXTURE.read_text()))


def test_returns_list_of_dicts():
    result = fetch_education_companies(_make_client())
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_all_hits():
    result = fetch_education_companies(_make_client())
    assert len(result) == 3


def test_hits_have_name_field():
    result = fetch_education_companies(_make_client())
    assert all("name" in r for r in result)


def test_makes_one_post_request():
    client = _make_client()
    fetch_education_companies(client)
    assert len(client.calls) == 1


def test_posts_to_algolia_url():
    client = _make_client()
    fetch_education_companies(client)
    url, _ = client.calls[0]
    assert url == ALGOLIA_URL


def test_request_includes_algolia_headers():
    client = _make_client()
    fetch_education_companies(client)
    _, kwargs = client.calls[0]
    headers = kwargs.get("headers", {})
    assert headers.get("x-algolia-application-id") == ALGOLIA_APP_ID
    assert headers.get("x-algolia-api-key") == ALGOLIA_API_KEY


def test_request_filters_education():
    client = _make_client()
    fetch_education_companies(client)
    _, kwargs = client.calls[0]
    body = kwargs.get("json", {})
    assert body.get("filters") == "industries:Education"


def test_constants_non_empty():
    assert ALGOLIA_URL
    assert ALGOLIA_APP_ID
    assert ALGOLIA_API_KEY
