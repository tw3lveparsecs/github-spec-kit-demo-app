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

Expected: List of 3 pre-loaded scenarios (user-authentication, ecommerce-checkout, data-dashboard)

## Docker Development

### Using Docker Compose

```bash
docker-compose up --build
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
3. Open http://localhost:5000 when port forwarding starts
4. Select a demo scenario and explore!

The `.devcontainer/post-create.sh` script automatically:
- Installs Python dependencies
- Installs frontend dependencies
- Verifies installations

## Production Deployment

### Azure App Service

The application is deployed to Azure App Service using Bicep infrastructure-as-code.

#### Prerequisites

1. **Azure CLI** installed and authenticated
   ```bash
   az login
   az account set --subscription <your-subscription-id>
   ```

2. **Azure Resource Group** created
   ```bash
   az group create --name rg-speckit-demo-dev --location eastus
   ```

#### Deploy Infrastructure

```bash
# Deploy development environment
az deployment group create \
  --resource-group rg-speckit-demo-dev \
  --template-file infra/main.bicep \
  --parameters infra/parameters/dev.bicepparam
```

#### Deploy Application

```bash
# Package the application
zip -r app.zip backend frontend -x "*.pyc" -x "*__pycache__*"

# Deploy to App Service
az webapp deployment source config-zip \
  --resource-group rg-speckit-demo-dev \
  --name speckit-demo-dev-app \
  --src app.zip
```

#### GitHub Actions CI/CD

The repository includes GitHub Actions workflows for automated deployment:

1. **CI Workflow** (`.github/workflows/ci.yml`)
   - Runs on push to main/develop and PRs
   - Executes Black, mypy, flake8 checks
   - Runs pytest with coverage
   - Runs Playwright E2E tests
   - Performs security scanning with Bandit

2. **CD Workflow** (`.github/workflows/cd.yml`)
   - Deploys to development on main branch push
   - Manual production deployment with approval
   - Automatic health check verification

3. **Infrastructure Workflow** (`.github/workflows/infrastructure.yml`)
   - Manual trigger for infrastructure changes
   - What-if preview before deployment
   - Deploys Bicep templates to Azure

#### Required GitHub Secrets

Configure these secrets in your repository:

| Secret | Description |
|--------|-------------|
| `AZURE_CREDENTIALS_DEV` | Azure service principal for dev deployment |
| `AZURE_CREDENTIALS_PROD` | Azure service principal for prod deployment |

Create service principal:
```bash
az ad sp create-for-rbac --name "speckit-demo-deploy" \
  --role contributor \
  --scopes /subscriptions/<subscription-id>/resourceGroups/rg-speckit-demo-dev \
  --sdk-auth
```

See [infra/README.md](infra/README.md) for detailed infrastructure documentation.

## Health Check Validation

The application includes a health endpoint at `/api/health` that returns:
- `status`: "healthy" when running
- `timestamp`: Current UTC time
- `version`: Application version

Use this for:
- Docker healthchecks
- Azure App Service health probes
- Load balancer health monitoring
- CI/CD pipeline validation

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
