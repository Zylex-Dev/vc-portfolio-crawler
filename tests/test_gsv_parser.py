from pathlib import Path
from vc_crawler.crawlers.gsv_ventures.parser import (
    PORTFOLIO_URL,
    parse_portfolio_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "gsv_ventures_portfolio.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://gsv.ventures/portfolio/"


def test_returns_list_of_dicts():
    result = parse_portfolio_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_three_companies():
    assert len(parse_portfolio_page(FIXTURE)) == 3


def test_empty_page_returns_empty_list():
    assert parse_portfolio_page("<html><body></body></html>") == []


# --- Card A: EduLearn Pro (index 0) ---

def test_card_a_name():
    assert parse_portfolio_page(FIXTURE)[0]["name"] == "EduLearn Pro"


def test_card_a_tagline():
    assert parse_portfolio_page(FIXTURE)[0]["tagline"] == "Transforming how students learn online"


def test_card_a_description():
    assert parse_portfolio_page(FIXTURE)[0]["description"] == "EduLearn Pro is an online learning platform for K-12 students."


def test_card_a_website():
    assert parse_portfolio_page(FIXTURE)[0]["website"] == "https://edulearnpro.com/"


def test_card_a_logo_url():
    assert parse_portfolio_page(FIXTURE)[0]["logo_url"] == "https://gsv.ventures/wp-content/uploads/logo-edulearnpro.png"


def test_card_a_founders():
    assert parse_portfolio_page(FIXTURE)[0]["founders"] == ["Alice Smith", "Bob Jones"]


def test_card_a_investment():
    assert parse_portfolio_page(FIXTURE)[0]["investment"] == "Series A, 2021"


def test_card_a_founded_year_str():
    assert parse_portfolio_page(FIXTURE)[0]["founded_year_str"] == "2018"


def test_card_a_sector():
    assert parse_portfolio_page(FIXTURE)[0]["sector"] == "Pre-K-12"


# --- Card B: SkillUp (index 1) — minimal, no aside ---

def test_card_b_name():
    assert parse_portfolio_page(FIXTURE)[1]["name"] == "SkillUp"


def test_card_b_website():
    assert parse_portfolio_page(FIXTURE)[1]["website"] == "https://skillup.io/"


def test_card_b_description_none():
    assert parse_portfolio_page(FIXTURE)[1]["description"] is None


def test_card_b_founders_empty():
    assert parse_portfolio_page(FIXTURE)[1]["founders"] == []


def test_card_b_investment_none():
    assert parse_portfolio_page(FIXTURE)[1]["investment"] is None


def test_card_b_founded_year_str_none():
    assert parse_portfolio_page(FIXTURE)[1]["founded_year_str"] is None


def test_card_b_sector_none():
    assert parse_portfolio_page(FIXTURE)[1]["sector"] is None


# --- Card C: LearnPath (index 2) — 3 founders, no description p ---

def test_card_c_name():
    assert parse_portfolio_page(FIXTURE)[2]["name"] == "LearnPath"


def test_card_c_founders_multiple():
    assert parse_portfolio_page(FIXTURE)[2]["founders"] == ["Carol Davis", "Dan Evans", "Eve Foster"]


def test_card_c_description_none():
    assert parse_portfolio_page(FIXTURE)[2]["description"] is None


def test_card_c_investment():
    assert parse_portfolio_page(FIXTURE)[2]["investment"] == "Seed, 2020"


def test_card_c_sector():
    assert parse_portfolio_page(FIXTURE)[2]["sector"] == "Post-Secondary"
