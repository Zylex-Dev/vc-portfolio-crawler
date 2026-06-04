import vc_crawler.__main__ as cli
from vc_crawler.models import Company


def _sequoia_sample():
    return [Company(id=1, fund="sequoia", name="A", slug="a", fund_url="u", sectors=["AI"])]


def test_main_writes_sequoia_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.sequoia.crawler as seq_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw): return _sequoia_sample()
    monkeypatch.setattr(seq_mod, "SequoiaCrawler", Fake)
    rc = cli.main(["--fund", "sequoia", "--out", str(tmp_path), "--no-enrich", "--format", "both"])
    assert rc == 0
    assert (tmp_path / "sequoia_companies.json").exists()
    assert (tmp_path / "sequoia_companies.csv").exists()


def test_main_writes_a16z_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.a16z.crawler as a16z_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw): return [Company(id=1, fund="a16z", name="GitHub", slug="github", fund_url="u")]
    monkeypatch.setattr(a16z_mod, "A16ZCrawler", Fake)
    rc = cli.main(["--fund", "a16z", "--out", str(tmp_path), "--no-enrich", "--format", "both"])
    assert rc == 0
    assert (tmp_path / "a16z_companies.json").exists()
    assert (tmp_path / "a16z_companies.csv").exists()


def test_limit_passed_to_crawler(tmp_path, monkeypatch):
    import vc_crawler.crawlers.sequoia.crawler as seq_mod
    received = {}
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            received.update(kw)
            return _sequoia_sample()
    monkeypatch.setattr(seq_mod, "SequoiaCrawler", Fake)
    cli.main(["--fund", "sequoia", "--out", str(tmp_path), "--no-enrich", "--format", "json", "--limit", "5"])
    assert received["limit"] == 5


def test_no_enrich_passes_enrich_false(tmp_path, monkeypatch):
    import vc_crawler.crawlers.sequoia.crawler as seq_mod
    received = {}
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            received.update(kw)
            return _sequoia_sample()
    monkeypatch.setattr(seq_mod, "SequoiaCrawler", Fake)
    cli.main(["--fund", "sequoia", "--out", str(tmp_path), "--no-enrich", "--format", "json"])
    assert received["enrich"] is False
