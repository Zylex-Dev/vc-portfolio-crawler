from vc_crawler.crawlers.brighteye.normalizer import normalize, PORTFOLIO_URL
from vc_crawler.models import Company


def _zen():
    return {
        "slug": "zen-educate",
        "location": "UK",
        "logo_url": "https://cdn.prod.website-files.com/zen_logo.avif",
        "website": "https://www.zeneducate.com/",
        "is_exited": False,
        "name": "Zen Educate",
        "description": "Leading UK/US supply teacher marketplace.",
        "categories": ["Work"],
    }


def _uphill():
    return {
        "slug": "uphill",
        "location": "Portugal",
        "logo_url": "https://cdn.prod.website-files.com/uphill_logo.avif",
        "website": "https://uphillhealth.com/",
        "is_exited": False,
        "name": None,
        "description": None,
        "categories": [],
    }


def _htb():
    """Slug with -copy suffix, no name, no website."""
    return {
        "slug": "hack-the-box-copy",
        "location": "Greece / UK",
        "logo_url": "https://cdn.prod.website-files.com/htb_logo.avif",
        "website": None,
        "is_exited": False,
        "name": None,
        "description": None,
        "categories": [],
    }


def _gosu():
    return {
        "slug": "gosu",
        "location": "France",
        "logo_url": "https://cdn.prod.website-files.com/gosu_logo.avif",
        "website": None,
        "is_exited": True,
        "name": None,
        "description": None,
        "categories": [],
    }


# --- Basic shape ---

def test_returns_company_instance():
    assert isinstance(normalize(_zen(), 1), Company)


def test_fund_is_brighteye():
    assert normalize(_zen(), 1).fund == "brighteye"


def test_id_assigned():
    assert normalize(_zen(), 42).id == 42


def test_fund_url_constant():
    assert normalize(_zen(), 1).fund_url == PORTFOLIO_URL


def test_fund_url_value():
    assert normalize(_zen(), 1).fund_url == "https://www.brighteyevc.com/portfolio"


# --- Name ---

def test_name_from_featured():
    assert normalize(_zen(), 1).name == "Zen Educate"


def test_name_derived_from_slug_when_no_featured_name():
    assert normalize(_uphill(), 1).name == "Uphill"


def test_name_derived_multiword():
    raw = _uphill()
    raw["slug"] = "iron-hack"
    assert normalize(raw, 1).name == "Iron Hack"


def test_name_strips_copy_suffix():
    assert normalize(_htb(), 1).name == "Hack The Box"


def test_name_strips_copy_suffix_multiword():
    raw = _uphill()
    raw["slug"] = "some-company-copy"
    assert normalize(raw, 1).name == "Some Company"


# --- Slug ---

def test_slug_unchanged_for_clean_slug():
    assert normalize(_zen(), 1).slug == "zen-educate"


def test_slug_copy_suffix_removed():
    assert normalize(_htb(), 1).slug == "hack-the-box"


# --- Sectors ---

def test_sectors_from_featured():
    assert normalize(_zen(), 1).sectors == ["Work"]


def test_sectors_empty_when_no_featured():
    assert normalize(_uphill(), 1).sectors == []


# --- Website ---

def test_website():
    assert normalize(_zen(), 1).website == "https://www.zeneducate.com/"


def test_website_none_when_missing():
    assert normalize(_gosu(), 1).website is None


# --- Description ---

def test_description_from_featured():
    assert normalize(_zen(), 1).description == "Leading UK/US supply teacher marketplace."


def test_description_none_when_not_featured():
    assert normalize(_uphill(), 1).description is None


# --- Stage ---

def test_stage_exited():
    assert normalize(_gosu(), 1).stage == "Exited"


def test_stage_none_when_not_exited():
    assert normalize(_zen(), 1).stage is None


# --- Logo ---

def test_logo_url():
    assert normalize(_zen(), 1).logo_url == "https://cdn.prod.website-files.com/zen_logo.avif"


def test_logo_url_none_when_missing():
    raw = _zen()
    raw["logo_url"] = None
    assert normalize(raw, 1).logo_url is None


# --- All-None fields ---

def test_stage_year_none():
    assert normalize(_zen(), 1).stage_year is None


def test_founded_year_none():
    assert normalize(_zen(), 1).founded_year is None


def test_invested_year_none():
    assert normalize(_zen(), 1).invested_year is None


def test_source_modified_none():
    assert normalize(_zen(), 1).source_modified is None


def test_ticker_symbol_none():
    assert normalize(_zen(), 1).ticker_symbol is None


def test_acquirer_none():
    assert normalize(_zen(), 1).acquirer is None


def test_founders_none():
    assert normalize(_zen(), 1).founders is None
