# src/services/github.py
import os, time
from typing import Any, Dict, Optional, Tuple
import httpx
from fastapi import HTTPException

BASE = "https://api.github.com"

def _owner() -> str: return os.getenv("GITHUB_OWNER", "")
def _repo() -> str:  return os.getenv("GITHUB_REPO", "")
def _token() -> str: return os.getenv("GITHUB_TOKEN", "")

def _headers() -> Dict[str, str]:
    tok = _token()
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

def repo_url(path: str) -> str:
    return f"{BASE}/repos/{_owner()}/{_repo()}{path}"

def rate_limit_from(resp: httpx.Response) -> Tuple[Optional[int], Optional[int]]:
    remaining = resp.headers.get("X-RateLimit-Remaining")
    reset = resp.headers.get("X-RateLimit-Reset")
    return (int(remaining) if remaining is not None else None,
            int(reset) if reset is not None else None)

def to_labels_list(gh_issue: Dict[str, Any]) -> list[str]:
    return [lbl["name"] for lbl in gh_issue.get("labels", []) if isinstance(lbl, dict) and "name" in lbl]

def project_issue(gh_issue: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "number": gh_issue["number"],
        "html_url": gh_issue["html_url"],
        "state": gh_issue["state"],
        "title": gh_issue["title"],
        "body": gh_issue.get("body"),
        "labels": to_labels_list(gh_issue),
        "created_at": gh_issue["created_at"],
        "updated_at": gh_issue["updated_at"],
    }

async def gh_request(method: str, url: str, *, params=None, json=None) -> httpx.Response:
    if not _token():
        # Helpful message for devs/tests
        raise HTTPException(status_code=401, detail="Missing GITHUB_TOKEN environment variable")
    async with httpx.AsyncClient(timeout=15.0) as client:
        return await client.request(method, url, headers=_headers(), params=params, json=json)

def map_or_raise(resp: httpx.Response) -> None:
    if resp.status_code in (200, 201):
        return
    if resp.status_code == 304:
        raise HTTPException(status_code=304)
    if resp.status_code in (401, 403):
        # Special-case “rate limit exceeded” → 429
        text_lower = (resp.text or "").lower()
        if "rate limit" in text_lower:
            _, reset = rate_limit_from(resp)
            retry_after = max(1, (reset - int(time.time())) if reset else 30)
            raise HTTPException(status_code=429, detail=f"Rate limited; retry after {retry_after}s")
        raise HTTPException(status_code=401, detail="Unauthorized to GitHub (check token/scopes/repo selection)")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Issue not found")
    if resp.status_code == 422:
        try:
            details = resp.json()
        except Exception:
            details = {"message": resp.text}
        raise HTTPException(status_code=400, detail=details)
    if 500 <= resp.status_code < 600:
        raise HTTPException(status_code=503, detail="Upstream error from GitHub")
    raise HTTPException(status_code=resp.status_code, detail=resp.text)
