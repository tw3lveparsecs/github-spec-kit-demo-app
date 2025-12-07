#!/usr/bin/env python
"""Test API endpoints"""

import sys
sys.path.insert(0, 'src')

from app import app

# Test the app with test client
with app.test_client() as client:
    # Test health endpoint
    print("Testing /api/health...")
    response = client.get('/api/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json}")
    print()
    
    # Test scenarios endpoint
    print("Testing /api/scenarios...")
    response = client.get('/api/scenarios')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json
        print(f"Found {data['total']} scenarios:")
        for scenario in data['scenarios']:
            print(f"  - {scenario['id']}: {scenario['title']}")
    else:
        print(f"Error: {response.json}")
    print()
    
    # Test specific scenario
    print("Testing /api/scenarios/user-authentication...")
    response = client.get('/api/scenarios/user-authentication')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        scenario = response.json
        print(f"Title: {scenario['title']}")
        print(f"Description: {scenario['description']}")
        print(f"Workflow phases: {len(scenario['workflow_phases'])}")
    else:
        print(f"Error: {response.json}")
