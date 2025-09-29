import os, logging, uuid
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from fastapi import FastAPI

from .api.issues import router as issues_router
from .api.webhook import router as webhook_router
from .api.health import router as health_router

app = FastAPI(title="GitHub Issues Gateway", version="1.0.0")

@app.get("/openapi.yaml", include_in_schema=False)
def download_spec():
    # This points one folder up from src/ to find openapi.yaml in the repo root
    path = Path(__file__).resolve().parent.parent / "openapi.yaml"
    return FileResponse(path, media_type="application/yaml", filename="openapi.yaml")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = req_id
        return response

app.add_middleware(RequestIDMiddleware)

@app.exception_handler(Exception)
async def unhandled_exc(_, exc: Exception):
    # keep generic in prod; include more details in dev if you want
    return JSONResponse(status_code=500, content={"error": "internal_error"})

app.include_router(issues_router)
app.include_router(webhook_router)
app.include_router(health_router)
app.state.webhook_secret = os.getenv("WEBHOOK_SECRET", "")
