import pytest
import respx
import httpx
import time
from src.services.github import repo_url

@pytest.mark.asyncio
@respx.mock
async def test_list_issues_rate_limited_becomes_429(client):
    future_reset = int(time.time()) + 30
    respx.get(repo_url("/issues")).mock(
        return_value=httpx.Response(403, text="API rate limit exceeded", headers={"X-RateLimit-Reset": str(future_reset)})
    )
    r = await client.get("/issues")
    assert r.status_code == 429
