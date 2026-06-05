from pathlib import Path
import pytest
from vc_crawler.crawlers.reach_capital.parser import (
    PORTFOLIO_URL,
    parse_cards,
)

PORTFOLIO_FIXTURE = (
    Path(__file__).parent / "fixtures" / "reach_capital_portfolio.html"
).read_text(encoding="utf-8")

AJAX_FIXTURE = (
    Path(__file__).parent / "fixtures" / "reach_capital_ajax.html"
).read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://www.reachcapital.com/companies/?sector=learning"


def test_returns_list_of_dicts():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_three_companies_from_portfolio():
    assert len(parse_cards(PORTFOLIO_FIXTURE)) == 3


def test_returns_two_companies_from_ajax():
    assert len(parse_cards(AJAX_FIXTURE)) == 2


def test_empty_html_returns_empty_list():
    assert parse_cards("<html><body></body></html>") == []


def test_company_name():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["name"] == "BookNook"


def test_second_company_name():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["name"] == "Abl"


def test_active_company_not_exited():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["is_exited"] is False


def test_exited_company_flag():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["is_exited"] is True


def test_ajax_exited_company():
    result = parse_cards(AJAX_FIXTURE)
    assert result[1]["is_exited"] is True


def test_description():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["description"] == "Literacy platform connecting students with certified tutors."


def test_description_second_company():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["description"] == "Master scheduling tools and guidance for schools."


def test_founded_year_str():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["founded_year_str"] == "2016"


def test_founded_year_str_second():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["founded_year_str"] == "2015"


def test_founded_year_str_ajax():
    result = parse_cards(AJAX_FIXTURE)
    assert result[0]["founded_year_str"] == "2011"


def test_founders_list():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["founders"] == ["Dana Brown", "Michael Lombardo"]


def test_founders_multiple():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["founders"] == ["Adam Pisoni", "Amy Filsinger", "Chris Walsh"]


def test_founders_empty_when_no_leadership_section():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[2]["founders"] == []


def test_website():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["website"] == "https://booknook.com/"


def test_website_second():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["website"] == "https://ablschools.com/"


def test_logo_url():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[0]["logo_url"] == "https://www.reachcapital.com/wp-content/uploads/BookNook.png"


def test_logo_url_second():
    result = parse_cards(PORTFOLIO_FIXTURE)
    assert result[1]["logo_url"] == "https://www.reachcapital.com/wp-content/uploads/Abl.png"


def test_ajax_company_name():
    result = parse_cards(AJAX_FIXTURE)
    assert result[0]["name"] == "Desmos"


def test_ajax_website():
    result = parse_cards(AJAX_FIXTURE)
    assert result[0]["website"] == "https://www.desmos.com/"
