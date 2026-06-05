import pytest
from vc_crawler.crawlers.a16z_speedrun.normalizer import normalize
from vc_crawler.models import Company


def _cantor():
    return {
        "id": "aaaa-1111",
        "slug": "cantor",
        "name": "Cantor",
        "logo": "https://cdn.example.com/cantor.png",
        "cohort": "SR001",
        "preamble": "AI for real estate (short pitch)",
        "description": "Cantor builds AI tools for commercial real estate.",
        "industries": ["AI", "Real Estate / Prop Tech"],
        "founded_year": 2023,
        "website_url": "https://cantoreality.com",
        "founder_set": [
            {"first_name": "Alice", "last_name": "Smith",
             "slug": "alice-smith", "title": "CEO",
             "introduction": "", "linkedin_url": "", "profile_pic": None},
        ],
    }


def _orbit():
    return {
        "id": "bbbb-2222",
        "slug": "orbit",
        "name": "Orbit",
        "logo": None,
        "cohort": "SR001",
        "preamble": "",
        "description": "Community platform for developers.",
        "industries": ["Dev Tools & DevOps"],
        "founded_year": None,
        "website_url": "",
        "founder_set": [],
    }


def _bolt():
    return {
        "id": "dddd-4444",
        "slug": "bolt",
        "name": "Bolt",
        "logo": None,
        "cohort": "SR002",
        "preamble": "Fintech",
        "description": None,
        "industries": [],
        "founded_year": None,
        "website_url": None,
        "founder_set": [],
    }


def test_returns_company_instance():
    assert isinstance(normalize(_cantor(), 1), Company)


def test_fund_is_a16z_speedrun():
    assert normalize(_cantor(), 1).fund == "a16z-speedrun"


def test_id_assigned():
    assert normalize(_cantor(), 42).id == 42


def test_name():
    assert normalize(_cantor(), 1).name == "Cantor"


def test_slug_from_api():
    assert normalize(_cantor(), 1).slug == "cantor"


def test_fund_url():
    assert normalize(_cantor(), 1).fund_url == "https://speedrun.a16z.com/companies/cantor"


def test_sectors():
    c = normalize(_cantor(), 1)
    assert c.sectors == ["AI", "Real Estate / Prop Tech"]


def test_sectors_empty_list_when_no_industries():
    assert normalize(_bolt(), 1).sectors == []


def test_website():
    assert normalize(_cantor(), 1).website == "https://cantoreality.com"


def test_website_none_when_empty_string():
    assert normalize(_orbit(), 1).website is None


def test_website_none_when_null():
    assert normalize(_bolt(), 1).website is None


def test_description():
    assert normalize(_cantor(), 1).description == "Cantor builds AI tools for commercial real estate."


def test_description_none_when_null():
    assert normalize(_bolt(), 1).description is None


def test_stage_is_cohort():
    assert normalize(_cantor(), 1).stage == "SR001"


def test_stage_is_cohort_sr002():
    assert normalize(_bolt(), 1).stage == "SR002"


def test_stage_year_is_none():
    assert normalize(_cantor(), 1).stage_year is None


def test_founded_year():
    assert normalize(_cantor(), 1).founded_year == 2023


def test_founded_year_none():
    assert normalize(_orbit(), 1).founded_year is None


def test_invested_year_is_none():
    assert normalize(_cantor(), 1).invested_year is None


def test_logo_url():
    assert normalize(_cantor(), 1).logo_url == "https://cdn.example.com/cantor.png"


def test_logo_url_none():
    assert normalize(_orbit(), 1).logo_url is None


def test_ticker_symbol_none():
    assert normalize(_cantor(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_cantor(), 1).acquirer is None


def test_founders_joined():
    assert normalize(_cantor(), 1).founders == ["Alice Smith"]


def test_founders_multiple():
    raw = _cantor()
    raw["founder_set"] = [
        {"first_name": "Bob", "last_name": "Jones", "slug": "", "title": "", "introduction": "", "linkedin_url": "", "profile_pic": None},
        {"first_name": "Carol", "last_name": "Lee", "slug": "", "title": "", "introduction": "", "linkedin_url": "", "profile_pic": None},
    ]
    assert normalize(raw, 1).founders == ["Bob Jones", "Carol Lee"]


def test_founders_empty_becomes_none():
    assert normalize(_orbit(), 1).founders is None
