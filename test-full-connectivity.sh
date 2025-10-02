#!/bin/bash

echo "=== Resume Builder Connectivity Test ==="
echo

# Test 1: Backend Health Check
echo "1. Testing Backend Health..."
BACKEND_HEALTH=$(curl -s http://localhost:5000/api/health)
if [ $? -eq 0 ]; then
    echo "✅ Backend is healthy: $BACKEND_HEALTH"
else
    echo "❌ Backend health check failed"
fi
echo

# Test 2: Frontend Accessibility
echo "2. Testing Frontend Accessibility..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend is accessible (HTTP $FRONTEND_STATUS)"
else
    echo "❌ Frontend accessibility failed (HTTP $FRONTEND_STATUS)"
fi
echo

# Test 3: CORS Configuration
echo "3. Testing CORS Configuration..."
CORS_TEST=$(curl -s -H "Origin: http://localhost:8080" -H "Access-Control-Request-Method: POST" -H "Access-Control-Request-Headers: Content-Type" -X OPTIONS http://localhost:5000/api/resumes -w "%{http_code}")
if [[ "$CORS_TEST" == *"204"* ]]; then
    echo "✅ CORS is properly configured"
else
    echo "❌ CORS configuration issue: $CORS_TEST"
fi
echo

# Test 4: Database Connection
echo "4. Testing Database Connection..."
DB_TEST=$(docker exec resume_builder_backend python -c "
from database import get_db_cursor
try:
    cursor = get_db_cursor()
    cursor.execute('SELECT 1')
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
")
echo "$DB_TEST"
echo

# Test 5: Container Network Communication
echo "5. Testing Container Network Communication..."
NETWORK_TEST=$(docker exec resume_builder_frontend wget -qO- http://backend:5000/api/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ Frontend can reach backend via Docker network: $NETWORK_TEST"
else
    echo "❌ Frontend cannot reach backend via Docker network"
fi
echo

# Test 6: API Endpoint Test
echo "6. Testing API Endpoints..."
API_TEST=$(curl -s -X POST http://localhost:5000/api/resumes \
  -H "Content-Type: application/json" \
  -d '{"personal_info":{"full_name":"Test User","email":"test@example.com","phone":"123-456-7890","location":"Test City"},"summary":"Test summary","experience":[],"education":[],"skills":[],"projects":[]}' \
  -w "%{http_code}")

if [[ "$API_TEST" == *"201"* ]] || [[ "$API_TEST" == *"200"* ]]; then
    echo "✅ API endpoint is working"
else
    echo "❌ API endpoint test failed: $API_TEST"
fi
echo

echo "=== Test Summary ==="
echo "Frontend URL: http://localhost:8080"
echo "Backend URL: http://localhost:5000"
echo "API Base URL: http://localhost:5000/api"
echo
echo "If all tests pass, your frontend should be able to reach the backend successfully!"
