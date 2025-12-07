#!/usr/bin/env python
"""Test script to verify API is working"""

import sys
sys.path.insert(0, 'src')

from services.scenario_service import ScenarioService

# Test ScenarioService
print("Testing ScenarioService...")
service = ScenarioService()
scenarios = service.list_scenarios()
print(f"Found {len(scenarios)} scenarios:")
for scenario in scenarios:
    print(f"  - {scenario.id}: {scenario.title}")

# Test app routes
print("\nTesting Flask app routes...")
from app import app
routes = [str(rule) for rule in app.url_map.iter_rules()]
print("Registered routes:")
for route in routes:
    print(f"  {route}")
