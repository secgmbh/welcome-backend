#!/bin/bash
# Manual deployment script for Welcome Link Backend
# Usage: ./deploy-backend.sh

set -e

echo "=== Welcome Link Backend Deployment ==="
echo ""

# Check if we're in the backend directory
if [ ! -f "backend/server.py" ]; then
    echo "Error: Please run this script from the welcome-backend root directory"
    exit 1
fi

echo "1. Pulling latest changes..."
git pull origin main

echo ""
echo "2. Installing dependencies..."
cd backend
pip install -r requirements.txt --quiet

echo ""
echo "3. Running migrations..."
# Add migration commands here if needed

echo ""
echo "4. Restarting server..."
# For Docker:
if command -v docker-compose &> /dev/null; then
    docker-compose restart
    echo "Docker container restarted"
else
    echo "No docker-compose found. Please restart manually."
fi

echo ""
echo "5. Health check..."
sleep 5
curl -s "http://localhost:8000/api/health" || echo "Health check failed - server may not be running"

echo ""
echo "=== Deployment complete! ==="
echo "API URL: https://api.welcome-link.de"