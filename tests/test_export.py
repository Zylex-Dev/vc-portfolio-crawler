import csv
import json

from sequoia_crawler.export import write_json, write_csv
from sequoia_crawler.models import Company


def _company():
    return Company(
        id=1, name="AdMob", slug="admob", sequoia_url="https://x/",
        sectors=["GTM", "AI"], website="https://www.admob.com", stage="Acquired",
        stage_year=2010,
    )


def test_write_json_round_trips(tmp_path):
    path = tmp_path / "companies.json"
    write_json([_company()], path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data[0]["name"] == "AdMob"
    assert data[0]["sectors"] == ["GTM", "AI"]
    assert data[0]["stage_year"] == 2010


def test_write_csv_joins_sectors_and_has_header(tmp_path):
    path = tmp_path / "companies.csv"
    write_csv([_company()], path)
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows[0]["sectors"] == "GTM;AI"
    assert rows[0]["name"] == "AdMob"
    assert rows[0]["stage"] == "Acquired"


def test_writers_create_missing_parent_dir(tmp_path):
    nested = tmp_path / "out" / "companies.json"
    write_json([_company()], nested)
    assert nested.exists()
