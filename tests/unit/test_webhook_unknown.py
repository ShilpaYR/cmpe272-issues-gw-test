import pytest

@pytest.mark.asyncio
async def test_webhook_unknown_event_400(client):
    payload = b'{}'
    headers = {
        "X-GitHub-Event": "push",           # not allowed by service
        "X-GitHub-Delivery": "dX",
        "X-Hub-Signature-256": "sha256=" + "0"*64,  # bad sig -> 401 wins first
    }
    r = await client.post("/webhook", content=payload, headers=headers)
    assert r.status_code == 401  # signature check happens before event validation
