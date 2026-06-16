from unittest.mock import AsyncMock, MagicMock

from agent_matcher.matcher import _parse_response, match_one


def test_parse_response_extracts_fields():
    r = _parse_response('{"agent_id": 5, "relevance": 8, "rationale": "Подходит"}')
    assert r["agent_id"] == 5
    assert r["relevance"] == 8
    assert r["rationale"] == "Подходит"


def test_parse_response_handles_markdown_fences_and_noise():
    r = _parse_response('Вот ответ:\n```json\n{"agent_id": 3, "relevance": 7, "rationale": "ok"}\n```')
    assert r["agent_id"] == 3
    assert r["relevance"] == 7


def test_parse_response_sentinel_on_invalid_json():
    assert _parse_response("not json at all")["agent_id"] == -1


def test_parse_response_sentinel_on_missing_key():
    r = _parse_response('{"relevance": 8, "rationale": "no id"}')
    assert r["agent_id"] == -1
    assert r["rationale"] == "parse_error"


async def test_match_one_returns_parsed_dict_on_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = (
        '{"agent_id": 4, "relevance": 9, "rationale": "ok"}'
    )
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    r = await match_one({"name": "TestCo"}, mock_client, "system prompt")
    assert r["agent_id"] == 4
    assert r["relevance"] == 9


async def test_match_one_returns_sentinel_on_api_error():
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("API error"))

    r = await match_one({}, mock_client, "system")
    assert r["agent_id"] == -1
