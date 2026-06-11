from unittest.mock import AsyncMock, MagicMock

from pmo_analyzer.scorer import _parse_text, score_one


def test_parse_text_extracts_all_five_sub_scores():
    text = '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"Good"}'
    result = _parse_text(text)
    assert result["pmo_traj"] == 8
    assert result["pmo_mat"] == 7
    assert result["pmo_collab"] == 5
    assert result["pmo_game"] == 6
    assert result["pmo_feedback"] == 9


def test_parse_text_calculates_pmo_score_as_average():
    text = '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"ok"}'
    assert _parse_text(text)["pmo_score"] == round((8 + 7 + 5 + 6 + 9) / 5, 1)


def test_parse_text_preserves_notes():
    text = '{"traj":5,"mat":5,"collab":5,"game":5,"feedback":5,"notes":"Средний продукт"}'
    assert _parse_text(text)["pmo_notes"] == "Средний продукт"


def test_parse_text_returns_sentinel_on_invalid_json():
    assert _parse_text("not json {{")["pmo_score"] == -1.0


def test_parse_text_returns_sentinel_on_missing_score_key():
    assert _parse_text('{"traj":8,"mat":7,"notes":"incomplete"}')["pmo_score"] == -1.0


async def test_score_one_returns_parsed_dict_on_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        '{"traj":8,"mat":7,"collab":5,"game":6,"feedback":9,"notes":"ok"}'
    )
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await score_one(
        {"name": "TestCo", "sectors": "EdTech", "stage": "Seed", "description": "test"},
        "website text",
        mock_client,
        "system prompt",
    )
    assert result["pmo_traj"] == 8
    assert result["pmo_score"] == 7.0


async def test_score_one_returns_sentinel_on_api_error():
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API error"))

    result = await score_one({}, "", mock_client, "system")
    assert result["pmo_score"] == -1.0


async def test_score_one_returns_sentinel_on_invalid_response_json():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "I cannot score this startup."
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await score_one({}, "", mock_client, "system")
    assert result["pmo_score"] == -1.0
