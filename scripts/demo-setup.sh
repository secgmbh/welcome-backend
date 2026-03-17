#!/bin/bash

# Welcome Link Demo Setup Script
# Run this after backend deployment

set -e

API_URL="https://api.welcome-link.de"
DEMO_EMAIL="demo@welcome-link.de"
DEMO_PASSWORD="Demo123!"
PROPERTY_ID=17

echo "=== Welcome Link Demo Setup ==="
echo ""

# 1. Migrate QR Scans Table
echo "1. Creating QR scans table..."
curl -s -X POST "${API_URL}/api/debug/migrate-qr-scans" || echo "Already exists"

# 2. Login to get token
echo ""
echo "2. Logging in..."
TOKEN=$(curl -s -X POST "${API_URL}/api/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"${DEMO_EMAIL}\",\"password\":\"${DEMO_PASSWORD}\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")

if [ -z "$TOKEN" ]; then
  echo "ERROR: Login failed"
  exit 1
fi

echo "✅ Logged in"

# 3. Seed Demo Extras
echo ""
echo "3. Seeding demo extras..."
curl -s -X POST "${API_URL}/api/debug/seed-extras/${PROPERTY_ID}" \
  -H "Authorization: Bearer $TOKEN" || echo "Already seeded"

# 4. Verify
echo ""
echo "4. Verifying setup..."
EXTRAS=$(curl -s "${API_URL}/api/properties/${PROPERTY_ID}/extras")
echo "$EXTRAS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Extras count: {len(d.get(\"extras\",[]))}')"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Demo Links:"
echo "  Frontend: https://www.welcome-link.de"
echo "  Guestview: https://www.welcome-link.de/guestview/QEJHEXP1QF"
echo "  Login: ${DEMO_EMAIL} / ${DEMO_PASSWORD}"