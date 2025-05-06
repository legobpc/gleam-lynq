import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
import httpx

from app.main import app
from app.endpoint import url  # assuming your file is named url.py

# Include the URL checker router for testing
app.include_router(url.router)

@pytest.mark.asyncio
async def test_check_url_basic_success():
    """
    ✅ Test /check-url endpoint with a simple valid HTML page.

    Expected:
    - HTTP 200 OK
    - Extracts title, description, canonical, h1, and basic meta tags.
    """
    html_content = """
    <html lang="en">
        <head>
            <title>Test Page</title>
            <meta name="description" content="This is a test description.">
            <meta name="robots" content="index, follow">
            <link rel="canonical" href="https://example.com/page" />
            <link rel="icon" href="/favicon.ico" />
            <meta property="og:title" content="OG Test Title">
            <meta name="twitter:title" content="Twitter Test Title">
            <script type="application/ld+json">{"@context":"https://schema.org"}</script>
            <link rel="alternate" hreflang="en" href="https://example.com/en" />
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Subheading</h2>
        </body>
    </html>
    """

    with patch("app.endpoint.url.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_response.content = html_content.encode("utf-8")
        mock_response.headers = {
            "Content-Type": "text/html; charset=UTF-8",
            "Content-Length": str(len(html_content)),
            "X-Robots-Tag": "noindex"
        }
        mock_response.history = []
        mock_response.url = "https://example.com/page"
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-url", json={"url": "https://example.com/page"})

    data = response.json()
    assert response.status_code == 200
    assert data["http_status"] == 200
    assert data["title"] == "Test Page"
    assert data["description"] == "This is a test description."
    assert data["canonical"] == "https://example.com/page"
    assert data["canonical_matches"] is True
    assert data["h1"] == "Main Heading"
    assert data["all_h1"] == ["Main Heading"]
    assert len(data["headings"]) == 2
    assert any(tag["tag"] == "h2" and tag["text"] == "Subheading" for tag in data["headings"])
    assert data["robots_meta"] == "index, follow"
    assert data["x_robots_tag"] == "noindex"
    assert data["content_type"].startswith("text/html")
    assert data["content_length"] == len(html_content)
    assert data["open_graph"] == {"og:title": "OG Test Title"}
    assert data["twitter_meta"] == {"twitter:title": "Twitter Test Title"}
    assert data["schema_json_ld"] == '{"@context":"https://schema.org"}'
    assert data["alternate_hreflang"][0]["hreflang"] == "en"
    assert data["lang"] == "en"
    assert data["favicon_url"] == "/favicon.ico"
    assert "URL checked successfully" in data["message"]

@pytest.mark.asyncio
async def test_check_url_redirected():
    """
    🔄 Test /check-url endpoint when the URL is redirected (with history).
    """
    html_content = "<html><head><title>Redirected Page</title></head><body></body></html>"

    with patch("app.endpoint.url.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        redirect_history = [httpx.Response(301, headers={"Location": "https://example.com/page"})]
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_response.content = html_content.encode("utf-8")
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.history = redirect_history
        mock_response.url = "https://example.com/page"
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-url", json={"url": "https://example.com/start"})

    data = response.json()
    assert response.status_code == 200
    assert data["redirected"] is True
    assert data["final_url"] == "https://example.com/page"
    assert data["title"] == "Redirected Page"

@pytest.mark.asyncio
async def test_check_url_no_content_type_but_html():
    """
    🧐 Test edge case where Content-Type is missing but the content is HTML.

    Expected:
    - Should still parse HTML based on body start.
    """
    html_content = "<!doctype html><html><head><title>HTML No Type</title></head><body></body></html>"

    with patch("app.endpoint.url.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_response.content = html_content.encode("utf-8")
        mock_response.headers = {}  # No Content-Type header
        mock_response.history = []
        mock_response.url = "https://example.com/no-type"
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-url", json={"url": "https://example.com/no-type"})

    data = response.json()
    assert response.status_code == 200
    assert data["title"] == "HTML No Type"

@pytest.mark.asyncio
async def test_check_url_invalid_content_length():
    """
    🧪 Test edge case where Content-Length header is invalid (non-numeric).

    Expected:
    - content_length should be None (fallback).
    """
    html_content = "<html><head><title>Invalid Length</title></head><body></body></html>"

    with patch("app.endpoint.url.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_response.content = html_content.encode("utf-8")
        mock_response.headers = {
            "Content-Type": "text/html",
            "Content-Length": "abc"  # invalid
        }
        mock_response.history = []
        mock_response.url = "https://example.com/invalid-length"
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-url", json={"url": "https://example.com/invalid-length"})

    data = response.json()
    assert response.status_code == 200
    assert data["content_length"] is None

@pytest.mark.asyncio
async def test_check_url_empty_robots_meta():
    """
    🦾 Test edge case where <meta name="robots" content=""> is empty.

    Expected:
    - robots_meta should return an empty string (not None).
    """
    html_content = """
    <html>
        <head>
            <title>Robots Empty</title>
            <meta name="robots" content="">
        </head>
        <body></body>
    </html>
    """

    with patch("app.endpoint.url.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_response.content = html_content.encode("utf-8")
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.history = []
        mock_response.url = "https://example.com/robots-empty"
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-url", json={"url": "https://example.com/robots-empty"})

    data = response.json()
    assert response.status_code == 200
    assert data["robots_meta"] == ""  # Should return empty string

@pytest.mark.asyncio
async def test_check_url_204_no_content():
    """
    🚫 Test edge case where server responds with 204 No Content.

    Expected:
    - No parsing happens, all SEO fields stay None/empty.
    """
    with patch("app.endpoint.url.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_response.content = b""
        mock_response.headers = {"Content-Type": "text/html"}
        mock_response.history = []
        mock_response.url = "https://example.com/no-content"
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-url", json={"url": "https://example.com/no-content"})

    data = response.json()
    assert response.status_code == 200
    assert data["http_status"] == 204
    assert data["title"] is None
    assert data["description"] is None
