from vc_crawler.crawlers.new_schools.normalizer import normalize
from vc_crawler.models import Company

_INIT_MAP = {714: 2024, 720: 2023}


def _acme_listing():
    return {
        "name": "Acme Edu",
        "fund_url": "https://www.newschools.org/venture/acme-edu/",
        "slug": "acme-edu",
        "logo_url": "https://www.newschools.org/wp-content/uploads/acme-logo.png",
        "sectors": ["Learning Solutions"],
        "init_year_ids": [714],
        "is_past": True,
    }


def _acme_detail():
    return {
        "description": "Acme Edu designs engaging projects for students.",
        "website": "https://acmeedu.com",
        "founded_year": 2015,
    }


def _beta_listing():
    return {
        "name": "Beta Learn",
        "fund_url": "https://www.newschools.org/venture/beta-learn/",
        "slug": "beta-learn",
        "logo_url": None,
        "sectors": ["Diverse Leaders"],
        "init_year_ids": [720],
        "is_past": False,
    }


# ── shape ─────────────────────────────────────────────────────────────────────

def test_returns_company():
    assert isinstance(normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1), Company)

def test_id():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 42).id == 42

def test_fund():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).fund == "new-schools"

# ── name / slug / fund_url ────────────────────────────────────────────────────

def test_name():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).name == "Acme Edu"

def test_slug():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).slug == "acme-edu"

def test_fund_url():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).fund_url == \
        "https://www.newschools.org/venture/acme-edu/"

# ── sectors / logo ────────────────────────────────────────────────────────────

def test_sectors():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).sectors == ["Learning Solutions"]

def test_logo_url():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).logo_url == \
        "https://www.newschools.org/wp-content/uploads/acme-logo.png"

def test_logo_url_none():
    assert normalize(_beta_listing(), {}, _INIT_MAP, 1).logo_url is None

# ── invested_year ─────────────────────────────────────────────────────────────

def test_invested_year_from_init_map():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).invested_year == 2024

def test_invested_year_beta():
    assert normalize(_beta_listing(), {}, _INIT_MAP, 1).invested_year == 2023

def test_invested_year_none_when_no_init_ids():
    listing = _acme_listing()
    listing["init_year_ids"] = []
    assert normalize(listing, {}, _INIT_MAP, 1).invested_year is None

def test_invested_year_none_when_id_not_in_map():
    listing = _acme_listing()
    listing["init_year_ids"] = [9999]
    assert normalize(listing, {}, _INIT_MAP, 1).invested_year is None

# ── stage ─────────────────────────────────────────────────────────────────────

def test_stage_past():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).stage == "Past"

def test_stage_none_when_current():
    assert normalize(_beta_listing(), {}, _INIT_MAP, 1).stage is None

# ── description / website ─────────────────────────────────────────────────────

def test_description_from_detail():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).description == \
        "Acme Edu designs engaging projects for students."

def test_description_none_when_no_detail():
    assert normalize(_acme_listing(), {}, _INIT_MAP, 1).description is None

def test_website_from_detail():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).website == "https://acmeedu.com"

def test_website_none_when_no_detail():
    assert normalize(_acme_listing(), {}, _INIT_MAP, 1).website is None

# ── founded_year ──────────────────────────────────────────────────────────────

def test_founded_year_from_detail():
    assert normalize(_acme_listing(), _acme_detail(), _INIT_MAP, 1).founded_year == 2015

def test_founded_year_none_when_absent():
    assert normalize(_acme_listing(), {}, _INIT_MAP, 1).founded_year is None

# ── always-None fields ────────────────────────────────────────────────────────

def test_stage_year_none():
    assert normalize(_acme_listing(), {}, _INIT_MAP, 1).stage_year is None

def test_ticker_symbol_none():
    assert normalize(_acme_listing(), {}, _INIT_MAP, 1).ticker_symbol is None

def test_acquirer_none():
    assert normalize(_acme_listing(), {}, _INIT_MAP, 1).acquirer is None

def test_founders_none():
    assert normalize(_acme_listing(), {}, _INIT_MAP, 1).founders is None

def test_source_modified_none():
    assert normalize(_acme_listing(), {}, _INIT_MAP, 1).source_modified is None
