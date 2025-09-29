import pytest
import respx
import httpx
from src.services.github import repo_url

@pytest.mark.asyncio
@respx.mock
async def test_create_issue_sets_location_and_maps_fields(client):
    gh_issue = {
        "number": 42,
        "html_url": "https://github.com/owner/repo/issues/42",
        "state": "open",
        "title": "Bug: 500",
        "body": "Steps",
        "labels": [{"name": "bug"}],
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }
    respx.post(repo_url("/issues")).mock(
        return_value=httpx.Response(201, json=gh_issue)
    )

    r = await client.post("/issues", json={"title": "Bug: 500", "body": "Steps", "labels": ["bug"]})
    assert r.status_code == 201
    assert r.headers.get("Location") == "/issues/42"
    data = r.json()
    assert data["number"] == 42 and data["labels"] == ["bug"] and data["title"] == "Bug: 500"
