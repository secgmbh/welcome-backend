#!/bin/bash
# Setup Script für Welcome Link Gästeseite
# Ausführen nach Backend-Deployment

echo "=== Welcome Link Setup Script ==="
echo ""

# API URL
API="https://api.welcome-link.de"

# Login
echo "1. Login..."
TOKEN=$(curl -s -X POST "$API/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@welcome-link.de","password":"Demo123!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('token',''))")

if [ -z "$TOKEN" ]; then
  echo "❌ Login fehlgeschlagen"
  exit 1
fi
echo "✅ Login erfolgreich"

# QR-Scans Tabelle
echo ""
echo "2. QR-Scans Tabelle erstellen..."
curl -s -X POST "$API/api/debug/migrate-qr-scans" | python3 -m json.tool

# Demo-Extras
echo ""
echo "3. Demo-Extras erstellen..."
curl -s -X POST "$API/api/debug/seed-extras/17" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Verify
echo ""
echo "4. Verifizieren..."
echo "Public Property:"
curl -s "$API/api/public/properties/QEJHEXP1QF" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  Name:', d.get('name')); print('  WiFi:', d.get('wifi',{}).get('name'))"

echo ""
echo "Extras:"
curl -s "$API/api/properties/17/extras" | python3 -c "import sys,json; d=json.load(sys.stdin); print('  Count:', len(d.get('extras',[])))"

echo ""
echo "=== Setup abgeschlossen! ==="
echo "Gästeseite: https://www.welcome-link.de/guestview/QEJHEXP1QF"