from vc_crawler.crawlers.edu_capital.normalizer import normalize, PORTFOLIO_URL, _name_from_url
from vc_crawler.models import Company


def _r360():
    return {
        "logo_url": "https://cdn.prod.website-files.com/abc123_360_logo.png",
        "description": "Collaborative LMS",
        "category": "Future of work",
        "website": "https://360learning.com",
        "acquired": False,
    }


def _rappscho():
    return {
        "logo_url": "https://cdn.prod.website-files.com/def456_Appscho_.png",
        "description": "Application for school management for students",
        "category": "Future of education",
        "website": "https://www.appscho.com/",
        "acquired": True,
    }


def _rbuddy():
    return {
        "logo_url": "https://cdn.prod.website-files.com/ghi789_buddy_logo.jpg",
        "description": "AI-based language tutor for children",
        "category": "Future of education",
        "website": "https://buddy.ai/fr/",
        "acquired": False,
    }


def _remma():
    return {
        "logo_url": "https://cdn.prod.website-files.com/jkl012_screenshot.jpg",
        "description": "Conversational AI for language learning",
        "category": "Future of education",
        "website": "https://apps.apple.com/fr/app/emma-parler-anglais/id6737470910",
        "acquired": False,
    }


# --- Basic shape ---

def test_returns_company_instance():
    assert isinstance(normalize(_r360(), 1), Company)


def test_fund_is_edu_capital():
    assert normalize(_r360(), 1).fund == "edu-capital"


def test_id_assigned():
    assert normalize(_r360(), 42).id == 42


def test_fund_url_constant():
    assert normalize(_r360(), 1).fund_url == PORTFOLIO_URL


def test_fund_url_value():
    assert normalize(_r360(), 1).fund_url == "https://www.educapitalvc.com/portfolio"


# --- _name_from_url ---

def test_name_from_url_plain_domain():
    assert _name_from_url("https://360learning.com") == "360learning"


def test_name_from_url_strips_www():
    assert _name_from_url("https://www.appscho.com/") == "appscho"


def test_name_from_url_subdomain_stripped():
    assert _name_from_url("https://buddy.ai/fr/") == "buddy"


def test_name_from_url_apple_store():
    assert _name_from_url(
        "https://apps.apple.com/fr/app/emma-parler-anglais/id6737470910"
    ) == "emma"


def test_name_from_url_empty_string():
    assert _name_from_url("") == ""


# --- name field on Company ---

def test_name_360learning():
    assert normalize(_r360(), 1).name == "360learning"


def test_name_appscho():
    assert normalize(_rappscho(), 1).name == "appscho"


def test_name_buddy():
    assert normalize(_rbuddy(), 1).name == "buddy"


def test_name_emma_from_apple_url():
    assert normalize(_remma(), 1).name == "emma"


# --- slug ---

def test_slug_360learning():
    assert normalize(_r360(), 1).slug == "360learning"


def test_slug_appscho():
    assert normalize(_rappscho(), 1).slug == "appscho"


# --- sectors ---

def test_sectors_future_of_work():
    assert normalize(_r360(), 1).sectors == ["Future of work"]


def test_sectors_future_of_education():
    assert normalize(_rbuddy(), 1).sectors == ["Future of education"]


def test_sectors_empty_when_no_category():
    raw = _r360()
    raw["category"] = None
    assert normalize(raw, 1).sectors == []


# --- description ---

def test_description():
    assert normalize(_r360(), 1).description == "Collaborative LMS"


def test_description_none_when_missing():
    raw = _r360()
    raw["description"] = None
    assert normalize(raw, 1).description is None


# --- website ---

def test_website():
    assert normalize(_r360(), 1).website == "https://360learning.com"


def test_website_none_when_missing():
    raw = _r360()
    raw["website"] = None
    assert normalize(raw, 1).website is None


# --- stage ---

def test_stage_acquired():
    assert normalize(_rappscho(), 1).stage == "Acquired"


def test_stage_none_when_not_acquired():
    assert normalize(_r360(), 1).stage is None


# --- logo ---

def test_logo_url():
    assert normalize(_r360(), 1).logo_url == "https://cdn.prod.website-files.com/abc123_360_logo.png"


def test_logo_url_none_when_missing():
    raw = _r360()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


# --- All-None fields ---

def test_stage_year_none():
    assert normalize(_r360(), 1).stage_year is None


def test_founded_year_none():
    assert normalize(_r360(), 1).founded_year is None


def test_invested_year_none():
    assert normalize(_r360(), 1).invested_year is None


def test_source_modified_none():
    assert normalize(_r360(), 1).source_modified is None


def test_ticker_symbol_none():
    assert normalize(_r360(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_r360(), 1).acquirer is None


def test_founders_none():
    assert normalize(_r360(), 1).founders is None
