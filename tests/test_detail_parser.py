from pathlib import Path

from sequoia_crawler.detail_parser import parse_detail

FIXTURE = Path(__file__).parent / "fixtures" / "admob_like.html"


def test_parse_detail_extracts_all_fields():
    data = parse_detail(FIXTURE.read_text(encoding="utf-8"))
    assert data["website"] == "https://www.admob.com"
    assert "pay-per-click" in data["description"]
    assert data["status"] == "Acquired"
    assert data["status_year"] == 2010
    assert data["founded_year"] == 2006
    assert data["partnered_year"] == 2006
    assert data["logo_url"].endswith("admob-logo.png")


def test_parse_detail_missing_fields_are_none():
    data = parse_detail("<html><body><p>nothing here</p></body></html>")
    assert data["website"] is None
    assert data["description"] is None
    assert data["status"] is None
    assert data["status_year"] is None
    assert data["founded_year"] is None
    assert data["partnered_year"] is None
    assert data["logo_url"] is None
