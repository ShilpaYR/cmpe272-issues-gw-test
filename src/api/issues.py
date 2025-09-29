
from typing import Optional

from fastapi import APIRouter, Response, HTTPException, Query

from ..services.github import gh_request, repo_url, project_issue, map_or_raise
from ..models.schemas import (
    Issue,
    CreateIssueRequest,
    UpdateIssueRequest,
    Comment,
    CreateCommentRequest,
)

# IMPORTANT: this symbol must exist for app.py to import
router = APIRouter(prefix="", tags=["issues"])


@router.post("/issues", status_code=201, response_model=Issue)
async def create_issue(req: CreateIssueRequest, response: Response):
    payload = {"title": req.title}
    if req.body is not None:
        payload["body"] = req.body
    if req.labels:
        payload["labels"] = req.labels

    gh = await gh_request("POST", repo_url("/issues"), json=payload)
    map_or_raise(gh)
    data = gh.json()
    response.headers["Location"] = f"/issues/{data['number']}"
    return project_issue(data)


@router.get("/issues", response_model=list[Issue])
async def list_issues(
    state: str = Query(default="open", pattern="^(open|closed|all)$"),
    labels: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=30, ge=1, le=100),
    response: Response = None,
):
    params = {"state": state, "page": page, "per_page": per_page}
    if labels:
        params["labels"] = labels
    gh = await gh_request("GET", repo_url("/issues"), params=params)
    map_or_raise(gh)
    # forward pagination headers if present
    for h in ("Link", "X-RateLimit-Remaining", "X-RateLimit-Reset"):
        if gh.headers.get(h):
            response.headers[h] = gh.headers[h]
    return [project_issue(x) for x in gh.json()]


@router.get("/issues/{number}", response_model=Issue)
async def get_issue(number: int):
    gh = await gh_request("GET", repo_url(f"/issues/{number}"))
    map_or_raise(gh)
    return project_issue(gh.json())


@router.patch("/issues/{number}", response_model=Issue)
async def update_issue(number: int, req: UpdateIssueRequest):
    body = req.model_dump(exclude_unset=True)
    if "state" in body and body["state"] not in ("open", "closed"):
        raise HTTPException(400, "state must be 'open' or 'closed'")
    gh = await gh_request("PATCH", repo_url(f"/issues/{number}"), json=body)
    map_or_raise(gh)
    return project_issue(gh.json())


@router.post("/issues/{number}/comments", status_code=201, response_model=Comment)
async def add_comment(number: int, req: CreateCommentRequest):
    gh = await gh_request("POST", repo_url(f"/issues/{number}/comments"), json={"body": req.body})
    map_or_raise(gh)
    return gh.json()
