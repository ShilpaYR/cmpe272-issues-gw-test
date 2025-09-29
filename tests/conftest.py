# tests/conftest.py
import os, warnings
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed database")


# --- Set env BEFORE importing the app so services/github.py picks them up ---
os.environ.setdefault("GITHUB_TOKEN", "test-token")
os.environ.setdefault("GITHUB_OWNER", "owner")
os.environ.setdefault("GITHUB_REPO", "repo")
os.environ.setdefault("WEBHOOK_SECRET", "supersecretstring")

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from src.app import app

@pytest_asyncio.fixture
async def client():
    # No lifespan arg (works across httpx versions)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
