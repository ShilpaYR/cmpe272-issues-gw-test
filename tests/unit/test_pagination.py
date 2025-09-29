# tests/unit/test_pagination.py
import pytest
import respx
import httpx
from src.services.github import repo_url

@pytest.mark.asyncio
@respx.mock
async def test_list_issues_forwards_link_header(client):
    # Minimal issue JSON from GitHub
    gh_issue = {
        "number": 1,
        "html_url": "https://example/1",
        "state": "open",
        "title": "t",
        "body": None,
        "labels": [],
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
    }

    respx.get(repo_url("/issues")).mock(
        return_value=httpx.Response(
            200,
            headers={"Link": '<https://api.github.com/...&page=2>; rel="next"'},
            json=[gh_issue],
        )
    )

    r = await client.get("/issues")
    assert r.status_code == 200
    assert "Link" in r.headers
    assert 'rel="next"' in r.headers["Link"]
    data = r.json()
    assert isinstance(data, list) and data[0]["number"] == 1

