import pytest

@pytest.mark.asyncio
async def test_create_issue_requires_title(client):
    r = await client.post("/issues", json={})
    assert r.status_code == 422
