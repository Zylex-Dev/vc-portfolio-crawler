from vc_crawler.crawlers.reach_capital.normalizer import normalize
from vc_crawler.models import Company


def _booknook():
    return {
        "name": "BookNook",
        "is_exited": False,
        "description": "Literacy platform connecting students with certified tutors.",
        "website": "https://booknook.com/",
        "logo_url": "https://www.reachcapital.com/wp-content/uploads/BookNook.png",
        "founded_year_str": "2016",
        "founders": ["Dana Brown", "Michael Lombardo"],
    }


def _abl():
    return {
        "name": "Abl",
        "is_exited": True,
        "description": "Master scheduling tools and guidance for schools.",
        "website": "https://ablschools.com/",
        "logo_url": "https://www.reachcapital.com/wp-content/uploads/Abl.png",
        "founded_year_str": "2015",
        "founders": ["Adam Pisoni", "Amy Filsinger", "Chris Walsh"],
    }


def _aprende():
    return {
        "name": "Aprende Institute",
        "is_exited": False,
        "description": "The leading online education platform for vocational skills training.",
        "website": "https://aprende.com/",
        "logo_url": "https://www.reachcapital.com/wp-content/uploads/Aprende.png",
        "founded_year_str": "2020",
        "founders": [],
    }


def test_returns_company_instance():
    assert isinstance(normalize(_booknook(), 1), Company)


def test_fund_is_reach_capital():
    assert normalize(_booknook(), 1).fund == "reach-capital"


def test_id_assigned():
    assert normalize(_booknook(), 42).id == 42


def test_name():
    assert normalize(_booknook(), 1).name == "BookNook"


def test_slug_single_word():
    assert normalize(_booknook(), 1).slug == "booknook"


def test_slug_two_words():
    assert normalize(_aprende(), 1).slug == "aprende-institute"


def test_fund_url():
    assert normalize(_booknook(), 1).fund_url == "https://www.reachcapital.com/companies/?sector=learning"


def test_sectors():
    assert normalize(_booknook(), 1).sectors == ["Learning"]


def test_website():
    assert normalize(_booknook(), 1).website == "https://booknook.com/"


def test_website_none_when_missing():
    raw = _booknook()
    raw["website"] = None
    assert normalize(raw, 1).website is None


def test_description():
    assert normalize(_booknook(), 1).description == "Literacy platform connecting students with certified tutors."


def test_description_none_when_missing():
    raw = _booknook()
    raw["description"] = None
    assert normalize(raw, 1).description is None


def test_stage_none_when_active():
    assert normalize(_booknook(), 1).stage is None


def test_stage_exit_when_exited():
    assert normalize(_abl(), 1).stage == "Exit"


def test_founded_year():
    assert normalize(_booknook(), 1).founded_year == 2016


def test_founded_year_abl():
    assert normalize(_abl(), 1).founded_year == 2015


def test_founded_year_none_when_missing():
    raw = _booknook()
    raw["founded_year_str"] = None
    assert normalize(raw, 1).founded_year is None


def test_founded_year_invalid_string_returns_none():
    raw = _booknook()
    raw["founded_year_str"] = "not-a-year"
    assert normalize(raw, 1).founded_year is None


def test_founders():
    assert normalize(_booknook(), 1).founders == ["Dana Brown", "Michael Lombardo"]


def test_founders_multiple():
    assert normalize(_abl(), 1).founders == ["Adam Pisoni", "Amy Filsinger", "Chris Walsh"]


def test_founders_none_when_empty_list():
    assert normalize(_aprende(), 1).founders is None


def test_logo_url():
    assert normalize(_booknook(), 1).logo_url == "https://www.reachcapital.com/wp-content/uploads/BookNook.png"


def test_logo_url_none_when_missing():
    raw = _booknook()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


def test_invested_year_none():
    assert normalize(_booknook(), 1).invested_year is None


def test_stage_year_none():
    assert normalize(_booknook(), 1).stage_year is None


def test_ticker_symbol_none():
    assert normalize(_booknook(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_booknook(), 1).acquirer is None


def test_source_modified_none():
    assert normalize(_booknook(), 1).source_modified is None
