# tests/unit/test_signature.py
import hmac
import hashlib
import json
import os
import pytest

SECRET = (os.getenv("WEBHOOK_SECRET") or "supersecretstring").encode()

def sign(body: bytes) -> str:
    return "sha256=" + hmac.new(SECRET, body, hashlib.sha256).hexdigest()

@pytest.mark.asyncio
async def test_webhook_valid_signature(client):
    payload = json.dumps({"action": "opened", "issue": {"number": 1}}).encode()
    headers = {
        "X-GitHub-Event": "issues",
        "X-GitHub-Delivery": "d1",
        "X-Hub-Signature-256": sign(payload),
    }
    r = await client.post("/webhook", content=payload, headers=headers)
    assert r.status_code == 204

@pytest.mark.asyncio
async def test_webhook_invalid_signature(client):
    payload = b"{}"
    headers = {
        "X-GitHub-Event": "issues",
        "X-GitHub-Delivery": "d2",
        "X-Hub-Signature-256": "sha256=badsignature",
    }
    r = await client.post("/webhook", content=payload, headers=headers)
    assert r.status_code == 401
