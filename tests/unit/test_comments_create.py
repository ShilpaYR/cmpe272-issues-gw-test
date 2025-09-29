import pytest
import respx
import httpx
from src.services.github import repo_url

@pytest.mark.asyncio
@respx.mock
async def test_add_comment_201(client):
    respx.post(repo_url("/issues/7/comments")).mock(
        return_value=httpx.Response(201, json={"id": 123, "body": "hi", "user": {"login": "me"},
                                               "created_at": "2025-01-01T00:00:00Z",
                                               "html_url": "https://x/y"})
    )
    r = await client.post("/issues/7/comments", json={"body": "hi"})
    assert r.status_code == 201
    assert r.json()["id"] == 123
