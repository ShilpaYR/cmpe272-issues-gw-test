FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src ./src
COPY openapi.yaml .
COPY README.md ./README.md

RUN useradd -ms /bin/bash appuser
USER appuser

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]
