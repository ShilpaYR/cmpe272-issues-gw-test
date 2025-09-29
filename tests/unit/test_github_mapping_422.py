import pytest
import respx
import httpx
from src.services.github import repo_url

@pytest.mark.asyncio
@respx.mock
async def test_update_issue_422_maps_to_400(client):
    respx.patch(repo_url("/issues/9")).mock(
        return_value=httpx.Response(422, json={"message": "Validation Failed"})
    )
    r = await client.patch("/issues/9", json={"title": "x"})  # valid body -> reaches GitHub 422
    assert r.status_code == 400
