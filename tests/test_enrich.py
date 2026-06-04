from vc_crawler.crawlers.sequoia.enrich import enrich_company, enrich_all
from vc_crawler.models import Company

HTML = (
    '<html><head>'
    '<meta property="og:description" content="Desc">'
    '</head><body>'
    '<a href="https://www.example.com">Visit website</a>'
    '<span>Founded 2010</span>'
    '</body></html>'
)


class OkClient:
    def __init__(self, text):
        self._text = text

    def get(self, url, **kwargs):
        class R:
            text = self._text
        return R()


class FailClient:
    def get(self, url, **kwargs):
        raise RuntimeError("boom")


def _company(slug="a"):
    return Company(
        id=1, fund="sequoia", name="A", slug=slug,
        fund_url=f"https://sequoiacap.com/companies/{slug}/",
    )


def test_enrich_company_merges_parsed_fields():
    c = enrich_company(OkClient(HTML), _company())
    assert c.website == "https://www.example.com"
    assert c.description == "Desc"
    assert c.founded_year == 2010


def test_enrich_company_survives_fetch_error():
    c = enrich_company(FailClient(), _company())
    assert c.website is None
    assert c.name == "A"


def test_enrich_all_preserves_input_order():
    companies = [_company("a"), _company("b"), _company("c")]
    out = enrich_all(OkClient("<html></html>"), companies, workers=3)
    assert [c.slug for c in out] == ["a", "b", "c"]
