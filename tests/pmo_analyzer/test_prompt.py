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
    result = build_user_prompt(row)
    assert "LearnAI" in result
    assert "AI;EdTech" in result
    assert "Seed" in result
    assert "Adaptive tutoring for kids." in result


def test_user_prompt_has_no_website_content_line():
    row = {"name": "Co", "sectors": "EdTech", "stage": "Seed", "description": "desc"}
    assert "Website content" not in build_user_prompt(row)


def test_user_prompt_shows_na_for_missing_row_keys():
    result = build_user_prompt({})
    assert result.count("N/A") >= 4
