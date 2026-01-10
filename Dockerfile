# Production Dockerfile
# Keeps the same on-disk layout as the repo (backend/ + frontend/) so the containerized app
# behaves the same as local development.
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application code (preserve repo layout)
COPY backend/src /app/backend/src
COPY backend/data /app/backend/data
COPY frontend/src /app/frontend/src

# Optional: include specs/constitution content if referenced by future scenarios
COPY specs /app/specs
COPY .specify /app/.specify

# Environment
ENV FLASK_APP=src/app.py
ENV PYTHONPATH=/app/backend/src:$PYTHONPATH
ENV PORT=5000

EXPOSE 5000

# Health check (supports PORT override)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD sh -c 'curl -fsS "http://localhost:${PORT}/api/health" >/dev/null || exit 1'

# Run with gunicorn
WORKDIR /app/backend
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 4 --timeout 120 src.app:app"]
