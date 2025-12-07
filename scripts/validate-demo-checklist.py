#!/usr/bin/env python3
"""
Demo Checklist Validation Script (T135)

Validates that all demo features work correctly by running through
the quickstart.md checklist items programmatically.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen, Request


BASE_URL = "http://localhost:5000"
TIMEOUT = 5  # seconds


class ChecklistValidator:
    """Validates demo checklist items."""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def check(self, name: str, condition: bool, details: str = ""):
        """Record a check result."""
        status = "✅ PASS" if condition else "❌ FAIL"
        self.results.append((name, condition, details))
        if condition:
            self.passed += 1
        else:
            self.failed += 1
        print(f"{status}: {name}")
        if details and not condition:
            print(f"       {details}")
    
    def api_request(self, endpoint: str, method: str = "GET", data: dict = None) -> tuple:
        """Make an API request and return (success, response_dict, elapsed_ms)."""
        url = f"{BASE_URL}{endpoint}"
        try:
            start = time.time()
            
            if data:
                req = Request(url, method=method,
                             data=json.dumps(data).encode(),
                             headers={"Content-Type": "application/json"})
            else:
                req = Request(url, method=method)
            
            with urlopen(req, timeout=TIMEOUT) as response:
                elapsed = (time.time() - start) * 1000
                body = json.loads(response.read().decode())
                return True, body, elapsed
        except URLError as e:
            return False, str(e), 0
        except json.JSONDecodeError:
            return False, "Invalid JSON response", 0
        except Exception as e:
            return False, str(e), 0


def check_file_exists(path: Path, name: str) -> bool:
    """Check if a required file exists."""
    return path.exists()


def main():
    """Run demo checklist validation."""
    print("=" * 60)
    print("DEMO CHECKLIST VALIDATION (T135)")
    print("=" * 60)
    print()
    
    validator = ChecklistValidator()
    repo_root = Path(__file__).parent.parent
    
    # Section 1: Project Structure
    print("📂 PROJECT STRUCTURE")
    print("-" * 40)
    
    validator.check(
        "Backend directory exists",
        check_file_exists(repo_root / "backend", "backend")
    )
    validator.check(
        "Frontend directory exists",
        check_file_exists(repo_root / "frontend", "frontend")
    )
    validator.check(
        "Infrastructure directory exists",
        check_file_exists(repo_root / "infra", "infra")
    )
    validator.check(
        "Docker Compose file exists",
        check_file_exists(repo_root / "docker-compose.yml", "docker-compose.yml")
    )
    validator.check(
        "GitHub workflows directory exists",
        check_file_exists(repo_root / ".github" / "workflows", "workflows")
    )
    print()
    
    # Section 2: Backend Files
    print("🐍 BACKEND FILES")
    print("-" * 40)
    
    validator.check(
        "Flask app.py exists",
        check_file_exists(repo_root / "backend" / "src" / "app.py", "app.py")
    )
    validator.check(
        "API routes exist",
        check_file_exists(repo_root / "backend" / "src" / "api" / "routes.py", "routes.py")
    )
    validator.check(
        "Scenarios data exists",
        check_file_exists(repo_root / "backend" / "data" / "scenarios", "scenarios")
    )
    validator.check(
        "Presenter notes data exists",
        check_file_exists(repo_root / "backend" / "data" / "presenter-notes", "presenter-notes")
    )
    validator.check(
        "Requirements file exists",
        check_file_exists(repo_root / "backend" / "requirements.txt", "requirements.txt")
    )
    print()
    
    # Section 3: Frontend Files
    print("🌐 FRONTEND FILES")
    print("-" * 40)
    
    validator.check(
        "index.html exists",
        check_file_exists(repo_root / "frontend" / "src" / "index.html", "index.html")
    )
    validator.check(
        "Main JavaScript exists",
        check_file_exists(repo_root / "frontend" / "src" / "js" / "main.js", "main.js")
    )
    validator.check(
        "Service worker exists",
        check_file_exists(repo_root / "frontend" / "src" / "sw.js", "sw.js")
    )
    validator.check(
        "Main CSS exists",
        check_file_exists(repo_root / "frontend" / "src" / "css" / "main.css", "main.css")
    )
    print()
    
    # Section 4: API Endpoints (requires running server)
    print("🔌 API ENDPOINTS (requires server at localhost:5000)")
    print("-" * 40)
    
    # Health check
    success, response, elapsed = validator.api_request("/api/health")
    validator.check(
        "Health endpoint responds",
        success and isinstance(response, dict) and response.get("status") == "healthy",
        f"Response: {response}"
    )
    
    # Scenarios endpoint
    success, response, elapsed = validator.api_request("/api/scenarios")
    has_three_scenarios = success and isinstance(response, list) and len(response) >= 3
    validator.check(
        "Scenarios endpoint returns 3+ scenarios",
        has_three_scenarios,
        f"Got {len(response) if isinstance(response, list) else 0} scenarios"
    )
    
    # Constitution endpoint
    success, response, elapsed = validator.api_request("/api/constitution")
    validator.check(
        "Constitution endpoint responds",
        success and isinstance(response, dict),
        f"Response type: {type(response)}"
    )
    
    # Presenter notes endpoint
    success, response, elapsed = validator.api_request("/api/presenter-notes")
    validator.check(
        "Presenter notes endpoint responds",
        success,
        f"Response: {response}"
    )
    print()
    
    # Section 5: Demo Scenarios
    print("🎭 DEMO SCENARIOS")
    print("-" * 40)
    
    scenario_ids = ["user-authentication", "ecommerce-checkout", "data-dashboard"]
    for scenario_id in scenario_ids:
        success, response, elapsed = validator.api_request(f"/api/scenarios/{scenario_id}")
        validator.check(
            f"Scenario '{scenario_id}' loads",
            success and isinstance(response, dict) and "id" in response,
            f"Response: {response}"
        )
    print()
    
    # Section 6: Workflow Operations
    print("⚙️ WORKFLOW OPERATIONS")
    print("-" * 40)
    
    # Create a workflow session
    success, response, elapsed = validator.api_request(
        "/api/workflow/user-authentication/start",
        method="POST"
    )
    has_session = success and isinstance(response, dict)
    validator.check(
        "Workflow session can be created",
        has_session,
        f"Response: {response}"
    )
    
    # Reset endpoint
    success, response, elapsed = validator.api_request("/api/workflow/reset", method="POST")
    reset_fast = elapsed < 5000  # Under 5 seconds per FR-007
    validator.check(
        "Reset completes in under 5 seconds",
        success and reset_fast,
        f"Elapsed: {elapsed:.0f}ms"
    )
    print()
    
    # Summary
    print("=" * 60)
    print(f"RESULTS: {validator.passed} passed, {validator.failed} failed")
    print("=" * 60)
    
    if validator.failed == 0:
        print("✅ ALL DEMO CHECKLIST ITEMS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME DEMO CHECKLIST ITEMS FAILED")
        print("Note: API tests require the server to be running at localhost:5000")
        sys.exit(1)


if __name__ == "__main__":
    main()
