# Quickstart: GitHub Spec Kit Demo Application

Get the demo app running locally in under 5 minutes.

## Prerequisites

- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **Git**: For cloning the repository
- **VS Code** (optional): Recommended for best development experience
- **Docker** (optional): For container-based development

## Local Development

### Option 1: GitHub Codespaces (Fastest) ⚡

Click the green "Code" button → "Codespaces" → "Create codespace on main"

The environment auto-configures in ~60 seconds. Once ready:

```bash
# Backend already running on http://localhost:5000
# Frontend served from backend/static/

# Open in browser
open http://localhost:5000
```

### Option 2: Local Setup (Traditional)

**Step 1: Clone and navigate**

```bash
git clone https://github.com/YOUR_ORG/speckit-demo-app.git
cd speckit-demo-app
```

**Step 2: Set up Python environment**

```bash
# Create virtual environment
python3 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt
```

**Step 3: Run the application**

```bash
# Start Flask dev server
cd backend
flask run

# App runs at http://localhost:5000
```

**Step 4: Open in browser**

```bash
# macOS
open http://localhost:5000

# Windows
start http://localhost:5000

# Linux
xdg-open http://localhost:5000
```

You should see the GitHub Spec Kit Demo home screen with three sample scenarios!

## Verify Installation

### Health Check

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-11-23T12:00:00Z",
  "version": "1.0.0"
}
```

### List Demo Scenarios

```bash
curl http://localhost:5000/api/scenarios
```

You should see 3 pre-loaded scenarios: User Authentication, Ecommerce Checkout, Data Dashboard.

## Development Workflow

### Run Tests

```bash
# All tests (unit + integration + e2e)
pytest

# Unit tests only
pytest tests/unit/

# With coverage report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Code Quality Checks

```bash
# Format code with Black
black src/ tests/

# Type checking with mypy
mypy src/

# Linting
flake8 src/ tests/
```

### Run Frontend Tests

```bash
cd frontend
npm install  # First time only
npm test
```

## Project Structure

```
speckit-demo-app/
├── backend/
│   ├── src/               # Python source code
│   │   ├── models/        # Data models
│   │   ├── services/      # Business logic
│   │   └── api/           # Flask routes
│   ├── tests/             # Backend tests
│   ├── data/              # Pre-loaded scenarios
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── js/            # JavaScript source
│   │   └── css/           # Stylesheets
│   └── tests/             # Frontend tests
└── .devcontainer/         # Codespaces config
```

## Using the Demo App

### 1. Select a Scenario

- Home screen shows 3 pre-loaded scenarios
- Click any scenario card to begin

### 2. Run the Workflow

- Click "Run /speckit.specify" to generate spec.md
- Watch the animated typing effect (realistic demo!)
- Click "Next: Clarify" to proceed
- Answer clarification questions or skip
- Continue through plan → tasks → implement

### 3. View Generated Artifacts

- Click "View Files" panel on right
- See spec.md, plan.md, tasks.md with syntax highlighting
- Expand/collapse sections

### 4. Constitution Demo

- Click "Constitution" tab
- See all four principles
- Click "Show Enforcement" to see checks in action
- Violations appear with warning badges

### 5. Reset Demo

- Click "Reset Demo" button (top right)
- Confirm reset action
- Returns to clean initial state (<5 seconds)

### 6. Create Custom Scenario

- Click "Create Custom"
- Enter feature description
- Select domain (security, ecommerce, etc.)
- Click "Generate Demo"
- Workflow simulates with your input!

## Troubleshooting

### Port 5000 Already in Use

**Solution**: Use a different port

```bash
flask run --port 5001
```

### Module Not Found Errors

**Solution**: Ensure virtual environment is activated

```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Frontend Assets Not Loading

**Solution**: Clear browser cache or try incognito mode

```bash
# Hard refresh
Cmd+Shift+R (macOS)
Ctrl+Shift+R (Windows/Linux)
```

### Tests Failing

**Solution**: Install dev dependencies

```bash
pip install -r backend/requirements-dev.txt
```

## Deployment

Cloud deployment instructions and automated deployment workflows are intentionally omitted from this quickstart.

If you need to deploy this demo, treat it like any containerized Flask app:

- build the container image from the repo root
- run it behind your preferred hosting platform / reverse proxy

## Configuration

### Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Flask configuration
FLASK_APP=src/app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Demo configuration
MAX_CUSTOM_SCENARIOS=10
ANIMATION_SPEED_CPS=50
CACHE_TIMEOUT_SECONDS=3600
```

## Performance Tuning

### Backend Optimization

```python
# In src/app.py

# Enable response compression
from flask_compress import Compress
Compress(app)

# Configure caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.cached(timeout=3600)
def get_scenarios():
    # Cached for 1 hour
    pass
```

### Frontend Optimization

```javascript
// Enable service worker for offline capability
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js");
}

// Lazy load demo scenarios
import("./components/scenario-selector.js").then((module) => {
  module.initialize();
});
```

## Next Steps

- **Customize scenarios**: Edit JSON files in `backend/data/scenarios/`
- **Modify constitution**: Update `.specify/memory/constitution.md`
- **Add presenter notes**: Extend data models with talking points
- **Brand customization**: Update Primer CSS variables in `frontend/src/css/`
- **Run at conference**: Run locally or host on your preferred platform

## Getting Help

- **Documentation**: See `/specs/001-speckit-demo-app/` for full design docs
- **Issues**: Open GitHub issue with `[demo-app]` prefix
- **Constitution**: Review `.specify/memory/constitution.md` for quality standards

## Quick Reference

| Command               | Purpose          |
| --------------------- | ---------------- |
| `flask run`           | Start dev server |
| `pytest`              | Run tests        |
| `black src/`          | Format code      |
| `mypy src/`           | Type check       |
| `curl /api/health`    | Health check     |
| `curl /api/scenarios` | List scenarios   |

## Demo Checklist

Before presenting:

- [ ] App running locally and accessible in browser
- [ ] All three sample scenarios load
- [ ] Constitution tab displays four principles
- [ ] Reset button returns to clean state (<5 seconds)
- [ ] Custom scenario creation works
- [ ] Presenter notes toggle functions (if implemented)
- [ ] Browser is in full-screen mode (F11)
- [ ] Screen resolution set to 1920x1080 or higher
- [ ] Backup plan if internet drops (offline mode enabled)

**You're ready to demo!** 🚀
