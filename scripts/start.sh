#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-5000}"
NO_INSTALL=0
USE_DOCKER=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --docker) USE_DOCKER=1; shift ;;
    --no-install) NO_INSTALL=1; shift ;;
    --port) PORT="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: ./scripts/start.sh [--docker] [--no-install] [--port 5000]"
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 1
      ;;
  esac
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
backend_dir="$repo_root/backend"
venv_dir="$backend_dir/.venv"

info() { echo "[start] $*"; }

if [[ $USE_DOCKER -eq 1 ]]; then
  info "Starting via Docker Compose..."
  cd "$repo_root"
  if command -v docker >/dev/null 2>&1; then
    if docker compose version >/dev/null 2>&1; then
      exec docker compose up --build
    fi
  fi
  if command -v docker-compose >/dev/null 2>&1; then
    exec docker-compose up --build
  fi
  echo "Docker is not installed or not on PATH." >&2
  exit 1
fi

info "Repo root: $repo_root"
info "Backend dir: $backend_dir"

python_cmd=""
if command -v python3 >/dev/null 2>&1; then
  python_cmd="python3"
elif command -v python >/dev/null 2>&1; then
  python_cmd="python"
else
  echo "Python is not installed or not on PATH." >&2
  exit 1
fi

if [[ ! -d "$venv_dir" ]]; then
  info "Creating virtual environment in backend/.venv..."
  cd "$backend_dir"
  "$python_cmd" -m venv .venv
fi

# shellcheck disable=SC1091
source "$venv_dir/bin/activate"

if [[ $NO_INSTALL -eq 0 ]]; then
  info "Installing backend dependencies..."
  cd "$backend_dir"
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
  if [[ -f "$backend_dir/requirements-dev.txt" ]]; then
    python -m pip install -r requirements-dev.txt
  fi
fi

info "Starting backend on port $PORT..."
export PYTHONPATH="$backend_dir/src"
export PORT="$PORT"

cd "$backend_dir"
exec python run_dev.py
