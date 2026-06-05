import pytest

from vc_crawler.http_client import build_session, PoliteClient


class FakeResp:
    def __init__(self, status=200):
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, resp):
        self.resp = resp
        self.calls: list[tuple] = []

    def get(self, url, **kwargs):
        self.calls.append(("get", url, kwargs))
        return self.resp

    def post(self, url, **kwargs):
        self.calls.append(("post", url, kwargs))
        return self.resp


def test_build_session_sets_user_agent():
    s = build_session(user_agent="x/1.0")
    assert s.headers["User-Agent"] == "x/1.0"


def test_build_session_mounts_retry_adapter():
    s = build_session(total_retries=4)
    adapter = s.get_adapter("https://example.com")
    assert adapter.max_retries.total == 4


def test_polite_get_delegates_and_sets_timeout():
    resp = FakeResp(200)
    sess = FakeSession(resp)
    client = PoliteClient(session=sess, delay=0, timeout=15)
    out = client.get("https://example.com", params={"a": 1})
    assert out is resp
    method, url, kwargs = sess.calls[0]
    assert method == "get"
    assert url == "https://example.com"
    assert kwargs["timeout"] == 15
    assert kwargs["params"] == {"a": 1}


def test_polite_get_raises_on_http_error():
    client = PoliteClient(session=FakeSession(FakeResp(500)), delay=0)
    with pytest.raises(RuntimeError):
        client.get("https://example.com")


def test_polite_post_delegates_and_sets_timeout():
    resp = FakeResp(200)
    sess = FakeSession(resp)
    client = PoliteClient(session=sess, delay=0, timeout=15)
    out = client.post("https://example.com", data="foo=bar")
    assert out is resp
    method, url, kwargs = sess.calls[0]
    assert method == "post"
    assert url == "https://example.com"
    assert kwargs["timeout"] == 15
    assert kwargs["data"] == "foo=bar"


def test_polite_post_raises_on_http_error():
    client = PoliteClient(session=FakeSession(FakeResp(500)), delay=0)
    with pytest.raises(RuntimeError):
        client.post("https://example.com")
