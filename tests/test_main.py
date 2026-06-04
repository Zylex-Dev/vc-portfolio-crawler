import sequoia_crawler.__main__ as cli
from sequoia_crawler.models import Company


def _sample():
    return [Company(id=1, name="A", slug="a", sequoia_url="u", sectors=["AI"])]


def test_main_writes_both_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "build_companies", lambda *_: _sample())
    monkeypatch.setattr(cli, "_check_completeness", lambda *_: None)
    monkeypatch.setattr(cli, "apply_stages", lambda *_: None)
    rc = cli.main(["--out", str(tmp_path), "--no-enrich", "--format", "both"])
    assert rc == 0
    assert (tmp_path / "sequoia_companies.json").exists()
    assert (tmp_path / "sequoia_companies.csv").exists()


def test_apply_stages_assigns_by_normalized_name(monkeypatch):
    comps = [
        Company(id=1, name="AdMob", slug="admob", sequoia_url="u"),
        Company(id=2, name="Unlisted Co", slug="x", sequoia_url="u"),
    ]
    monkeypatch.setattr(
        cli, "fetch_stage_map",
        lambda *_: {cli.normalize_name("AdMob"): "Acquired"},
    )
    cli.apply_stages(None, comps)
    assert comps[0].stage == "Acquired"
    assert comps[1].stage is None


def test_apply_stages_survives_fetch_failure(monkeypatch):
    comps = [Company(id=1, name="AdMob", slug="admob", sequoia_url="u")]

    def boom(*_):
        raise RuntimeError("network down")

    monkeypatch.setattr(cli, "fetch_stage_map", boom)
    cli.apply_stages(None, comps)  # must not raise
    assert comps[0].stage is None


def test_main_limit_truncates(tmp_path, monkeypatch):
    many = [Company(id=i, name=str(i), slug=str(i), sequoia_url="u") for i in range(10)]
    monkeypatch.setattr(cli, "build_companies", lambda *_: many)
    monkeypatch.setattr(cli, "_check_completeness", lambda *_: None)
    monkeypatch.setattr(cli, "apply_stages", lambda *_: None)
    captured = {}
    monkeypatch.setattr(cli, "write_json", lambda comps, *_: captured.update(n=len(comps)))
    monkeypatch.setattr(cli, "write_csv", lambda *_: None)
    rc = cli.main(["--out", str(tmp_path), "--no-enrich", "--format", "json", "--limit", "3"])
    assert rc == 0
    assert captured["n"] == 3
