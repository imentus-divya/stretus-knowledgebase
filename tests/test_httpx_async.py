"""API smoke test using httpx AsyncClient (lifespan via asgi-lifespan)."""

from __future__ import annotations

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from kb_server.main import create_app


@pytest.mark.asyncio
async def test_health_async_client(settings):
    app = create_app(settings)
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            r = await ac.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
