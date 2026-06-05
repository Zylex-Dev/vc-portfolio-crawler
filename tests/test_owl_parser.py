from pathlib import Path
import pytest
from vc_crawler.crawlers.owl_ventures.parser import (
    PORTFOLIO_URL,
    parse_portfolio_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "owl_ventures_portfolio.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://www.owlvc.com/portfolio"


def test_returns_list_of_dicts():
    result = parse_portfolio_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_four_companies():
    assert len(parse_portfolio_page(FIXTURE)) == 4


def test_empty_page_returns_empty_list():
    assert parse_portfolio_page("<html><body></body></html>") == []


def test_active_company_name():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["name"] == "Amira Learning"


def test_acquired_company_name():
    result = parse_portfolio_page(FIXTURE)
    assert result[1]["name"] == "Abl"


def test_active_company_not_acquired():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["is_acquired"] is False


def test_acquired_company_flag():
    result = parse_portfolio_page(FIXTURE)
    assert result[1]["is_acquired"] is True


def test_acquirer_set_for_acquired():
    result = parse_portfolio_page(FIXTURE)
    assert result[1]["acquirer"] == "BetterLesson"


def test_acquirer_none_for_active():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["acquirer"] is None


def test_logo_url():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["logo_url"] == "https://cdn.example.com/amira.svg"


def test_description():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["description"] == "Amira listens to young students read aloud and provides real-time tutoring."


def test_website():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["website"] == "https://amiralearning.com/"


def test_website_not_press_release():
    result = parse_portfolio_page(FIXTURE)
    assert "news" not in (result[0]["website"] or "")


def test_fund_path():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["fund_path"] == "/portfolio/amira"


def test_fund_path_abl():
    result = parse_portfolio_page(FIXTURE)
    assert result[1]["fund_path"] == "/portfolio/abl"


def test_single_sector():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["sectors"] == ["Pre K-12"]


def test_multiple_sectors():
    result = parse_portfolio_page(FIXTURE)
    assert result[2]["sectors"] == ["Pre K-12", "Post-Secondary"]


def test_different_sector():
    result = parse_portfolio_page(FIXTURE)
    assert result[3]["sectors"] == ["Future of Work"]


def test_initial_investment_string():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["initial_investment"] == "Led Series A in 2019"


def test_initial_investment_none_when_hidden():
    result = parse_portfolio_page(FIXTURE)
    assert result[2]["initial_investment"] is None
    assert result[3]["initial_investment"] is None


def test_founded_year_string():
    result = parse_portfolio_page(FIXTURE)
    assert result[0]["founded_year_str"] == "2017"


def test_founders_collected():
    result = parse_portfolio_page(FIXTURE)
    assert "Pete Jungwirth" in result[0]["founders"]


def test_founders_empty_when_all_hidden():
    result = parse_portfolio_page(FIXTURE)
    assert result[3]["founders"] == []
