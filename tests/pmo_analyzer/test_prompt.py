from pmo_analyzer.prompt import build_system_prompt, build_user_prompt


def test_system_prompt_contains_all_five_instruments():
    prompt = build_system_prompt()
    for instrument in ["TRAJ", "MAT", "COLLAB", "GAME", "FEEDBACK"]:
        assert instrument in prompt, f"Missing instrument: {instrument}"


def test_system_prompt_requests_json_output():
    assert "JSON" in build_system_prompt()


def test_user_prompt_includes_name_sectors_stage_description():
    row = {
        "name": "LearnAI",
        "sectors": "AI;EdTech",
        "stage": "Seed",
        "description": "Adaptive tutoring for kids.",
    }
    result = build_user_prompt(row, "Homepage: AI-powered learning")
    assert "LearnAI" in result
    assert "AI;EdTech" in result
    assert "Seed" in result
    assert "Adaptive tutoring for kids." in result
    assert "AI-powered learning" in result


def test_user_prompt_shows_na_when_scraped_text_is_empty():
    row = {"name": "Co", "sectors": "EdTech", "stage": "Series A", "description": "desc"}
    assert "N/A" in build_user_prompt(row, "")


def test_user_prompt_shows_na_when_scraped_text_is_none():
    row = {"name": "Co", "sectors": "EdTech", "stage": "Series A", "description": "desc"}
    assert "N/A" in build_user_prompt(row, None)
