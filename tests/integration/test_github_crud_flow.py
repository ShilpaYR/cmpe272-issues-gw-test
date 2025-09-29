# tests/integration/test_github_crud_flow.py
import os
import time
import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app

# Only run when we actually want to hit GitHub.
pytestmark = pytest.mark.integration

REQUIRED_VARS = ("GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO")
missing = [v for v in REQUIRED_VARS if not os.getenv(v)]

@pytest.mark.skipif(missing, reason=f"Set env vars: {', '.join(REQUIRED_VARS)}")
@pytest.mark.asyncio
async def test_crud_and_comments_against_github():
    # Run the app in-process; it will use real GitHub via your env token.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1) Create issue
        title = f"ITEST {int(time.time())}"
        body = "Integration test issue"
        r = await client.post("/issues", json={"title": title, "body": body, "labels": ["test"]})
        assert r.status_code == 201, r.text
        created = r.json()
        num = created["number"]

        # 2) GET that issue
        r = await client.get(f"/issues/{num}")
        assert r.status_code == 200, r.text
        got = r.json()
        assert got["title"] == title

        # 3) PATCH title/body
        r = await client.patch(f"/issues/{num}", json={"title": title + " (edited)", "body": body + " ++"})
        assert r.status_code == 200, r.text
        assert r.json()["title"].endswith("(edited)")

        # 4) Close and reopen
        r = await client.patch(f"/issues/{num}", json={"state": "closed"})
        assert r.status_code == 200, r.text
        assert r.json()["state"] == "closed"

        r = await client.patch(f"/issues/{num}", json={"state": "open"})
        assert r.status_code == 200, r.text
        assert r.json()["state"] == "open"

        # 5) Add comment
        r = await client.post(f"/issues/{num}/comments", json={"body": "Thanks for testing!"})
        assert r.status_code == 201, r.text
        comment = r.json()
        assert "id" in comment and comment["body"] == "Thanks for testing!"
