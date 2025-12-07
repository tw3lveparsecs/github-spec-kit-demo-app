# Production Dockerfile for Azure App Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/src ./src
COPY backend/data ./data

# Copy frontend static files
COPY frontend/src ./frontend/src

# Set environment variables
ENV FLASK_APP=src/app.py
ENV PYTHONPATH=/app/src:$PYTHONPATH
ENV PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run Flask with gunicorn for production
RUN pip install --no-cache-dir gunicorn

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "src.app:app"]
