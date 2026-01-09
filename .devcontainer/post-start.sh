#!/bin/bash
set -e

echo "▶️  Codespaces start: ensuring backend is running..."

HEALTH_URL="http://localhost:5000/api/health"

if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
  echo "✅ Backend already running on :5000"
  exit 0
fi

echo "🚀 Starting Flask backend on :5000 (background)"
cd /workspace/backend

export PYTHONPATH="/workspace/backend/src:${PYTHONPATH}"
export FLASK_APP="src/app.py"
export FLASK_ENV="development"
export FLASK_DEBUG="1"

nohup python -m flask run --host=0.0.0.0 --port=5000 > /tmp/flask.log 2>&1 &

# Give it a moment to come up; Codespaces will auto-forward the port.
sleep 1

if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
  echo "✅ Backend started: $HEALTH_URL"
else
  echo "⚠️  Backend is still starting. Check /tmp/flask.log if it doesn't come up."
fi
