from vc_crawler.crawlers.gsv_ventures.normalizer import normalize, PORTFOLIO_URL
from vc_crawler.models import Company


def _edulearnpro():
    return {
        "name": "EduLearn Pro",
        "tagline": "Transforming how students learn online",
        "description": "EduLearn Pro is an online learning platform for K-12 students.",
        "website": "https://edulearnpro.com/",
        "logo_url": "https://gsv.ventures/wp-content/uploads/logo-edulearnpro.png",
        "founders": ["Alice Smith", "Bob Jones"],
        "investment": "Series A, 2021",
        "founded_year_str": "2018",
        "sector": "Pre-K-12",
    }


def _skillup():
    return {
        "name": "SkillUp",
        "tagline": "Building tomorrow's workforce today",
        "description": None,
        "website": "https://skillup.io/",
        "logo_url": "https://gsv.ventures/wp-content/uploads/logo-skillup.png",
        "founders": [],
        "investment": None,
        "founded_year_str": None,
        "sector": None,
    }


def _learnpath():
    return {
        "name": "LearnPath",
        "tagline": "Personalized learning journeys for everyone",
        "description": None,
        "website": "https://learnpath.com/",
        "logo_url": "https://gsv.ventures/wp-content/uploads/logo-learnpath.png",
        "founders": ["Carol Davis", "Dan Evans", "Eve Foster"],
        "investment": "Seed, 2020",
        "founded_year_str": "2019",
        "sector": "Post-Secondary",
    }


def test_returns_company_instance():
    assert isinstance(normalize(_edulearnpro(), 1), Company)


def test_fund_is_gsv_ventures():
    assert normalize(_edulearnpro(), 1).fund == "gsv-ventures"


def test_id_assigned():
    assert normalize(_edulearnpro(), 42).id == 42


def test_name():
    assert normalize(_edulearnpro(), 1).name == "EduLearn Pro"


def test_slug():
    assert normalize(_edulearnpro(), 1).slug == "edulearn-pro"


def test_slug_simple():
    assert normalize(_skillup(), 1).slug == "skillup"


def test_fund_url_constant():
    assert normalize(_edulearnpro(), 1).fund_url == PORTFOLIO_URL


def test_fund_url_value():
    assert normalize(_edulearnpro(), 1).fund_url == "https://gsv.ventures/portfolio/"


def test_sectors_from_segment():
    assert normalize(_edulearnpro(), 1).sectors == ["Pre-K-12"]


def test_sectors_empty_when_no_segment():
    assert normalize(_skillup(), 1).sectors == []


def test_sectors_post_secondary():
    assert normalize(_learnpath(), 1).sectors == ["Post-Secondary"]


def test_website():
    assert normalize(_edulearnpro(), 1).website == "https://edulearnpro.com/"


def test_website_none_when_missing():
    raw = _edulearnpro()
    raw["website"] = None
    assert normalize(raw, 1).website is None


def test_description_uses_paragraph():
    assert normalize(_edulearnpro(), 1).description == "EduLearn Pro is an online learning platform for K-12 students."


def test_description_falls_back_to_tagline():
    assert normalize(_skillup(), 1).description == "Building tomorrow's workforce today"


def test_description_tagline_when_no_paragraph():
    assert normalize(_learnpath(), 1).description == "Personalized learning journeys for everyone"


def test_stage_series_a():
    assert normalize(_edulearnpro(), 1).stage == "Series A"


def test_stage_seed():
    assert normalize(_learnpath(), 1).stage == "Seed"


def test_stage_none_when_no_investment():
    assert normalize(_skillup(), 1).stage is None


def test_invested_year_from_investment():
    assert normalize(_edulearnpro(), 1).invested_year == 2021


def test_invested_year_seed():
    assert normalize(_learnpath(), 1).invested_year == 2020


def test_invested_year_none_when_no_investment():
    assert normalize(_skillup(), 1).invested_year is None


def test_founded_year():
    assert normalize(_edulearnpro(), 1).founded_year == 2018


def test_founded_year_none_when_missing():
    assert normalize(_skillup(), 1).founded_year is None


def test_logo_url():
    assert normalize(_edulearnpro(), 1).logo_url == "https://gsv.ventures/wp-content/uploads/logo-edulearnpro.png"


def test_logo_url_none_when_missing():
    raw = _edulearnpro()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


def test_founders():
    assert normalize(_edulearnpro(), 1).founders == ["Alice Smith", "Bob Jones"]


def test_founders_multiple():
    assert normalize(_learnpath(), 1).founders == ["Carol Davis", "Dan Evans", "Eve Foster"]


def test_founders_none_when_empty():
    assert normalize(_skillup(), 1).founders is None


def test_stage_year_none():
    assert normalize(_edulearnpro(), 1).stage_year is None


def test_ticker_symbol_none():
    assert normalize(_edulearnpro(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_edulearnpro(), 1).acquirer is None


def test_source_modified_none():
    assert normalize(_edulearnpro(), 1).source_modified is None
