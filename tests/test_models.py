from sequoia_crawler.models import Company, CSV_FIELDS


def _company():
    return Company(
        id=1, name="AdMob", slug="admob",
        sequoia_url="https://sequoiacap.com/companies/admob/",
        sectors=["GTM", "AI"], website="https://www.admob.com",
    )


def test_to_dict_keeps_sectors_as_list():
    d = _company().to_dict()
    assert d["name"] == "AdMob"
    assert d["sectors"] == ["GTM", "AI"]
    assert "status" not in d
    assert "status_year" not in d


def test_stage_year_field_exists_and_status_is_gone():
    c = _company()
    assert c.stage_year is None
    assert "stage_year" in CSV_FIELDS
    assert "status" not in CSV_FIELDS
    assert not hasattr(c, "status")


def test_to_csv_row_joins_sectors():
    row = _company().to_csv_row()
    assert row["sectors"] == "GTM;AI"
    assert row["website"] == "https://www.admob.com"


def test_csv_fields_match_dataclass_keys():
    assert set(CSV_FIELDS) == set(_company().to_dict().keys())


def test_stage_field_defaults_to_none_and_is_exported():
    c = _company()
    assert c.stage is None
    assert "stage" in c.to_dict()
    assert "stage" in CSV_FIELDS
