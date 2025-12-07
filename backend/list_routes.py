"""List all registered Flask routes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from app import app

print("=== Registered Routes ===")
for rule in app.url_map.iter_rules():
    methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"{rule.rule:50} {methods:20} -> {rule.endpoint}")
