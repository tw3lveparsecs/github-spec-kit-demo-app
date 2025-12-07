"""
Test script for workflow endpoints using Flask test client.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app import app


def test_workflow_endpoints():
    """Test the workflow endpoints."""
    with app.test_client() as client:
        print("=" * 70)
        print("Testing Workflow Endpoints")
        print("=" * 70)

        # Test 1: GET /api/workflow/user-authentication
        print("\n1. GET /api/workflow/user-authentication")
        response = client.get("/api/workflow/user-authentication")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   Scenario: {data.get('scenario', {}).get('title', 'N/A')}")
            print(f"   Current Phase: {data.get('current_phase', {}).get('display_name', 'N/A')}")
            print(f"   Phase Index: {data.get('phase_index', 'N/A')}/{data.get('total_phases', 'N/A')}")
        else:
            print(f"   Error: {response.data.decode()}")

        # Test 2: POST /api/workflow/user-authentication/step
        print("\n2. POST /api/workflow/user-authentication/step")
        response = client.post("/api/workflow/user-authentication/step")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   Current Phase: {data.get('current_phase', {}).get('display_name', 'N/A')}")
        else:
            print(f"   Error: {response.data.decode()}")

        # Test 3: POST /api/workflow/user-authentication/jump
        print("\n3. POST /api/workflow/user-authentication/jump")
        response = client.post(
            "/api/workflow/user-authentication/jump",
            json={"phase": "plan"},
            content_type="application/json",
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   Current Phase: {data.get('current_phase', {}).get('display_name', 'N/A')}")
        else:
            print(f"   Error: {response.data.decode()}")

        print("\n" + "=" * 70)
        print("Test Complete")
        print("=" * 70)


if __name__ == "__main__":
    test_workflow_endpoints()
