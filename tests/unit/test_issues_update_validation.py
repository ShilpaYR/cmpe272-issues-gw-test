import pytest

@pytest.mark.asyncio
async def test_update_issue_rejects_bad_state(client):
    r = await client.patch("/issues/1", json={"state": "maybe"})
    assert r.status_code == 400
