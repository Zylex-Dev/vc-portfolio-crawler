from pathlib import Path
import pytest

from vc_crawler.crawlers.new_schools.parser import (
    PORTFOLIO_URL,
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


# ── parse_detail_page ─────────────────────────────────────────────────────────

def test_detail_returns_dict():
    assert isinstance(parse_detail_page(DETAIL_FIXTURE), dict)

def test_detail_description():
    result = parse_detail_page(DETAIL_FIXTURE)
    assert result["description"] == (
        "Acme Edu designs engaging, hands-on learning projects for grades K-8, "
        "transforming the classroom into a space for connection and growth."
    )

def test_detail_skips_short_blocks():
    """'Our Vision' (9 chars) must not be the description."""
    result = parse_detail_page(DETAIL_FIXTURE)
    assert result["description"] != "Our Vision"

def test_detail_website():
    result = parse_detail_page(DETAIL_FIXTURE)
    assert result["website"] == "https://acmeedu.com"

def test_detail_no_description():
    html = "<html><body><div class='elementor-widget-text-editor'><p>Hi</p></div></body></html>"
    assert parse_detail_page(html)["description"] is None

def test_detail_no_website():
    html = "<html><body><p>Some text about the company and its work in education.</p></body></html>"
    assert parse_detail_page(html)["website"] is None

def test_detail_ignores_non_website_links():
    html = """<html><body>
    <div class="elementor-widget-text-editor">
      <p>Company description that is longer than fifty characters for sure.</p>
    </div>
    <a href="https://twitter.com/foo">Twitter</a>
    </body></html>"""
    assert parse_detail_page(html)["website"] is None

def test_detail_founded_year():
    result = parse_detail_page(DETAIL_FIXTURE)
    assert result["founded_year"] == 2015

def test_detail_founded_year_none_when_absent():
    html = "<html><body><p>No founded year here.</p></body></html>"
    assert parse_detail_page(html)["founded_year"] is None
