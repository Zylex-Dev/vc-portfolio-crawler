import httpx
from unittest.mock import AsyncMock, MagicMock

from pmo_analyzer.scraper import extract_text, scrape_url


def test_extract_text_includes_page_title():
    html = "<html><head><title>My School App</title></head><body><p>Learn here</p></body></html>"
    assert "My School App" in extract_text(html)


def test_extract_text_includes_meta_description():
    html = '<html><head><meta name="description" content="Best tutoring platform"></head><body></body></html>'
    assert "Best tutoring platform" in extract_text(html)


def test_extract_text_removes_script_content():
    html = "<html><body><script>alert('xss')</script><p>Real content</p></body></html>"
    result = extract_text(html)
    assert "alert" not in result
    assert "Real content" in result


def test_extract_text_removes_style_content():
    html = "<html><body><style>.red { color: red }</style><p>Visible text</p></body></html>"
    result = extract_text(html)
    assert ".red" not in result
    assert "Visible text" in result


def test_extract_text_truncates_to_3000_characters():
    html = f"<html><body><p>{'a' * 5000}</p></body></html>"
    assert len(extract_text(html)) <= 3000


async def test_scrape_url_returns_extracted_text_on_success():
    mock_client = AsyncMock()
    mock_response = MagicMock()
    mock_response.text = "<html><head><title>EduTech</title></head><body><p>We teach</p></body></html>"
    mock_client.get = AsyncMock(return_value=mock_response)

    result = await scrape_url("https://example.com", mock_client)
    assert "EduTech" in result
    assert "We teach" in result


async def test_scrape_url_returns_empty_string_on_timeout():
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

    result = await scrape_url("https://example.com", mock_client)
    assert result == ""


async def test_scrape_url_returns_empty_string_on_any_error():
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=Exception("connection refused"))

    result = await scrape_url("https://example.com", mock_client)
    assert result == ""
