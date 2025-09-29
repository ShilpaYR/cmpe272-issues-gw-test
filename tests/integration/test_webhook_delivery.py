# tests/integration/test_webhook_delivery.py
import os
import time
import pytest
import httpx
import asyncio

pytestmark = pytest.mark.integration

# Local service base URL (talks to your app)
BASE = os.getenv("SERVICE_BASE_URL", "http://localhost:8080")
# GitHub API for triggering events
GH_BASE = "https://api.github.com"

REQUIRED_VARS = ("GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO", "WEBHOOK_SECRET")
missing = [v for v in REQUIRED_VARS if not os.getenv(v)]

@pytest.mark.skipif(missing, reason=f"Set env vars: {', '.join(REQUIRED_VARS)}")
@pytest.mark.asyncio
async def test_webhook_event_is_persisted():
    """
    Pre-reqs:
      - uvicorn running on localhost:8080
      - public tunnel forwarding to /webhook and configured in GitHub repo
    Steps:
      1) Create a real GitHub issue via GitHub API -> triggers webhook
      2) Poll /events until event appears
    """
    token = os.environ["GITHUB_TOKEN"]
    owner = os.environ["GITHUB_OWNER"]
    repo  = os.environ["GITHUB_REPO"]

    issue_title = f"WH ITEST {int(time.time())}"

    async with httpx.AsyncClient(timeout=20.0) as http:
        # 1) Create real issue on GitHub (this triggers a webhook delivery)
        r = await http.post(
            f"{GH_BASE}/repos/{owner}/{repo}/issues",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={"title": issue_title, "body": "webhook integration test"},
        )
        assert r.status_code == 201, r.text
        num = r.json()["number"]

        # 2) Poll your local service /events until it sees the delivery
        #    (GitHub sends within a second, but we allow a short window)
        deadline = time.time() + 25
        found = False
        while time.time() < deadline:
            events = (await http.get(f"{BASE}/events?limit=50")).json()
            # Normalize titles might not be stored; we rely on issue number + event type
            found = any(e.get("event") == "issues" and e.get("issue_number") == num for e in events)
            if found:
                break
            await asyncio.sleep(1)

        assert found, "Did not observe webhook event in /events within the timeout window"
