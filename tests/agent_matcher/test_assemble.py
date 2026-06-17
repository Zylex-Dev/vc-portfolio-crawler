import pandas as pd

from agent_matcher.assemble import build_agent_pivot_df, build_assignment_df

AGENTS = [
    {"agent_id": 1, "name": "Метаучебник", "sredstvo": "Геймификация",
     "developmentStatus": "Протестировать", "role": "r", "expectedBehavior": "e"},
    {"agent_id": 2, "name": "Генератор", "sredstvo": "Материалы",
     "developmentStatus": "В разработке", "role": "r", "expectedBehavior": "e"},
]


def _df():
    return pd.DataFrame([
        {"id": 10, "name": "A", "fund": "f", "sectors": "EdTech", "pmo_score": 5.0},
        {"id": 11, "name": "B", "fund": "f", "sectors": "EdTech", "pmo_score": 6.0},
        {"id": 12, "name": "C", "fund": "f", "sectors": "EdTech", "pmo_score": 7.0},
        {"id": 13, "name": "D", "fund": "f", "sectors": "EdTech", "pmo_score": 3.0},
    ])


def _results():
    return {
        "10": {"agent_id": 1, "relevance": 9, "rationale": "strong"},
        "11": {"agent_id": 1, "relevance": 6, "rationale": "weak"},    # < threshold -> unmatched
        "12": {"agent_id": 0, "relevance": 0, "rationale": "none"},    # explicit none -> unmatched
        "13": {"agent_id": -1, "relevance": -1, "rationale": "error"}, # error
    }


def test_assignment_threshold_and_groups():
    a = build_assignment_df(_df(), _results(), AGENTS, threshold=7)
    byid = {int(r["id"]): r for _, r in a.iterrows()}
    assert byid[10]["assigned_agent"] == "Метаучебник"
    assert byid[10]["agent_sredstvo"] == "Геймификация"
    assert byid[10]["sectors"] == "EdTech"
    assert byid[10]["rationale"] == "strong"
    assert byid[11]["assigned_agent"] == "unmatched"
    assert byid[12]["assigned_agent"] == "unmatched"
    assert byid[13]["assigned_agent"] == "error"


def test_assignment_has_full_column_schema():
    df = pd.DataFrame([{
        "id": 10, "fund": "f", "name": "A", "sectors": "EdTech",
        "website": "a.com", "description": "desc", "stage": "Seed",
        "stage_year": 2021, "founded_year": 2019, "invested_year": 2020,
        "pmo_score": 5.0, "pmo_traj": 5, "pmo_mat": 6, "pmo_collab": 4,
        "pmo_game": 3, "pmo_feedback": 7, "pmo_notes": "ok",
    }])
    res = {"10": {"agent_id": 1, "relevance": 9, "rationale": "strong"}}
    a = build_assignment_df(df, res, AGENTS, threshold=7)
    assert list(a.columns) == [
        "id", "fund", "name", "sectors", "website", "description",
        "stage", "stage_year", "founded_year", "invested_year",
        "pmo_score", "pmo_traj", "pmo_mat", "pmo_collab", "pmo_game",
        "pmo_feedback", "pmo_notes",
        "assigned_agent", "agent_sredstvo", "agent_status",
        "relevance", "rationale",
    ]
    r = a.iloc[0]
    assert r["website"] == "a.com" and r["pmo_notes"] == "ok"
    assert r["stage"] == "Seed" and r["founded_year"] == 2019


def test_assignment_invalid_agent_id_is_unmatched():
    res = {"10": {"agent_id": 999, "relevance": 10, "rationale": "x"}}
    df = pd.DataFrame([{"id": 10, "name": "A", "fund": "f", "sectors": "EdTech", "pmo_score": 5.0}])
    a = build_assignment_df(df, res, AGENTS)
    assert a.iloc[0]["assigned_agent"] == "unmatched"


def test_pivot_has_all_agents_plus_unmatched_and_error():
    a = build_assignment_df(_df(), _results(), AGENTS, threshold=7)
    p = build_agent_pivot_df(a, AGENTS)
    names = list(p["agent_name"])
    assert "Метаучебник" in names
    assert "Генератор" in names          # ноль стартапов, но строка присутствует
    assert "unmatched" in names
    assert "error" in names
    meta = p[p["agent_name"] == "Метаучебник"].iloc[0]
    assert meta["num_startups"] == 1
    assert "A (9)" in meta["startups"]
    genr = p[p["agent_name"] == "Генератор"].iloc[0]
    assert genr["num_startups"] == 0


def test_pivot_sorts_startups_by_relevance_desc():
    df = pd.DataFrame([
        {"id": 1, "name": "Low", "fund": "f", "sectors": "e", "pmo_score": 1},
        {"id": 2, "name": "High", "fund": "f", "sectors": "e", "pmo_score": 1},
    ])
    res = {
        "1": {"agent_id": 1, "relevance": 7, "rationale": ""},
        "2": {"agent_id": 1, "relevance": 10, "rationale": ""},
    }
    a = build_assignment_df(df, res, AGENTS)
    s = build_agent_pivot_df(a, AGENTS)
    row = s[s["agent_name"] == "Метаучебник"].iloc[0]["startups"]
    assert row.index("High") < row.index("Low")
