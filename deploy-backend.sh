#!/bin/bash
# Deploy Backend to Render
# Run this when Render doesn't auto-deploy

echo "=== Welcome Link Backend Deploy ==="

# Sync server.py to backend folder
cp server.py backend/server.py
echo "✓ server.py synced to backend/"

# Commit and push
git add -A
git commit -m "chore: deploy $(date '+%Y-%m-%d %H:%M')"
git push origin main

echo ""
echo "✓ Pushed to GitHub"
echo ""
echo "Render sollte jetzt deployen."
echo "Falls nicht: https://dashboard.render.com → Manual Deploy"