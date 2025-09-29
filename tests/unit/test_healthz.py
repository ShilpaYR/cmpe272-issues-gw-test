import pytest

@pytest.mark.asyncio
async def test_healthz_ok(client):
    r = await client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"ok": True}

