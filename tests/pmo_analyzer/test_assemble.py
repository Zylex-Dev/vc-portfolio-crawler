import pandas as pd

from pmo_analyzer.assemble import merge_results


def test_merge_results_joins_scores_on_id():
    df = pd.DataFrame([
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ])
    results = {
        "1": {"pmo_score": 7.0, "pmo_traj": 8, "pmo_mat": 7,
              "pmo_collab": 5, "pmo_game": 6, "pmo_feedback": 9, "pmo_notes": "ok"},
        "2": {"pmo_score": 4.0, "pmo_traj": 4, "pmo_mat": 4,
              "pmo_collab": 4, "pmo_game": 4, "pmo_feedback": 4, "pmo_notes": "meh"},
    }
    merged = merge_results(df, results)
    assert len(merged) == 2
    assert merged.loc[merged["id"] == 1, "pmo_score"].iloc[0] == 7.0
    assert merged.loc[merged["id"] == 2, "pmo_traj"].iloc[0] == 4
    assert "name" in merged.columns


def test_merge_results_left_join_keeps_unscored_rows():
    df = pd.DataFrame([{"id": 1, "name": "A"}, {"id": 2, "name": "B"}])
    results = {
        "1": {"pmo_score": 7.0, "pmo_traj": 8, "pmo_mat": 7,
              "pmo_collab": 5, "pmo_game": 6, "pmo_feedback": 9, "pmo_notes": "ok"},
    }
    merged = merge_results(df, results)
    assert len(merged) == 2
    assert pd.isna(merged.loc[merged["id"] == 2, "pmo_score"].iloc[0])
