from pathlib import Path
from vc_crawler.crawlers.brighteye.parser import (
    PORTFOLIO_URL,
    parse_portfolio_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "brighteye_portfolio.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://www.brighteyevc.com/portfolio"


def test_returns_list_of_dicts():
    result = parse_portfolio_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_four_companies():
    assert len(parse_portfolio_page(FIXTURE)) == 4


def test_empty_page_returns_empty_list():
    assert parse_portfolio_page("<html><body></body></html>") == []


# --- Card 1: zen-educate (matched to featured) ---

def test_card1_slug():
    assert parse_portfolio_page(FIXTURE)[0]["slug"] == "zen-educate"


def test_card1_location():
    assert parse_portfolio_page(FIXTURE)[0]["location"] == "UK"


def test_card1_logo_url():
    assert parse_portfolio_page(FIXTURE)[0]["logo_url"] == "https://cdn.prod.website-files.com/zen_logo.avif"


def test_card1_website():
    assert parse_portfolio_page(FIXTURE)[0]["website"] == "https://www.zeneducate.com/"


def test_card1_is_exited_false():
    assert parse_portfolio_page(FIXTURE)[0]["is_exited"] is False


def test_card1_name_from_featured():
    assert parse_portfolio_page(FIXTURE)[0]["name"] == "Zen Educate"


def test_card1_description_from_featured():
    assert parse_portfolio_page(FIXTURE)[0]["description"] == "Leading UK/US supply teacher marketplace."


def test_card1_categories_from_featured():
    assert parse_portfolio_page(FIXTURE)[0]["categories"] == ["Work"]


# --- Card 2: uphill (plain, not in featured) ---

def test_card2_slug():
    assert parse_portfolio_page(FIXTURE)[1]["slug"] == "uphill"


def test_card2_location():
    assert parse_portfolio_page(FIXTURE)[1]["location"] == "Portugal"


def test_card2_website():
    assert parse_portfolio_page(FIXTURE)[1]["website"] == "https://uphillhealth.com/"


def test_card2_is_exited_false():
    assert parse_portfolio_page(FIXTURE)[1]["is_exited"] is False


def test_card2_name_none():
    assert parse_portfolio_page(FIXTURE)[1]["name"] is None


def test_card2_description_none():
    assert parse_portfolio_page(FIXTURE)[1]["description"] is None


def test_card2_categories_empty():
    assert parse_portfolio_page(FIXTURE)[1]["categories"] == []


# --- Card 3: hack-the-box-copy (slug with -copy, no website) ---

def test_card3_slug():
    assert parse_portfolio_page(FIXTURE)[2]["slug"] == "hack-the-box-copy"


def test_card3_website_none():
    assert parse_portfolio_page(FIXTURE)[2]["website"] is None


def test_card3_location():
    assert parse_portfolio_page(FIXTURE)[2]["location"] == "Greece / UK"


# --- Card 4: gosu (exited) ---

def test_card4_slug():
    assert parse_portfolio_page(FIXTURE)[3]["slug"] == "gosu"


def test_card4_is_exited_true():
    assert parse_portfolio_page(FIXTURE)[3]["is_exited"] is True


def test_card4_website_none():
    assert parse_portfolio_page(FIXTURE)[3]["website"] is None
