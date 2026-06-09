from pathlib import Path
from vc_crawler.crawlers.edu_capital.parser import (
    PORTFOLIO_URL,
    parse_portfolio_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "educapital_portfolio.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://www.educapitalvc.com/portfolio"


def test_returns_list_of_dicts():
    result = parse_portfolio_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_four_companies():
    assert len(parse_portfolio_page(FIXTURE)) == 4


def test_empty_page_returns_empty_list():
    assert parse_portfolio_page("<html><body></body></html>") == []


# --- Card 1: 360learning ---

def test_card1_logo_url():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["logo_url"] == "https://cdn.prod.website-files.com/abc123_360_logo.png"


def test_card1_description():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["description"] == "Collaborative LMS"


def test_card1_category():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["category"] == "Future of work"


def test_card1_website():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["website"] == "https://360learning.com"


def test_card1_not_acquired():
    r = parse_portfolio_page(FIXTURE)[0]
    assert r["acquired"] is False


# --- Card 2: appscho (acquired) ---

def test_card2_acquired_true():
    r = parse_portfolio_page(FIXTURE)[1]
    assert r["acquired"] is True


def test_card2_website():
    r = parse_portfolio_page(FIXTURE)[1]
    assert r["website"] == "https://www.appscho.com/"


def test_card2_category():
    r = parse_portfolio_page(FIXTURE)[1]
    assert r["category"] == "Future of education"


# --- Card 3: buddy.ai ---

def test_card3_not_acquired():
    r = parse_portfolio_page(FIXTURE)[2]
    assert r["acquired"] is False


def test_card3_website():
    r = parse_portfolio_page(FIXTURE)[2]
    assert r["website"] == "https://buddy.ai/fr/"


# --- Card 4: Apple Store URL ---

def test_card4_website_apple():
    r = parse_portfolio_page(FIXTURE)[3]
    assert r["website"] == "https://apps.apple.com/fr/app/emma-parler-anglais/id6737470910"


def test_card4_not_acquired():
    r = parse_portfolio_page(FIXTURE)[3]
    assert r["acquired"] is False
