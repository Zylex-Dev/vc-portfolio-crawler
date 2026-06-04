import pytest
from vc_crawler.crawlers.a16z.normalizer import normalize
from vc_crawler.models import Company


def _airbnb():
    return {"name":"Airbnb","web":"https://www.airbnb.com","stages":["IPO"],"status":"Exits","verticals":"Consumer","focus_areas":["Marketplace","Travel"],"initial_a16z_date_funded":"2011-07-25T00:00:00","year_founded":"2008","overview":"Airbnb creates a world.","logo":"https://a16z.com/airbnb.svg","ticker_symbol":"ABNB","acquirer":None,"founders_list":["Brian Chesky","Joe Gebbia"],"exit_date":"2020-12-10T00:00:00","announcement":{"permalink":"https://a16z.com/portfolio/airbnb/","excerpt":""}}

def _github():
    return {"name":"GitHub","web":None,"url":None,"external_url":"https://github.com","stages":["M&A"],"status":"Exits","verticals":"Enterprise","focus_areas":["Developer Tools"],"initial_a16z_date_funded":"2012-07-09T00:00:00","year_founded":"2008","overview":"Code hosting.","logo":"https://a16z.com/github.svg","ticker_symbol":None,"acquirer":"Microsoft","founders_list":[],"exit_date":"2018-10-26T00:00:00","announcement":{"permalink":"https://a16z.com/portfolio/github/","excerpt":""}}

def _databricks():
    return {"name":"Databricks","web":"https://www.databricks.com","stages":["Growth","Venture"],"status":"Active","verticals":"Enterprise","focus_areas":["Data","AI"],"initial_a16z_date_funded":"2019-02-01T00:00:00","year_founded":"2013","overview":"Data and AI.","logo":None,"ticker_symbol":None,"acquirer":None,"founders_list":["Ali Ghodsi"],"exit_date":None,"announcement":{"permalink":"https://a16z.com/portfolio/databricks/","excerpt":""}}


def test_returns_company_instance():
    assert isinstance(normalize(_airbnb(), 1), Company)

def test_fund_is_a16z():
    assert normalize(_airbnb(), 1).fund == "a16z"

def test_id_assigned():
    assert normalize(_airbnb(), 42).id == 42

def test_name():
    assert normalize(_airbnb(), 1).name == "Airbnb"

def test_slug_lowercased():
    assert normalize(_airbnb(), 1).slug == "airbnb"

def test_website_from_web():
    assert normalize(_airbnb(), 1).website == "https://www.airbnb.com"

def test_website_falls_back_to_external_url():
    assert normalize(_github(), 1).website == "https://github.com"

def test_fund_url_from_announcement():
    assert normalize(_airbnb(), 1).fund_url == "https://a16z.com/portfolio/airbnb/"

def test_fund_url_fallback_when_no_announcement():
    raw = _airbnb()
    raw["announcement"] = None
    assert normalize(raw, 1).fund_url == "https://a16z.com/portfolio/"

def test_sectors_from_focus_areas():
    c = normalize(_airbnb(), 1)
    assert "Marketplace" in c.sectors
    assert "Travel" in c.sectors

def test_description_from_overview():
    assert normalize(_airbnb(), 1).description == "Airbnb creates a world."

def test_stage_single():
    assert normalize(_airbnb(), 1).stage == "IPO"

def test_stage_picks_most_advanced_from_multiple():
    assert normalize(_databricks(), 1).stage == "Growth"

def test_founded_year():
    assert normalize(_airbnb(), 1).founded_year == 2008

def test_invested_year():
    assert normalize(_airbnb(), 1).invested_year == 2011

def test_logo_url():
    assert normalize(_airbnb(), 1).logo_url == "https://a16z.com/airbnb.svg"

def test_logo_url_none():
    assert normalize(_databricks(), 1).logo_url is None

def test_ticker_symbol():
    assert normalize(_airbnb(), 1).ticker_symbol == "ABNB"

def test_ticker_symbol_none():
    assert normalize(_github(), 1).ticker_symbol is None

def test_acquirer():
    assert normalize(_github(), 1).acquirer == "Microsoft"

def test_acquirer_none():
    assert normalize(_airbnb(), 1).acquirer is None

def test_founders_list():
    assert normalize(_airbnb(), 1).founders == ["Brian Chesky", "Joe Gebbia"]

def test_founders_empty_becomes_none():
    assert normalize(_github(), 1).founders is None

def test_stage_year_for_exits():
    assert normalize(_airbnb(), 1).stage_year == 2020

def test_stage_year_none_for_active():
    assert normalize(_databricks(), 1).stage_year is None
