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
    assert (tmp_path / "sequoia" / "companies.json").exists()
    assert (tmp_path / "sequoia" / "companies.csv").exists()


def test_main_writes_a16z_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.a16z.crawler as a16z_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw): return [Company(id=1, fund="a16z", name="GitHub", slug="github", fund_url="u")]
    monkeypatch.setattr(a16z_mod, "A16ZCrawler", Fake)
    rc = cli.main(["--fund", "a16z", "--out", str(tmp_path), "--no-enrich", "--format", "both"])
    assert rc == 0
    assert (tmp_path / "a16z" / "companies.json").exists()
    assert (tmp_path / "a16z" / "companies.csv").exists()


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


def test_build_companies_assigns_sequential_ids(monkeypatch):
    """Verifies sequential IDs are assigned regardless of WordPress IDs."""
    import vc_crawler.crawlers.sequoia.api as seq_api
    raws = [
        {"id": 900, "slug": "a", "link": "u", "title": {"rendered": "A"},
         "categories": [], "modified": None},
        {"id": 12, "slug": "b", "link": "u", "title": {"rendered": "B"},
         "categories": [], "modified": None},
        {"id": 555, "slug": "c", "link": "u", "title": {"rendered": "C"},
         "categories": [], "modified": None},
    ]
    monkeypatch.setattr(seq_api, "fetch_categories", lambda *_: {})
    monkeypatch.setattr(seq_api, "iter_companies", lambda *_: iter(raws))
    from vc_crawler.crawlers.sequoia.crawler import SequoiaCrawler
    class FakeClient: pass
    crawler = SequoiaCrawler(FakeClient())
    # Patch out completeness/stages/enrich — not testing those here
    monkeypatch.setattr(crawler, "_check_completeness", lambda *_: None)
    monkeypatch.setattr(crawler, "_apply_stages", lambda *_: None)
    companies = crawler.run(enrich=False)
    assert [c.id for c in companies] == [1, 2, 3]
    assert [c.slug for c in companies] == ["a", "b", "c"]


def test_apply_stages_assigns_by_normalized_name(monkeypatch):
    """Verifies _apply_stages maps stage values to companies by name."""
    from vc_crawler.crawlers.sequoia.crawler import SequoiaCrawler
    from vc_crawler.crawlers.sequoia.listing import normalize_name
    import vc_crawler.crawlers.sequoia.crawler as crawler_mod
    comps = [
        Company(id=1, fund="sequoia", name="AdMob", slug="admob", fund_url="u"),
        Company(id=2, fund="sequoia", name="Unlisted Co", slug="x", fund_url="u"),
    ]
    monkeypatch.setattr(
        crawler_mod, "fetch_stage_map",
        lambda *_: {normalize_name("AdMob"): "Acquired"},
    )
    class FakeClient: pass
    crawler = SequoiaCrawler(FakeClient())
    crawler._apply_stages(comps)
    assert comps[0].stage == "Acquired"
    assert comps[1].stage is None


def test_apply_stages_survives_fetch_failure(monkeypatch):
    """Verifies _apply_stages doesn't raise on network failure."""
    from vc_crawler.crawlers.sequoia.crawler import SequoiaCrawler
    import vc_crawler.crawlers.sequoia.crawler as crawler_mod

    def boom(*_):
        raise RuntimeError("network down")

    monkeypatch.setattr(crawler_mod, "fetch_stage_map", boom)
    class FakeClient: pass
    comps = [Company(id=1, fund="sequoia", name="AdMob", slug="admob", fund_url="u")]
    crawler = SequoiaCrawler(FakeClient())
    crawler._apply_stages(comps)  # must not raise
    assert comps[0].stage is None


def test_main_writes_speedrun_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.a16z_speedrun.crawler as sr_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="a16z-speedrun", name="Cantor", slug="cantor",
                            fund_url="https://speedrun.a16z.com/companies/cantor")]
    monkeypatch.setattr(sr_mod, "SpeedrunCrawler", Fake)
    rc = cli.main(["--fund", "a16z-speedrun", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "a16z-speedrun" / "companies.json").exists()
    assert (tmp_path / "a16z-speedrun" / "companies.csv").exists()


def test_main_writes_owl_ventures_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.owl_ventures.crawler as owl_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="owl-ventures", name="Amira Learning",
                            slug="amira", fund_url="https://www.owlvc.com/portfolio/amira")]
    monkeypatch.setattr(owl_mod, "OwlCrawler", Fake)
    rc = cli.main(["--fund", "owl-ventures", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "owl-ventures" / "companies.json").exists()
    assert (tmp_path / "owl-ventures" / "companies.csv").exists()


def test_main_writes_reach_capital_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.reach_capital.crawler as rc_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="reach-capital", name="BookNook",
                            slug="booknook",
                            fund_url="https://www.reachcapital.com/companies/?sector=learning")]
    monkeypatch.setattr(rc_mod, "ReachCrawler", Fake)
    rc = cli.main(["--fund", "reach-capital", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "reach-capital" / "companies.json").exists()
    assert (tmp_path / "reach-capital" / "companies.csv").exists()


def test_main_writes_gsv_ventures_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.gsv_ventures.crawler as gsv_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="gsv-ventures", name="EduLearn Pro",
                            slug="edulearn-pro",
                            fund_url="https://gsv.ventures/portfolio/")]
    monkeypatch.setattr(gsv_mod, "GSVCrawler", Fake)
    rc = cli.main(["--fund", "gsv-ventures", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "gsv-ventures" / "companies.json").exists()
    assert (tmp_path / "gsv-ventures" / "companies.csv").exists()


def test_main_writes_learn_capital_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.learn_capital.crawler as lc_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="learn-capital", name="Edify Academy",
                            slug="edify-academy",
                            fund_url="https://learn.vc/ventures")]
    monkeypatch.setattr(lc_mod, "LearnCrawler", Fake)
    rc = cli.main(["--fund", "learn-capital", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "learn-capital" / "companies.json").exists()
    assert (tmp_path / "learn-capital" / "companies.csv").exists()


def test_fund_registry_contains_brighteye():
    from vc_crawler.__main__ import _FUND_REGISTRY
    assert "brighteye" in _FUND_REGISTRY


def test_main_writes_brighteye_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.brighteye.crawler as be_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="brighteye", name="Zen Educate",
                            slug="zen-educate",
                            fund_url="https://www.brighteyevc.com/portfolio")]
    monkeypatch.setattr(be_mod, "BrighteyeCrawler", Fake)
    rc = cli.main(["--fund", "brighteye", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "brighteye" / "companies.json").exists()
    assert (tmp_path / "brighteye" / "companies.csv").exists()


def test_fund_registry_contains_y_combinator():
    from vc_crawler.__main__ import _FUND_REGISTRY
    assert "y-combinator" in _FUND_REGISTRY


def test_main_writes_y_combinator_outputs(tmp_path, monkeypatch):
    import vc_crawler.crawlers.y_combinator.crawler as yc_mod
    class Fake:
        def __init__(self, client): pass
        def run(self, **kw):
            return [Company(id=1, fund="y-combinator", name="Codecademy",
                            slug="codecademy",
                            fund_url="https://www.ycombinator.com/companies/codecademy")]
    monkeypatch.setattr(yc_mod, "YCCrawler", Fake)
    rc = cli.main(["--fund", "y-combinator", "--out", str(tmp_path), "--format", "both"])
    assert rc == 0
    assert (tmp_path / "y-combinator" / "companies.json").exists()
    assert (tmp_path / "y-combinator" / "companies.csv").exists()
