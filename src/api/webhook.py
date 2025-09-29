from fastapi import APIRouter, Request, Header, HTTPException, Response, Query
import hmac, hashlib, os, time

from ..models.events_store import save_event, last_events
from ..models.schemas import Event


import os
SECRET = (os.getenv("WEBHOOK_SECRET") or "").encode()

router = APIRouter(tags=["webhook"])

def verify_signature(raw: bytes, header: str | None) -> bool:
    if not header or not header.startswith("sha256="): return False
    sig = header.split("=",1)[1]
    mac = hmac.new(SECRET, raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(mac, sig)

@router.post("/webhook", status_code=204)
async def webhook(
    request: Request,
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_github_delivery: str = Header(..., alias="X-GitHub-Delivery"),
    x_hub_sig_256: str = Header(None, alias="X-Hub-Signature-256"),
):
    raw = await request.body()
    if not verify_signature(raw, x_hub_sig_256):
        raise HTTPException(status_code=401, detail="invalid signature")
    if x_github_event not in ("issues", "issue_comment", "ping"):
        raise HTTPException(status_code=400, detail="unknown event")

    payload = await request.json()
    action = payload.get("action")
    issue_num = None
    if "issue" in payload and isinstance(payload["issue"], dict):
        issue_num = payload["issue"].get("number")

    event_id = f"{x_github_delivery}:{x_github_event}:{action or ''}"
    save_event({
        "id": event_id,
        "event": x_github_event,
        "action": action,
        "issue_number": issue_num,
        "timestamp": payload.get("repository", {}).get("pushed_at") or str(int(time.time()))
    })
    # Fast ACK; any heavy work should be queued (not required here)
    return Response(status_code=204)

@router.get("/events", response_model=list[Event])
def get_events(limit: int = Query(default=50, ge=1, le=200)):
    return last_events(limit)


