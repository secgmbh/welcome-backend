#!/bin/bash
# Health Check Script for Welcome Link
# Run every 5 minutes via cron: */5 * * * * /path/to/healthcheck.sh

set -e

API_URL="https://api.welcome-link.de"
FRONTEND_URL="https://www.welcome-link.de"
WEBHOOK_URL="https://your-monitoring-service.com/webhook"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_api() {
    echo -n "Checking API... "
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/health" 2>/dev/null || echo "000")
    
    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}OK${NC} (HTTP $RESPONSE)"
        return 0
    else
        echo -e "${RED}FAILED${NC} (HTTP $RESPONSE)"
        return 1
    fi
}

check_frontend() {
    echo -n "Checking Frontend... "
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL" 2>/dev/null || echo "000")
    
    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}OK${NC} (HTTP $RESPONSE)"
        return 0
    else
        echo -e "${RED}FAILED${NC} (HTTP $RESPONSE)"
        return 1
    fi
}

check_api_response_time() {
    echo -n "Checking API response time... "
    TIME=$(curl -s -o /dev/null -w "%{time_total}" "$API_URL/api/health" 2>/dev/null || echo "0")
    
    # Compare with threshold (0.5 seconds)
    if (( $(echo "$TIME < 0.5" | bc -l) )); then
        echo -e "${GREEN}OK${NC} (${TIME}s)"
        return 0
    elif (( $(echo "$TIME < 1.0" | bc -l) )); then
        echo -e "${YELLOW}SLOW${NC} (${TIME}s)"
        return 0
    else
        echo -e "${RED}SLOW${NC} (${TIME}s)"
        return 1
    fi
}

check_demo_login() {
    echo -n "Checking Demo Login... "
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "$API_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"demo@welcome-link.de","password":"Demo123!"}' 2>/dev/null || echo "000")
    
    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}OK${NC} (HTTP $RESPONSE)"
        return 0
    else
        echo -e "${RED}FAILED${NC} (HTTP $RESPONSE)"
        return 1
    fi
}

# Run all checks
echo "========================================"
echo "Welcome Link Health Check"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"
echo ""

FAILURES=0

check_api || FAILURES=$((FAILURES + 1))
check_frontend || FAILURES=$((FAILURES + 1))
check_api_response_time || FAILURES=$((FAILURES + 1))
check_demo_login || FAILURES=$((FAILURES + 1))

echo ""
echo "========================================"

if [ $FAILURES -eq 0 ]; then
    echo -e "Status: ${GREEN}ALL CHECKS PASSED${NC}"
    echo "========================================"
    exit 0
else
    echo -e "Status: ${RED}$FAILURES CHECK(S) FAILED${NC}"
    echo "========================================"
    
    # Send alert webhook
    curl -s -X POST "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "{\"text\":\"⚠️ Welcome Link Health Check: $FAILURES check(s) failed\"}" \
        > /dev/null 2>&1 || true
    
    exit 1
fi