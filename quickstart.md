# Quickstart Guide

## Prerequisites

- Python 3.11+
- pip (Python package manager)

## Local Development Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd github-spec-kit-demo
```

### Option A: Use the Startup Script (Recommended)

This repo includes cross-OS startup scripts:

- Windows (PowerShell): `./scripts/start.ps1`
- macOS/Linux (Bash): `./scripts/start.sh`

They will create `backend/.venv` (if missing), install dependencies, and start the backend on port 5000.

Windows PowerShell:

```powershell
./scripts/start.ps1
```

macOS/Linux:

```bash
chmod +x ./scripts/start.sh
./scripts/start.sh
```

### Option B: Manual Setup

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Run the Application

```bash
# Set Python path
export PYTHONPATH=$PWD/src  # Linux/Mac
$env:PYTHONPATH="$PWD\src"  # Windows PowerShell

# Start Flask server
python -m flask run --host=0.0.0.0 --port=5000
```

### 4. Verify Health

Open your browser to http://localhost:5000

Or test with curl:

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-12-05T...",
  "version": "1.0.0"
}
```

### 5. Test Scenarios Endpoint

```bash
curl http://localhost:5000/api/scenarios
```

Expected: List of available scenarios (currently includes `ecommerce-checkout`)

## Docker Development

### Using Docker Compose

```bash
docker compose up --build
```

Access at http://localhost:5000

### Using Dockerfile.dev

```bash
docker build -f Dockerfile.dev -t speckit-demo:dev .
docker run -p 5000:5000 speckit-demo:dev
```

## GitHub Codespaces

1. Click "Code" → "Codespaces" → "Create codespace on main"
2. Wait ~60s for setup to complete
3. Codespaces will auto-start the backend and auto-forward port 5000 (it should open in your browser)
4. Select a demo scenario and explore!

The `.devcontainer/post-create.sh` script automatically:

- Installs Python dependencies
- Installs frontend dependencies
- Verifies installations

The `.devcontainer/post-start.sh` script automatically starts the Flask backend.

## Deployment

This repository currently documents **local development, Docker, and Codespaces**.
Cloud deployment instructions and automation (e.g., cloud CLI install steps, deployment pipelines) have been removed because they are no longer used.

## Health Check Validation

The application includes a health endpoint at `/api/health` that returns:

- `status`: "healthy" when running
- `timestamp`: Current UTC time
- `version`: Application version

Use this for:

- Docker healthchecks
- Load balancer health monitoring
- Local smoke testing

## Troubleshooting

**Issue**: Flask app not starting

- Verify PYTHONPATH is set to `backend/src`
- Check requirements.txt dependencies installed
- Verify Python 3.11+ is active

**Issue**: 404 on API endpoints

- Ensure Flask server is running on port 5000
- Check that routes are registered (should see logs on startup)
- Verify no other process is using port 5000

**Issue**: Scenarios not loading

- Check `backend/data/scenarios/` contains JSON files
- Verify file permissions allow reading
- Check Flask logs for ScenarioLoader errors

## Development Tools

### Linting

```bash
cd backend
flake8 src/
```

### Type Checking

```bash
mypy src/
```

### Code Formatting

```bash
black src/
```

### Run Tests

```bash
pytest tests/
pytest --cov=src tests/  # With coverage
```

### Frontend Tests

```bash
cd frontend
npx playwright test
```
