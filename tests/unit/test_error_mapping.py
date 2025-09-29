# tests/unit/test_error_mapping.py
import pytest
import respx
import httpx
from src.services.github import repo_url

@pytest.mark.asyncio
@respx.mock
async def test_get_issue_404_maps_to_404(client):
    # Mock the upstream GitHub call our service will make
    respx.get(repo_url("/issues/999")).mock(return_value=httpx.Response(404))

    r = await client.get("/issues/999")
    assert r.status_code == 404
