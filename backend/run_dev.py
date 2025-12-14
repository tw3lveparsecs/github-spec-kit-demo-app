#!/usr/bin/env python
"""Development server runner with proper path setup."""
import os
import sys

# Add src directory to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_dir)
os.chdir(src_dir)

# Import and run the app
from app import app

if __name__ == '__main__':
    print("Starting development server...")
    app.run(host='0.0.0.0', port=5000, debug=False)
