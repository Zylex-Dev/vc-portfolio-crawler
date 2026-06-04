from pathlib import Path
import pytest
from vc_crawler.crawlers.a16z.parser import parse_portfolio_page, PORTFOLIO_URL

FIXTURE = Path(__file__).parent / "fixtures" / "a16z_portfolio.html"


def test_returns_correct_count():
    companies = parse_portfolio_page(FIXTURE.read_text(encoding="utf-8"))
    assert len(companies) == 3


def test_extracts_names():
    companies = parse_portfolio_page(FIXTURE.read_text(encoding="utf-8"))
    names = {c["name"] for c in companies}
    assert names == {"Airbnb", "GitHub", "Databricks"}


def test_raises_on_missing_global():
    with pytest.raises(ValueError, match="a16z_portfolio_companies"):
        parse_portfolio_page("<html><body><p>nothing here</p></body></html>")


def test_returns_raw_dicts():
    companies = parse_portfolio_page(FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(companies[0], dict)
    assert "stages" in companies[0]


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://a16z.com/portfolio/"
