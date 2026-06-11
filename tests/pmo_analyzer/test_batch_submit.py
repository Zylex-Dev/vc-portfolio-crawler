import pandas as pd

from pmo_analyzer.batch_submit import build_requests


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"id": 1, "slug": "company-a", "name": "Alpha", "sectors": "EdTech", "stage": "Seed",     "description": "Adaptive learning"},
        {"id": 2, "slug": "company-b", "name": "Beta",  "sectors": "AI",     "stage": "Series A", "description": "AI tutor"},
    ])


def test_build_requests_returns_one_request_per_row():
    assert len(build_requests(_sample_df(), {})) == 2


def test_build_requests_custom_id_equals_startup_id_as_string():
    requests = build_requests(_sample_df(), {})
    ids = {r["custom_id"] for r in requests}
    assert ids == {"1", "2"}


def test_build_requests_uses_scraped_text_when_slug_present():
    scraped = {"company-a": "great platform for students"}
    requests = build_requests(_sample_df(), scraped)
    request_a = next(r for r in requests if r["custom_id"] == "1")
    content = request_a["params"]["messages"][0]["content"]
    assert "great platform for students" in content


def test_build_requests_uses_na_when_slug_missing_from_scraped():
    requests = build_requests(_sample_df(), {})
    content = requests[0]["params"]["messages"][0]["content"]
    assert "N/A" in content


def test_build_requests_uses_haiku_model():
    requests = build_requests(_sample_df(), {})
    assert requests[0]["params"]["model"] == "claude-haiku-4-5"


def test_build_requests_max_tokens_is_256():
    requests = build_requests(_sample_df(), {})
    assert requests[0]["params"]["max_tokens"] == 256
