#!/bin/bash
set -e

echo "🚀 Setting up GitHub Spec Kit Demo Application..."

# Navigate to workspace
cd /workspace

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd ../frontend
npm install

# Return to workspace root
cd /workspace

# Verify installations
echo "✅ Verifying installations..."
python --version
flask --version
node --version
npm --version

echo "✨ Setup complete! Ready to start developing."
echo ""
echo "Quick start commands:"
echo "  cd backend && flask run              # Start Flask backend"
echo "  cd frontend && npx playwright test   # Run e2e tests"
echo ""
