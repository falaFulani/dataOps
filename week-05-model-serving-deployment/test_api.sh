#!/usr/bin/env bash
# =============================================================================
# API Test Script
# =============================================================================
# Tests all endpoints of the model serving API.
# Run this after starting the service (locally or in Docker).
#
# Usage:
#   chmod +x test_api.sh
#   ./test_api.sh
# =============================================================================

set -euo pipefail

BASE_URL="${API_URL:-http://localhost:8000}"
PASS=0
FAIL=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

check_response() {
    local test_name="$1"
    local http_code="$2"
    local expected_code="$3"
    local body="$4"

    if [ "$http_code" == "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name (HTTP $http_code)"
        echo "   Response: $body" | head -c 200
        echo ""
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name (Expected HTTP $expected_code, got $http_code)"
        echo "   Response: $body"
        ((FAIL++))
    fi
}

# ---------------------------------------------------------------------------
# Test 1: Health Check
# ---------------------------------------------------------------------------
print_header "Test 1: Health Check (GET /health)"

RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/health")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

check_response "Health check" "$HTTP_CODE" "200" "$BODY"

# ---------------------------------------------------------------------------
# Test 2: Readiness Check
# ---------------------------------------------------------------------------
print_header "Test 2: Readiness Check (GET /ready)"

RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/ready")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

check_response "Readiness check" "$HTTP_CODE" "200" "$BODY"

# ---------------------------------------------------------------------------
# Test 3: Model Info
# ---------------------------------------------------------------------------
print_header "Test 3: Model Info (GET /model-info)"

RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/model-info")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

check_response "Model info" "$HTTP_CODE" "200" "$BODY"

# ---------------------------------------------------------------------------
# Test 4: Valid Prediction (Setosa)
# ---------------------------------------------------------------------------
print_header "Test 4: Prediction - Setosa (POST /predict)"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/predict" \
    -H "Content-Type: application/json" \
    -d '{"features": [5.1, 3.5, 1.4, 0.2]}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

check_response "Predict Setosa" "$HTTP_CODE" "200" "$BODY"

# ---------------------------------------------------------------------------
# Test 5: Valid Prediction (Versicolor)
# ---------------------------------------------------------------------------
print_header "Test 5: Prediction - Versicolor (POST /predict)"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/predict" \
    -H "Content-Type: application/json" \
    -d '{"features": [6.4, 3.2, 4.5, 1.5]}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

check_response "Predict Versicolor" "$HTTP_CODE" "200" "$BODY"

# ---------------------------------------------------------------------------
# Test 6: Valid Prediction (Virginica)
# ---------------------------------------------------------------------------
print_header "Test 6: Prediction - Virginica (POST /predict)"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/predict" \
    -H "Content-Type: application/json" \
    -d '{"features": [7.7, 3.0, 6.1, 2.3]}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

check_response "Predict Virginica" "$HTTP_CODE" "200" "$BODY"

# ---------------------------------------------------------------------------
# Test 7: Invalid Input - Wrong number of features
# ---------------------------------------------------------------------------
print_header "Test 7: Invalid Input - Wrong Feature Count (POST /predict)"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/predict" \
    -H "Content-Type: application/json" \
    -d '{"features": [5.1, 3.5]}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

check_response "Reject wrong feature count" "$HTTP_CODE" "422" "$BODY"

# ---------------------------------------------------------------------------
# Test 8: Invalid Input - Negative features
# ---------------------------------------------------------------------------
print_header "Test 8: Invalid Input - Negative Values (POST /predict)"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/predict" \
    -H "Content-Type: application/json" \
    -d '{"features": [-1.0, 3.5, 1.4, 0.2]}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

check_response "Reject negative features" "$HTTP_CODE" "422" "$BODY"

# ---------------------------------------------------------------------------
# Test 9: Invalid Input - Missing body
# ---------------------------------------------------------------------------
print_header "Test 9: Invalid Input - Missing Body (POST /predict)"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/predict" \
    -H "Content-Type: application/json" \
    -d '{}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

check_response "Reject missing body" "$HTTP_CODE" "422" "$BODY"

# ---------------------------------------------------------------------------
# Test 10: OpenAPI Docs Available
# ---------------------------------------------------------------------------
print_header "Test 10: OpenAPI Docs (GET /docs)"

RESPONSE=$(curl -s -w "\n%{http_code}" "${BASE_URL}/docs")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✅ PASS${NC}: Swagger UI available at ${BASE_URL}/docs"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC}: Swagger UI not available (HTTP $HTTP_CODE)"
    ((FAIL++))
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print_header "Test Summary"
TOTAL=$((PASS + FAIL))
echo -e "  Total:  $TOTAL"
echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the output above.${NC}"
    exit 1
fi
