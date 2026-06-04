from sequoia_crawler.sitemap import fetch_company_slugs

SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://sequoiacap.com/companies/admob/</loc></url>
  <url><loc>https://sequoiacap.com/companies/stripe/</loc></url>
  <url><loc>https://sequoiacap.com/our-companies/</loc></url>
</urlset>"""


class FakeResp:
    text = SAMPLE_XML


class FakeClient:
    def get(self, url, **kwargs):
        return FakeResp()


def test_fetch_company_slugs_extracts_only_company_slugs():
    slugs = fetch_company_slugs(FakeClient())
    assert slugs == {"admob", "stripe"}
