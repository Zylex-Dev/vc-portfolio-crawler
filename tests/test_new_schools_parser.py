from pathlib import Path
import pytest

from vc_crawler.crawlers.new_schools.parser import (
    PORTFOLIO_URL,
    INV_YEAR_API,
    INIT_YEAR_API,
    parse_term_map,
    parse_listing_page,
    parse_detail_page,
)

LISTING_FIXTURE = (Path(__file__).parent / "fixtures" / "newschools_listing.html").read_text(encoding="utf-8")
DETAIL_FIXTURE  = (Path(__file__).parent / "fixtures" / "newschools_detail.html").read_text(encoding="utf-8")


# ── constants ────────────────────────────────────────────────────────────────

def test_portfolio_url():
    assert PORTFOLIO_URL == "https://www.newschools.org/ventures/"

def test_inv_year_api():
    assert "investment-year" in INV_YEAR_API
    assert "wp-json/wp/v2" in INV_YEAR_API

def test_init_year_api():
    assert "initial-investment-year" in INIT_YEAR_API
    assert "wp-json/wp/v2" in INIT_YEAR_API


# ── parse_term_map ────────────────────────────────────────────────────────────

def test_term_map_basic():
    json_text = '[{"id": 709, "name": "2024"}, {"id": 574, "name": "2023"}]'
    result = parse_term_map(json_text)
    assert result == {709: 2024, 574: 2023}

def test_term_map_returns_int_keys_and_values():
    json_text = '[{"id": 711, "name": "2022"}]'
    m = parse_term_map(json_text)
    key, val = list(m.items())[0]
    assert isinstance(key, int)
    assert isinstance(val, int)

def test_term_map_empty_list():
    assert parse_term_map("[]") == {}


# ── parse_listing_page ────────────────────────────────────────────────────────

def test_listing_returns_tuple():
    result = parse_listing_page(LISTING_FIXTURE)
    assert isinstance(result, tuple) and len(result) == 2

def test_listing_returns_two_records():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert len(records) == 2

def test_listing_max_page():
    _, max_page = parse_listing_page(LISTING_FIXTURE)
    assert max_page == 1

def test_listing_max_page_default_when_no_anchor():
    _, max_page = parse_listing_page("<html><body></body></html>")
    assert max_page == 1

def test_listing_empty_page():
    records, _ = parse_listing_page("<html><body></body></html>")
    assert records == []

def test_listing_card1_name():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["name"] == "Acme Edu"

def test_listing_card1_fund_url():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["fund_url"] == "https://www.newschools.org/venture/acme-edu/"

def test_listing_card1_slug():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["slug"] == "acme-edu"

def test_listing_card1_logo_url():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["logo_url"] == "https://www.newschools.org/wp-content/uploads/acme-logo.png"

def test_listing_card1_sectors():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["sectors"] == ["Learning Solutions"]

def test_listing_card1_init_year_ids():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["init_year_ids"] == [714]

def test_listing_card1_inv_year_ids():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["inv_year_ids"] == [709]

def test_listing_card1_is_past_true():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[0]["is_past"] is True

def test_listing_card2_name():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["name"] == "Beta Learn"

def test_listing_card2_slug():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["slug"] == "beta-learn"

def test_listing_card2_logo_url_none():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["logo_url"] is None

def test_listing_card2_sectors():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["sectors"] == ["Diverse Leaders"]

def test_listing_card2_init_year_ids():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["init_year_ids"] == [720]

def test_listing_card2_is_past_false():
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert records[1]["is_past"] is False

def test_listing_init_ids_do_not_bleed_into_inv_ids():
    """initial-investment-year-714 must NOT appear in inv_year_ids."""
    records, _ = parse_listing_page(LISTING_FIXTURE)
    assert 714 not in records[0]["inv_year_ids"]
