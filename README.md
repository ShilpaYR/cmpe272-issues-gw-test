
# GitHub Issues Gateway

A thin HTTP service that wraps the **GitHub REST API for Issues** for a single repository, exposing clean endpoints, validating webhooks, and providing an OpenAPI 3.1 contract.

---

## Features
- Issue CRUD (Create, Read, Update/Close/Open) and Comments
- Webhook receiver with HMAC SHA-256 signature verification
- Stores webhook deliveries in SQLite (idempotent)
- OpenAPI 3.1 spec (`/openapi.yaml`)
- Unit + integration tests with coverage >80%
- Dockerized (dev & prod), VS Code Dev Container ready
- Observability: structured logs, `/healthz` endpoint

---

## 1. Local Development / Running

### Requirements
- Python 3.11+
- GitHub Fine-Grained PAT (scoped to your repo, Issues: Read/Write)
- Docker Desktop (for container runs)
- ngrok (or smee) for webhook testing

### Setup
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```ini
GITHUB_TOKEN=ghp_xxx                # your PAT
GITHUB_OWNER=your-github-username
GITHUB_REPO=cmpe272-issues-gw-test  # repo name only
WEBHOOK_SECRET=supersecretstring
PORT=8080
```

Run the server:
```bash
uvicorn src.app:app --host 0.0.0.0 --port 8080 --reload
```

Check:
- http://localhost:8080/healthz → `{"ok": true}`
- http://localhost:8080/docs (FastAPI Swagger UI)
- http://localhost:8080/openapi.yaml (contract file)

---

## 2. Running with Docker

### Build & Run (Dev Hot-Reload)
```bash
docker compose -f docker-compose.dev.yml up --build
```
Now edit files locally → auto-reload in container.

### Build & Run (Prod-like)
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Stop
```bash
docker compose -f docker-compose.dev.yml down
```

OR

### Using Make file (Recommended)
(Dev Hot-Reload)
```bash
make dev-up
```
```bash
make dev-down
```

(Prod)
```bash
make prod-up
```
```bash
make prod-down
```


---

## 3. API Usage (Examples with HTTPie)

### Create an Issue
```bash
http POST :8080/issues title="Bug: save fails" body="Steps..." labels:='["bug"]'
```

### List Issues
```bash
http GET :8080/issues state==open page==1 per_page==10
```

### Get Single Issue
```bash
http GET :8080/issues/1
```

### Update / Close Issue
```bash
http PATCH :8080/issues/1 state="closed"
```

### Add Comment
```bash
http POST :8080/issues/1/comments body="Thanks!"
```

### Get Events (debugging webhook deliveries)
```bash
http GET :8080/events limit==5
```

---

## 4. Webhook Setup

1. Run server locally:
   ```bash
   uvicorn src.app:app --host 0.0.0.0 --port 8080
   ```
2. Start tunnel:
   ```bash
   ngrok http 8080
   ```
   Copy the HTTPS URL.
3. In your repo → **Settings → Webhooks → Add Webhook**:
   - Payload URL: `https://<ngrok-id>.ngrok.app/webhook`
   - Content type: `application/json`
   - Secret: **must match `WEBHOOK_SECRET` in `.env`**
   - Events: Issues + Issue comments (and Ping)
4. Create or comment on an issue in GitHub.
5. Verify event is stored:
   ```bash
   http GET :8080/events
   ```

---

## 5. OpenAPI Contract

Contract file: [`openapi.yaml`](./openapi.yaml)

Download from the service:
```bash
http GET :8080/openapi.yaml
```

Validate:
```bash
openapi-spec-validator openapi.yaml
```

---

## 6. Testing

### Unit Tests and Coverage
```bash
make test
```
Target: ≥80% (current ~90%+)

### Integration Tests (require PAT, server + tunnel)
```bash
set -a
source .env
set +a

make integration
```

---
