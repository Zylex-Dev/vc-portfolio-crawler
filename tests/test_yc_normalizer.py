from vc_crawler.crawlers.y_combinator.normalizer import normalize
from vc_crawler.models import Company


def _codecademy():
    return {
        "id": 86,
        "name": "Codecademy",
        "slug": "codecademy",
        "small_logo_thumb_url": "https://example.com/logo.png",
        "website": "http://codecademy.com",
        "long_description": "Codecademy is the leading online learning platform.",
        "one_liner": "The leading online learning platform.",
        "batch": "Summer 2011",
        "status": "Acquired",
        "stage": "Growth",
        "industries": ["Education"],
    }


def _outschool():
    return {
        "id": 999,
        "name": "Outschool",
        "slug": "outschool",
        "small_logo_thumb_url": "https://example.com/outschool.png",
        "website": "https://outschool.com",
        "long_description": None,
        "one_liner": "A live online learning platform for kids.",
        "batch": "Winter 2016",
        "status": "Active",
        "stage": "Growth",
        "industries": ["Education"],
    }


def _dropschool():
    return {
        "id": 777,
        "name": "DropSchool",
        "slug": "dropschool",
        "small_logo_thumb_url": None,
        "website": None,
        "long_description": None,
        "one_liner": None,
        "batch": "Summer 2020",
        "status": "Inactive",
        "stage": None,
        "industries": [],
    }


def test_returns_company_instance():
    assert isinstance(normalize(_codecademy(), 1), Company)


def test_fund_is_y_combinator():
    assert normalize(_codecademy(), 1).fund == "y-combinator"


def test_id_assigned():
    assert normalize(_codecademy(), 42).id == 42


def test_name():
    assert normalize(_codecademy(), 1).name == "Codecademy"


def test_slug():
    assert normalize(_codecademy(), 1).slug == "codecademy"


def test_fund_url():
    assert normalize(_codecademy(), 1).fund_url == "https://www.ycombinator.com/companies/codecademy"


def test_sectors():
    assert normalize(_codecademy(), 1).sectors == ["Education"]


def test_sectors_empty_list():
    assert normalize(_dropschool(), 1).sectors == []


def test_website():
    assert normalize(_codecademy(), 1).website == "http://codecademy.com"


def test_website_none_when_null():
    assert normalize(_dropschool(), 1).website is None


def test_description_uses_long_description():
    assert normalize(_codecademy(), 1).description == "Codecademy is the leading online learning platform."


def test_description_falls_back_to_one_liner():
    assert normalize(_outschool(), 1).description == "A live online learning platform for kids."


def test_description_none_when_both_missing():
    assert normalize(_dropschool(), 1).description is None


def test_stage_acquired():
    assert normalize(_codecademy(), 1).stage == "Acquired"


def test_stage_inactive():
    assert normalize(_dropschool(), 1).stage == "Inactive"


def test_stage_active_uses_stage_field():
    assert normalize(_outschool(), 1).stage == "Growth"


def test_stage_active_none_when_stage_field_none():
    raw = _outschool()
    raw["stage"] = None
    assert normalize(raw, 1).stage is None


def test_stage_unknown_status_uses_stage_field():
    raw = _outschool()
    raw["status"] = "Public"
    raw["stage"] = "Growth"
    assert normalize(raw, 1).stage == "Growth"


def test_stage_year_none():
    assert normalize(_codecademy(), 1).stage_year is None


def test_founded_year_none():
    assert normalize(_codecademy(), 1).founded_year is None


def test_invested_year_from_batch():
    assert normalize(_codecademy(), 1).invested_year == 2011


def test_invested_year_winter_batch():
    assert normalize(_outschool(), 1).invested_year == 2016


def test_invested_year_summer_2020():
    assert normalize(_dropschool(), 1).invested_year == 2020


def test_invested_year_none_when_batch_null():
    raw = _dropschool()
    raw["batch"] = None
    assert normalize(raw, 1).invested_year is None


def test_logo_url():
    assert normalize(_codecademy(), 1).logo_url == "https://example.com/logo.png"


def test_logo_url_none():
    assert normalize(_dropschool(), 1).logo_url is None


def test_ticker_symbol_none():
    assert normalize(_codecademy(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_codecademy(), 1).acquirer is None


def test_founders_none():
    assert normalize(_codecademy(), 1).founders is None


def test_source_modified_none():
    assert normalize(_codecademy(), 1).source_modified is None
