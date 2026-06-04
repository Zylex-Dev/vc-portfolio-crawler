import sequoia_crawler.__main__ as cli
from sequoia_crawler.models import Company


def _sample():
    return [Company(id=1, name="A", slug="a", sequoia_url="u", sectors=["AI"])]


def test_main_writes_both_outputs(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "build_companies", lambda client: _sample())
    monkeypatch.setattr(cli, "_check_completeness", lambda client, companies: None)
    rc = cli.main(["--out", str(tmp_path), "--no-enrich", "--format", "both"])
    assert rc == 0
    assert (tmp_path / "sequoia_companies.json").exists()
    assert (tmp_path / "sequoia_companies.csv").exists()


def test_main_limit_truncates(tmp_path, monkeypatch):
    many = [Company(id=i, name=str(i), slug=str(i), sequoia_url="u") for i in range(10)]
    monkeypatch.setattr(cli, "build_companies", lambda client: many)
    monkeypatch.setattr(cli, "_check_completeness", lambda client, companies: None)
    captured = {}
    monkeypatch.setattr(cli, "write_json", lambda comps, path: captured.update(n=len(comps)))
    monkeypatch.setattr(cli, "write_csv", lambda comps, path: None)
    rc = cli.main(["--out", str(tmp_path), "--no-enrich", "--format", "json", "--limit", "3"])
    assert rc == 0
    assert captured["n"] == 3
