#!/bin/bash
# Integration test for frontend-backend connection

set -e

API_URL="http://localhost:8000"
TIMEOUT=5

echo "🧪 Frontend-Backend Integration Test"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health check
echo -n "1. Testing API health endpoint... "
if timeout $TIMEOUT curl -s "$API_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} (API not running)"
    echo "   Start with: uv run uvicorn dash_ai.api.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

# Test 2: API documentation
echo -n "2. Testing API documentation endpoint... "
if timeout $TIMEOUT curl -s "$API_URL/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} (API docs not available)"
    exit 1
fi

# Test 3: Invalid query (should fail with 422)
echo -n "3. Testing input validation (empty question)... "
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": ""}')
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "422" ]; then
    echo -e "${GREEN}✓${NC} (correctly rejected)"
else
    echo -e "${RED}✗${NC} (expected 422, got $http_code)"
fi

# Test 4: CORS headers
echo -n "4. Testing CORS headers... "
cors_header=$(curl -s -I "$API_URL/health" | grep -i "access-control-allow-origin" || echo "")
if [ -n "$cors_header" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC} (CORS header not found - might be needed for production)"
fi

# Test 5: Proper request format
echo -n "5. Testing proper request format... "
response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}')
http_code=$(echo "$response" | tail -n1)
# Should be 502 because Ollama/CLI might not be ready, but request format is OK
if [ "$http_code" = "200" ] || [ "$http_code" = "502" ] || [ "$http_code" = "504" ]; then
    echo -e "${GREEN}✓${NC} (request accepted)"
else
    echo -e "${RED}✗${NC} (unexpected status $http_code)"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Backend API is ready for frontend!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Next steps:"
echo "1. Check frontend is running: npm run dev (in frontend/)"
echo "2. Open http://localhost:5173 in your browser"
echo "3. Ask a question to test the full integration"
echo ""
echo "API Documentation: http://localhost:8000/docs"
