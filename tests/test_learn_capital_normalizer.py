from vc_crawler.crawlers.learn_capital.normalizer import normalize, PORTFOLIO_URL
from vc_crawler.models import Company


def _edify() -> dict:
    return {
        "name": "Edify Academy",
        "description": "An adaptive learning platform for K-12 students.",
        "headline": "Personalizing education for every learner.",
        "website": "https://edify.academy",
        "logo_url": "https://images.prismic.io/learn-site/edify-logo.png",
        "founders_text": "",
        "tags": ["education"],
        "acquired": False,
        "public": False,
    }


def _talentbridge() -> dict:
    return {
        "name": "TalentBridge",
        "description": None,
        "headline": "Bridging the global talent gap.",
        "website": "https://talentbridge.io",
        "logo_url": "https://images.prismic.io/learn-site/tb-logo.png",
        "founders_text": "Alice Kim, Bob Chen",
        "tags": ["community"],
        "acquired": False,
        "public": False,
    }


def _learnco() -> dict:
    return {
        "name": "LearnCo",
        "description": "Innovative student-centric lending products.",
        "headline": "Reimagining student financing.",
        "website": "https://learnco.com",
        "logo_url": "https://images.prismic.io/learn-site/learnco-logo.png",
        "founders_text": "Carlos Ruiz",
        "tags": ["finance"],
        "acquired": False,
        "public": True,
    }


def test_returns_company_instance():
    assert isinstance(normalize(_edify(), 1), Company)


def test_fund_is_learn_capital():
    assert normalize(_edify(), 1).fund == "learn-capital"


def test_id_assigned():
    assert normalize(_edify(), 42).id == 42


def test_name():
    assert normalize(_edify(), 1).name == "Edify Academy"


def test_slug():
    assert normalize(_edify(), 1).slug == "edify-academy"


def test_slug_simple():
    assert normalize(_talentbridge(), 1).slug == "talentbridge"


def test_fund_url_constant():
    assert normalize(_edify(), 1).fund_url == PORTFOLIO_URL


def test_fund_url_value():
    assert normalize(_edify(), 1).fund_url == "https://learn.vc/ventures"


def test_sectors_from_tags():
    assert normalize(_edify(), 1).sectors == ["education"]


def test_sectors_community():
    assert normalize(_talentbridge(), 1).sectors == ["community"]


def test_sectors_finance():
    assert normalize(_learnco(), 1).sectors == ["finance"]


def test_website():
    assert normalize(_edify(), 1).website == "https://edify.academy"


def test_website_none_when_missing():
    raw = _edify()
    raw["website"] = None
    assert normalize(raw, 1).website is None


def test_description_uses_description_field():
    assert normalize(_edify(), 1).description == "An adaptive learning platform for K-12 students."


def test_description_falls_back_to_headline():
    assert normalize(_talentbridge(), 1).description == "Bridging the global talent gap."


def test_description_none_when_both_missing():
    raw = _edify()
    raw["description"] = None
    raw["headline"] = None
    assert normalize(raw, 1).description is None


def test_logo_url():
    assert normalize(_edify(), 1).logo_url == "https://images.prismic.io/learn-site/edify-logo.png"


def test_logo_url_none_when_missing():
    raw = _edify()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


def test_stage_none_for_active():
    assert normalize(_edify(), 1).stage is None


def test_stage_public():
    assert normalize(_learnco(), 1).stage == "Public"


def test_stage_acquired():
    raw = _edify()
    raw["acquired"] = True
    assert normalize(raw, 1).stage == "Acquired"


def test_stage_acquired_takes_priority_over_public():
    raw = _edify()
    raw["acquired"] = True
    raw["public"] = True
    assert normalize(raw, 1).stage == "Acquired"


def test_founders_none_when_empty():
    assert normalize(_edify(), 1).founders is None


def test_founders_single():
    assert normalize(_learnco(), 1).founders == ["Carlos Ruiz"]


def test_founders_multiple():
    assert normalize(_talentbridge(), 1).founders == ["Alice Kim", "Bob Chen"]


def test_founded_year_none():
    assert normalize(_edify(), 1).founded_year is None


def test_invested_year_none():
    assert normalize(_edify(), 1).invested_year is None


def test_stage_year_none():
    assert normalize(_edify(), 1).stage_year is None


def test_ticker_symbol_none():
    assert normalize(_edify(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_edify(), 1).acquirer is None


def test_source_modified_none():
    assert normalize(_edify(), 1).source_modified is None
