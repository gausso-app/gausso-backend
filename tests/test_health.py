# ============================================================
# Gausso Backend - Sağlık Kontrolü Testi
# ============================================================

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_root_welcome_message():
    """Ana endpoint'in doğru karşılama mesajı döndürdüğünü test eder."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Gausso" in data["message"]


@pytest.mark.asyncio
async def test_health_check():
    """Sağlık kontrolü endpoint'inin çalıştığını test eder."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
