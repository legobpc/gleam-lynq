import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
import httpx
import gzip
from io import BytesIO

from app.main import app
from app.endpoint import sitemap

# Include the sitemap router for testing
app.include_router(sitemap.router)

# ===============================
# Tests for /check-sitemap endpoint
# ===============================

@pytest.mark.asyncio
async def test_check_sitemap_urlset_success():
    """
    ✅ Test the /check-sitemap endpoint with a valid <urlset> sitemap.

    Expected:
    - HTTP 200 OK
    - sitemap_status: 'Found'
    - urls: list of 2 URLs extracted from the sitemap
    - sitemap_files: should be empty (because it's a <urlset>, not a <sitemapindex>)
    """
    sitemap_xml = """
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/page1</loc>
        </url>
        <url>
            <loc>https://example.com/page2</loc>
        </url>
    </urlset>
    """

    # Mock httpx.AsyncClient.get to return the above XML content
    with patch("app.endpoint.sitemap.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Mocked response: status 200 and content as sitemap XML
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = sitemap_xml.encode("utf-8")
        mock_instance.get.return_value = mock_response

        # Make the request using ASGITransport to simulate FastAPI server
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-sitemap", json={"domain": "example.com"})

    data = response.json()
    assert response.status_code == 200
    assert data["sitemap_status"] == "Found"
    assert data["urls"] == [
        "https://example.com/page1",
        "https://example.com/page2"
    ]
    assert data["sitemap_files"] == []


@pytest.mark.asyncio
async def test_check_sitemap_sitemapindex_success():
    """
    ✅ Test the /check-sitemap endpoint with a valid <sitemapindex> sitemap.

    Expected:
    - HTTP 200 OK
    - sitemap_status: 'Found'
    - sitemap_files: list of 2 nested sitemap files
    - urls: should be empty (because it's not a <urlset>)
    """
    sitemap_index_xml = """
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap>
            <loc>https://example.com/sitemap1.xml</loc>
        </sitemap>
        <sitemap>
            <loc>https://example.com/sitemap2.xml</loc>
        </sitemap>
    </sitemapindex>
    """

    with patch("app.endpoint.sitemap.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = sitemap_index_xml.encode("utf-8")
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-sitemap", json={"domain": "example.com"})

    data = response.json()
    assert response.status_code == 200
    assert data["sitemap_status"] == "Found"
    assert data["sitemap_files"] == [
        "https://example.com/sitemap1.xml",
        "https://example.com/sitemap2.xml"
    ]
    assert data["urls"] == []


@pytest.mark.asyncio
async def test_check_sitemap_parse_error():
    """
    ❌ Test the /check-sitemap endpoint with invalid (broken) XML.

    Expected:
    - HTTP 200 OK
    - sitemap_status: 'Parse Error'
    - message: contains 'Failed to parse sitemap XML'
    """
    invalid_xml = "<invalid><xml>"

    with patch("app.endpoint.sitemap.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = invalid_xml.encode("utf-8")
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-sitemap", json={"domain": "example.com"})

    data = response.json()
    assert response.status_code == 200
    assert data["sitemap_status"] == "Parse Error"
    assert "Failed to parse sitemap XML" in data["message"]


@pytest.mark.asyncio
async def test_check_sitemap_not_found():
    """
    🔍 Test the /check-sitemap endpoint when the sitemap is missing (404).

    Expected:
    - HTTP 200 OK
    - sitemap_status: 'Not Found'
    - http_status: 404
    - message: contains 'Sitemap returned status 404'
    """
    with patch("app.endpoint.sitemap.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_response.status_code = 404
        mock_response.content = b""
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-sitemap", json={"domain": "example.com"})

    data = response.json()
    assert response.status_code == 200
    assert data["sitemap_status"] == "Not Found"
    assert data["http_status"] == 404


@pytest.mark.asyncio
async def test_check_sitemap_request_error():
    """
    🚫 Test the /check-sitemap endpoint when a network request error occurs (e.g., connection failure).

    Expected:
    - HTTP 200 OK
    - sitemap_status: 'Error'
    - http_status: None
    - message: contains 'Request error'
    """
    with patch("app.endpoint.sitemap.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Simulate network failure
        mock_instance.get.side_effect = httpx.RequestError("Connection failed")

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/check-sitemap", json={"domain": "example.com"})

    data = response.json()
    assert response.status_code == 200
    assert data["sitemap_status"] == "Error"
    assert data["http_status"] is None

# ===============================
# Tests for /fetch-sitemap-urls endpoint
# ===============================

@pytest.mark.asyncio
async def test_fetch_sitemap_urls_success():
    """
    ✅ Test the /fetch-sitemap-urls endpoint with a valid XML sitemap.

    Expected:
    - HTTP 200 OK
    - sitemap_status: 'Parsed'
    - urls: list of URLs extracted
    """
    sitemap_xml = """
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/page1</loc>
        </url>
    </urlset>
    """

    with patch("app.endpoint.sitemap.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = sitemap_xml.encode("utf-8")
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/fetch-sitemap-urls", json={"sitemap_url": "https://example.com/sitemap.xml"})

    data = response.json()
    assert response.status_code == 200
    assert data["sitemap_status"] == "Parsed"
    assert data["urls"] == ["https://example.com/page1"]


@pytest.mark.asyncio
async def test_fetch_sitemap_urls_gzip_success():
    """
    ✅ Test the /fetch-sitemap-urls endpoint with a valid gzipped XML sitemap.

    Expected:
    - HTTP 200 OK
    - sitemap_status: 'Parsed'
    - urls: list of URLs extracted
    """
    # Prepare gzipped sitemap XML content
    sitemap_xml = """
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/page1</loc>
        </url>
    </urlset>
    """
    buffer = BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb") as f:
        f.write(sitemap_xml.encode("utf-8"))
    gzipped_content = buffer.getvalue()

    with patch("app.endpoint.sitemap.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = gzipped_content
        mock_instance.get.return_value = mock_response

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/fetch-sitemap-urls", json={"sitemap_url": "https://example.com/sitemap.xml.gz"})

    data = response.json()
    assert response.status_code == 200
    assert data["sitemap_status"] == "Parsed"
    assert data["urls"] == ["https://example.com/page1"]
