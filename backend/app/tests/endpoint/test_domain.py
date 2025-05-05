import pytest
import httpx
import dns.resolver

from httpx import AsyncClient
from httpx import ASGITransport
from app.main import app
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_check_domain_success():
    # Mock DNS resolve to work fine
    with patch("app.endpoint.domain.dns.resolver.resolve") as mock_resolve:
        mock_resolve.return_value = True

        # Mock HTTP GET to return 200
        with patch("app.endpoint.domain.httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.history = []
            mock_response.url = "https://example.com"
            mock_get.return_value = mock_response

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/domain/check-domain", json={"domain": "example.com"})

            data = response.json()
            assert response.status_code == 200
            assert data["dns_status"] == "ok"
            assert data["http_status"] == 200
            assert data["is_live"] is True
            assert data["redirected"] is False
            assert data["final_url"] == "https://example.com"
            assert data["redirect_chain"] == []
            assert "Domain is live" in data["message"]


@pytest.mark.asyncio
async def test_check_domain_dns_nxdomain():
    # Mock DNS to raise NXDOMAIN
    with patch("app.endpoint.domain.dns.resolver.resolve") as mock_resolve:
        mock_resolve.side_effect = dns.resolver.NXDOMAIN()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/domain/check-domain", json={"domain": "nonexistent.com"})

        data = response.json()
        assert response.status_code == 200
        assert data["dns_status"] == "NXDOMAIN"
        assert data["is_live"] is False
        assert data["http_status"] is None
        assert "DNS issue: NXDOMAIN" in data["message"]


@pytest.mark.asyncio
async def test_check_domain_http_connection_error():
    # Mock DNS to work fine
    with patch("app.endpoint.domain.dns.resolver.resolve") as mock_resolve:
        mock_resolve.return_value = True

        # Mock HTTP GET to raise RequestError
        with patch("app.endpoint.domain.httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.RequestError("Connection failed")

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/domain/check-domain", json={"domain": "fail.com"})

            data = response.json()
            assert response.status_code == 200
            assert data["dns_status"] == "ok"
            assert data["is_live"] is False
            assert data["http_status"] is None
            assert "Connection error" in data["message"]


@pytest.mark.asyncio
async def test_check_domain_redirected():
    # Mock DNS to work fine
    with patch("app.endpoint.domain.dns.resolver.resolve") as mock_resolve:
        mock_resolve.return_value = True

        # Mock HTTP GET to simulate redirect
        with patch("app.endpoint.domain.httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.history = [
                AsyncMock(url="https://google.com"),
                AsyncMock(url="https://www.google.com")
            ]
            mock_response.url = "https://www.google.com/final"
            mock_get.return_value = mock_response

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://google.com") as ac:
                response = await ac.post("/domain/check-domain", json={"domain": "google.com"})

            data = response.json()
            assert response.status_code == 200
            assert data["redirected"] is True
            assert data["final_url"] == "https://www.google.com/final"
            assert data["redirect_chain"] == [
                "https://google.com",
                "https://www.google.com"
            ]

@pytest.mark.asyncio
async def test_check_domain_no_redirect():
    # Mock DNS to resolve successfully
    with patch("app.endpoint.domain.dns.resolver.resolve") as mock_resolve:
        mock_resolve.return_value = True

        # Mock HTTP GET to return 200 without redirect
        with patch("app.endpoint.domain.httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.history = []  # No redirect history
            mock_response.url = "https://www.google.com"
            mock_get.return_value = mock_response

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="https://www.google.com") as ac:
                response = await ac.post("/domain/check-domain", json={"domain": "https://www.google.com"})

            data = response.json()
            assert response.status_code == 200
            assert data["redirected"] is False
            assert data["final_url"] == "https://www.google.com"
            assert data["redirect_chain"] == []
            assert data["http_status"] == 200
            assert data["is_live"] is True
            assert "Domain is live" in data["message"]