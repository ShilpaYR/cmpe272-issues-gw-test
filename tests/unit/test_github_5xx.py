import pytest
import respx
import httpx
from src.services.github import repo_url

@pytest.mark.asyncio
@respx.mock
async def test_get_issue_5xx_maps_to_503(client):
    respx.get(repo_url("/issues/3")).mock(
        return_value=httpx.Response(502, text="bad gateway")
    )
    r = await client.get("/issues/3")
    assert r.status_code == 503
