from vc_crawler.crawlers.owl_ventures.normalizer import normalize
from vc_crawler.models import Company


def _amira():
    return {
        "name": "Amira Learning",
        "logo_url": "https://cdn.example.com/amira.svg",
        "is_acquired": False,
        "acquirer": None,
        "description": "Amira listens to young students read aloud.",
        "website": "https://amiralearning.com/",
        "initial_investment": "Led Series A in 2019",
        "founded_year_str": "2017",
        "founders": ["Pete Jungwirth"],
        "sectors": ["Pre K-12"],
        "fund_path": "/portfolio/amira",
    }


def _abl():
    return {
        "name": "Abl",
        "logo_url": "https://cdn.example.com/abl.svg",
        "is_acquired": True,
        "acquirer": "BetterLesson",
        "description": "Abl offers a cloud-based platform for school scheduling.",
        "website": "https://www.ablschools.com/",
        "initial_investment": "Led Series A in 2016",
        "founded_year_str": "2015",
        "founders": ["Adam Pisoni"],
        "sectors": ["Pre K-12"],
        "fund_path": "/portfolio/abl",
    }


def _apna():
    return {
        "name": "Apna",
        "logo_url": "https://cdn.example.com/apna.svg",
        "is_acquired": False,
        "acquirer": None,
        "description": "India's largest professional networking platform.",
        "website": "https://apna.co/",
        "initial_investment": None,
        "founded_year_str": "2019",
        "founders": [],
        "sectors": ["Future of Work"],
        "fund_path": "/portfolio/apna",
    }


def test_returns_company_instance():
    assert isinstance(normalize(_amira(), 1), Company)


def test_fund_is_owl_ventures():
    assert normalize(_amira(), 1).fund == "owl-ventures"


def test_id_assigned():
    assert normalize(_amira(), 42).id == 42


def test_name():
    assert normalize(_amira(), 1).name == "Amira Learning"


def test_slug_from_path():
    assert normalize(_amira(), 1).slug == "amira"


def test_slug_abl():
    assert normalize(_abl(), 1).slug == "abl"


def test_fund_url():
    assert normalize(_amira(), 1).fund_url == "https://www.owlvc.com/portfolio/amira"


def test_sectors_single():
    assert normalize(_amira(), 1).sectors == ["Pre K-12"]


def test_sectors_future_of_work():
    assert normalize(_apna(), 1).sectors == ["Future of Work"]


def test_website():
    assert normalize(_amira(), 1).website == "https://amiralearning.com/"


def test_website_none_when_missing():
    raw = _amira()
    raw["website"] = None
    assert normalize(raw, 1).website is None


def test_description():
    assert normalize(_amira(), 1).description == "Amira listens to young students read aloud."


def test_stage_none_when_active():
    assert normalize(_amira(), 1).stage is None


def test_stage_acquired_when_acquired():
    assert normalize(_abl(), 1).stage == "Acquired"


def test_acquirer_set():
    assert normalize(_abl(), 1).acquirer == "BetterLesson"


def test_acquirer_none_when_active():
    assert normalize(_amira(), 1).acquirer is None


def test_founded_year():
    assert normalize(_amira(), 1).founded_year == 2017


def test_founded_year_abl():
    assert normalize(_abl(), 1).founded_year == 2015


def test_founded_year_none_when_missing():
    raw = _amira()
    raw["founded_year_str"] = None
    assert normalize(raw, 1).founded_year is None


def test_invested_year_from_investment_string():
    assert normalize(_amira(), 1).invested_year == 2019


def test_invested_year_abl():
    assert normalize(_abl(), 1).invested_year == 2016


def test_invested_year_from_plain_year_string():
    raw = _amira()
    raw["initial_investment"] = "2025"
    assert normalize(raw, 1).invested_year == 2025


def test_invested_year_none_when_no_investment():
    assert normalize(_apna(), 1).invested_year is None


def test_logo_url():
    assert normalize(_amira(), 1).logo_url == "https://cdn.example.com/amira.svg"


def test_logo_url_none_when_missing():
    raw = _amira()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


def test_founders():
    assert normalize(_amira(), 1).founders == ["Pete Jungwirth"]


def test_founders_none_when_empty():
    assert normalize(_apna(), 1).founders is None


def test_founders_multiple():
    raw = _amira()
    raw["founders"] = ["Alice Smith", "Bob Jones"]
    assert normalize(raw, 1).founders == ["Alice Smith", "Bob Jones"]


def test_stage_year_none():
    assert normalize(_amira(), 1).stage_year is None


def test_ticker_symbol_none():
    assert normalize(_amira(), 1).ticker_symbol is None


def test_source_modified_none():
    assert normalize(_amira(), 1).source_modified is None
