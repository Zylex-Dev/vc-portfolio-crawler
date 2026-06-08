from pathlib import Path
from vc_crawler.crawlers.learn_capital.parser import (
    PORTFOLIO_URL,
    parse_ventures_page,
)

FIXTURE = (Path(__file__).parent / "fixtures" / "learn_capital_ventures.html").read_text(encoding="utf-8")


def test_portfolio_url_constant():
    assert PORTFOLIO_URL == "https://learn.vc/ventures"


def test_returns_list_of_dicts():
    result = parse_ventures_page(FIXTURE)
    assert isinstance(result, list)
    assert all(isinstance(r, dict) for r in result)


def test_returns_three_companies():
    assert len(parse_ventures_page(FIXTURE)) == 3


def test_empty_page_returns_empty_list():
    assert parse_ventures_page("<html><body></body></html>") == []


def test_missing_ventures_key_returns_empty_list():
    import json
    html = '<script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{}}}</script>'
    assert parse_ventures_page(html) == []


# --- Company A: Edify Academy (index 0) ---

def test_company_a_name():
    assert parse_ventures_page(FIXTURE)[0]["name"] == "Edify Academy"


def test_company_a_description():
    assert parse_ventures_page(FIXTURE)[0]["description"] == "An adaptive learning platform for K-12 students."


def test_company_a_headline():
    assert parse_ventures_page(FIXTURE)[0]["headline"] == "Personalizing education for every learner."


def test_company_a_website():
    assert parse_ventures_page(FIXTURE)[0]["website"] == "https://edify.academy"


def test_company_a_logo_url():
    assert parse_ventures_page(FIXTURE)[0]["logo_url"] == "https://images.prismic.io/learn-site/edify-logo.png"


def test_company_a_founders_text_empty():
    assert parse_ventures_page(FIXTURE)[0]["founders_text"] == ""


def test_company_a_tags():
    assert parse_ventures_page(FIXTURE)[0]["tags"] == ["education"]


def test_company_a_acquired_false():
    assert parse_ventures_page(FIXTURE)[0]["acquired"] is False


def test_company_a_public_false():
    assert parse_ventures_page(FIXTURE)[0]["public"] is False


# --- Company B: TalentBridge (index 1) — founders present, empty description ---

def test_company_b_name():
    assert parse_ventures_page(FIXTURE)[1]["name"] == "TalentBridge"


def test_company_b_description_empty():
    assert parse_ventures_page(FIXTURE)[1]["description"] is None


def test_company_b_headline():
    assert parse_ventures_page(FIXTURE)[1]["headline"] == "Bridging the global talent gap."


def test_company_b_founders_text():
    assert parse_ventures_page(FIXTURE)[1]["founders_text"] == "Alice Kim, Bob Chen"


def test_company_b_tags():
    assert parse_ventures_page(FIXTURE)[1]["tags"] == ["community"]


# --- Company C: LearnCo (index 2) — public: true ---

def test_company_c_name():
    assert parse_ventures_page(FIXTURE)[2]["name"] == "LearnCo"


def test_company_c_public_true():
    assert parse_ventures_page(FIXTURE)[2]["public"] is True


def test_company_c_acquired_false():
    assert parse_ventures_page(FIXTURE)[2]["acquired"] is False


def test_company_c_tags():
    assert parse_ventures_page(FIXTURE)[2]["tags"] == ["finance"]


def test_company_c_founders_text():
    assert parse_ventures_page(FIXTURE)[2]["founders_text"] == "Carlos Ruiz"


def test_website_none_when_link_type_not_web():
    import json
    html = (
        '<script id="__NEXT_DATA__" type="application/json">'
        + json.dumps({"props": {"pageProps": {"ventures": [{
            "id": "x", "tags": [], "data": {
                "name": [{"type": "heading1", "text": "X", "spans": []}],
                "visit": {"link_type": "Media", "url": "https://example.com"},
                "acquired": False, "public": False,
            }
        }]}}})
        + "</script>"
    )
    result = parse_ventures_page(html)
    assert result[0]["website"] is None
