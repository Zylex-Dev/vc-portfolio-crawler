from agent_matcher.prompt import build_system_prompt, build_user_prompt

AGENTS = [
    {"agent_id": 1, "sredstvo": "Геймификация", "name": "Метаучебник",
     "role": "Карта знаний", "expectedBehavior": "Ученик видит карту"},
    {"agent_id": 2, "sredstvo": "Материалы", "name": "Генератор",
     "role": "Создаёт контент", "expectedBehavior": "Учитель генерирует"},
]


def test_system_prompt_lists_all_agent_ids_and_names():
    p = build_system_prompt(AGENTS)
    assert "[1]" in p and "[2]" in p
    assert "Метаучебник" in p and "Генератор" in p


def test_system_prompt_requests_json_with_agent_id():
    p = build_system_prompt(AGENTS)
    assert "JSON" in p
    assert "agent_id" in p
    assert "relevance" in p


def test_user_prompt_includes_startup_fields_and_pmo_scores():
    row = {
        "name": "LearnAI", "sectors": "AI;EdTech", "description": "Adaptive tutoring",
        "pmo_traj": 8, "pmo_mat": 7, "pmo_collab": 5, "pmo_game": 6, "pmo_feedback": 9,
    }
    r = build_user_prompt(row)
    assert "LearnAI" in r
    assert "AI;EdTech" in r
    assert "Adaptive tutoring" in r
    assert "8" in r and "9" in r


def test_user_prompt_shows_na_for_missing_fields():
    assert "N/A" in build_user_prompt({})


def test_user_prompt_renders_zero_score_as_zero():
    row = {
        "name": "Co", "sectors": "EdTech", "description": "desc",
        "pmo_traj": 0, "pmo_mat": 0, "pmo_collab": 0, "pmo_game": 0, "pmo_feedback": 0,
    }
    result = build_user_prompt(row)
    assert "0" in result
    assert "N/A" not in result
