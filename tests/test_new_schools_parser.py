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
