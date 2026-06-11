import pandas as pd
from unittest.mock import MagicMock

from pmo_analyzer.batch_collect import parse_result, merge_results

_ALL_COLS = ["pmo_score", "pmo_traj", "pmo_mat", "pmo_collab", "pmo_game", "pmo_feedback", "pmo_notes"]


def _make_success(custom_id: str, json_text: str) -> MagicMock:
    result = MagicMock()
    result.custom_id = custom_id
    result.result.type = "succeeded"
    block = MagicMock()
    block.type = "text"
    block.text = json_text
    result.result.message.content = [block]
    return result


def _make_errored(custom_id: str) -> MagicMock:
    result = MagicMock()
    result.custom_id = custom_id
    result.result.type = "errored"
    return result


def test_parse_result_extracts_all_five_sub_scores():
    raw = _make_success("1", '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"Good"}')
    parsed = parse_result(raw)
    assert parsed["pmo_traj"] == 8
    assert parsed["pmo_mat"] == 7
    assert parsed["pmo_collab"] == 5
    assert parsed["pmo_game"] == 6
    assert parsed["pmo_feedback"] == 9


def test_parse_result_calculates_pmo_score_as_average():
    raw = _make_success("1", '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"ok"}')
    parsed = parse_result(raw)
    assert parsed["pmo_score"] == round((8 + 7 + 5 + 6 + 9) / 5, 1)  # 7.0


def test_parse_result_preserves_notes():
    raw = _make_success("1", '{"traj":5,"mat":5,"collab":5,"game":5,"feedback":5,"notes":"Средний продукт"}')
    assert parse_result(raw)["pmo_notes"] == "Средний продукт"


def test_parse_result_returns_sentinel_on_invalid_json():
    raw = _make_success("1", "not valid {{ json")
    assert parse_result(raw)["pmo_score"] == -1.0


def test_parse_result_returns_sentinel_on_errored_result():
    assert parse_result(_make_errored("2"))["pmo_score"] == -1.0


def test_merge_results_adds_all_seven_new_columns():
    df = pd.DataFrame([{"id": 1, "name": "Co A"}, {"id": 2, "name": "Co B"}])
    results = {
        "1": {"pmo_score": 7.0, "pmo_traj": 7, "pmo_mat": 7, "pmo_collab": 7, "pmo_game": 7, "pmo_feedback": 7, "pmo_notes": "ok"},
        "2": {"pmo_score": -1.0, "pmo_traj": -1, "pmo_mat": -1, "pmo_collab": -1, "pmo_game": -1, "pmo_feedback": -1, "pmo_notes": "error"},
    }
    merged = merge_results(df, results)
    for col in _ALL_COLS:
        assert col in merged.columns, f"Missing column: {col}"


def test_merge_results_preserves_original_columns():
    df = pd.DataFrame([{"id": 1, "name": "Co A", "fund": "a16z", "sectors": "EdTech"}])
    results = {"1": {"pmo_score": 5.0, "pmo_traj": 5, "pmo_mat": 5, "pmo_collab": 5, "pmo_game": 5, "pmo_feedback": 5, "pmo_notes": "avg"}}
    merged = merge_results(df, results)
    assert merged.iloc[0]["fund"] == "a16z"
    assert merged.iloc[0]["sectors"] == "EdTech"


def test_merge_results_aligns_scores_to_correct_row():
    df = pd.DataFrame([{"id": 10, "name": "X"}, {"id": 20, "name": "Y"}])
    results = {
        "10": {"pmo_score": 9.0, "pmo_traj": 9, "pmo_mat": 9, "pmo_collab": 9, "pmo_game": 9, "pmo_feedback": 9, "pmo_notes": "great"},
        "20": {"pmo_score": 2.0, "pmo_traj": 2, "pmo_mat": 2, "pmo_collab": 2, "pmo_game": 2, "pmo_feedback": 2, "pmo_notes": "poor"},
    }
    merged = merge_results(df, results)
    assert merged.loc[merged["name"] == "X", "pmo_score"].iloc[0] == 9.0
    assert merged.loc[merged["name"] == "Y", "pmo_score"].iloc[0] == 2.0
