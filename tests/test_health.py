from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_metrics_returns_config(client):
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "default_mode" in data
    assert "tools_enabled" in data


@pytest.mark.asyncio
async def test_ready_endpoint_exists(client):
    # /ready may be degraded in test (no real DB), but must return a valid JSON body
    resp = await client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "database" in data
