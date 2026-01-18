# Testing Guide - Production Deployment

Comprehensive testing guide for deployed application on Render.

---

## Pre-Deployment Testing

### Local Testing

Before deploying, test locally:

```bash
# Run tests
python manage.py test

# Check for issues
python manage.py check --deploy

# Test with production settings
DEBUG=False python manage.py runserver
```

---

## Post-Deployment Testing

### 1. Health Check

**Test:** Basic application availability

```bash
# Check if application is running
curl -I https://your-app-name.onrender.com/

# Expected: HTTP/1.1 200 OK
```

### 2. Admin Interface

**Test:** Django admin functionality

1. Visit `https://your-app-name.onrender.com/admin/`
2. Login with superuser credentials
3. Verify all models are accessible:
   - Request Logs
   - Blocked IPs
   - Suspicious IPs
4. Test CRUD operations

### 3. API Endpoints

#### Request Logs API

```bash
# List all logs
curl https://your-app-name.onrender.com/api/v1/logs/

# Get specific log
curl https://your-app-name.onrender.com/api/v1/logs/1/

# Get statistics
curl https://your-app-name.onrender.com/api/v1/logs/stats/
```

#### Blocked IPs API

```bash
# List blocked IPs
curl https://your-app-name.onrender.com/api/v1/blocked/

# Block an IP
curl -X POST https://your-app-name.onrender.com/api/v1/blocked/ \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.0.0.1", "reason": "Test block"}'

# Unblock an IP
curl -X POST https://your-app-name.onrender.com/api/v1/blocked/1/unblock/
```

#### Suspicious IPs API

```bash
# List suspicious IPs
curl https://your-app-name.onrender.com/api/v1/suspicious/

# Block suspicious IP
curl -X POST https://your-app-name.onrender.com/api/v1/suspicious/1/block/
```

### 4. Rate Limiting

**Test:** Verify rate limits are enforced

```bash
# Test anonymous rate limit (5 requests/min)
for i in {1..10}; do 
  curl https://your-app-name.onrender.com/api/login/ \
    -X POST \
    -w "\nStatus: %{http_code}\n"
done

# First 5 should succeed (200)
# Remaining should fail (429 - Too Many Requests)
```

### 5. IP Logging

**Test:** Verify requests are being logged

```bash
# Make a request
curl https://your-app-name.onrender.com/

# Check if logged
curl https://your-app-name.onrender.com/api/v1/logs/ | grep "ip_address"
```

### 6. Geolocation

**Test:** Verify geolocation data is captured

```bash
# Check recent logs for geolocation data
curl https://your-app-name.onrender.com/api/v1/logs/ \
  | grep -E "(country|city)"

# Expected: country and city fields populated
```

### 7. Swagger Documentation

**Test:** Verify API documentation is accessible

1. Visit `https://your-app-name.onrender.com/swagger/`
2. Verify all endpoints are listed:
   - `/api/v1/logs/`
   - `/api/v1/blocked/`
   - `/api/v1/suspicious/`
3. Test "Try it out" functionality
4. Download OpenAPI schema: `/swagger.json`

### 8. Celery Worker

**Test:** Verify background tasks are running

```bash
# Check if worker is processing
# Go to Render Dashboard → Celery Worker → Logs

# Look for:
# [tasks]
#   . ip_tracking.tasks.detect_anomalies

# Manually trigger task (in Django shell)
from ip_tracking.tasks import detect_anomalies
result = detect_anomalies.delay()
print(f"Task ID: {result.id}")
print(f"Task Status: {result.status}")
```

### 9. Anomaly Detection

**Test:** Verify anomaly detection works

```bash
# Create suspicious activity (>100 requests)
for i in {1..110}; do
  curl https://your-app-name.onrender.com/
done

# Wait 1 hour or manually trigger task

# Check suspicious IPs
curl https://your-app-name.onrender.com/api/v1/suspicious/

# Should show your IP as suspicious
```

### 10. Static Files

**Test:** Verify static files are served

1. Visit admin interface
2. Check if CSS/JS are loading
3. Open browser DevTools → Network tab
4. Verify static files return 200 status

### 11. Database Persistence

**Test:** Verify data persists across restarts

```bash
# Create a blocked IP
curl -X POST https://your-app-name.onrender.com/api/v1/blocked/ \
  -H "Content-Type: application/json" \
  -d '{"ip_address": "10.0.0.2", "reason": "Persistence test"}'

# Restart web service in Render

# Check if data still exists
curl https://your-app-name.onrender.com/api/v1/blocked/
```

### 12. Security Headers

**Test:** Verify security headers are present

```bash
curl -I https://your-app-name.onrender.com/

# Expected headers:
# Strict-Transport-Security: max-age=31536000
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Content-Security-Policy: ...
```

### 13. HTTPS

**Test:** Verify HTTPS is enforced

```bash
# Try HTTP (should redirect to HTTPS)
curl -I http://your-app-name.onrender.com/

# Expected: 301 Moved Permanently
# Location: https://your-app-name.onrender.com/
```

---

## Load Testing

### Using Apache Bench

```bash
# Test 1000 requests with 10 concurrent connections
ab -n 1000 -c 10 https://your-app-name.onrender.com/

# Analyze results:
# - Requests per second
# - Time per request
# - Failed requests
```

### Using Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between

class IPTrackingUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/")
    
    @task(2)
    def view_logs(self):
        self.client.get("/api/v1/logs/")
    
    @task(1)
    def view_stats(self):
        self.client.get("/api/v1/logs/stats/")
```

Run test:
```bash
locust -f locustfile.py --host=https://your-app-name.onrender.com
```

---

## Integration Testing

### Test Complete Flow

```python
import requests

BASE_URL = "https://your-app-name.onrender.com"

# 1. Make request (should be logged)
response = requests.get(BASE_URL)
assert response.status_code == 200

# 2. Check if request was logged
logs = requests.get(f"{BASE_URL}/api/v1/logs/").json()
assert len(logs['results']) > 0

# 3. Block an IP
block_data = {
    "ip_address": "10.0.0.3",
    "reason": "Integration test"
}
response = requests.post(
    f"{BASE_URL}/api/v1/blocked/",
    json=block_data
)
assert response.status_code == 201

# 4. Verify IP is blocked
blocked = requests.get(f"{BASE_URL}/api/v1/blocked/").json()
assert any(ip['ip_address'] == '10.0.0.3' for ip in blocked['results'])

print("✓ All integration tests passed!")
```

---

## Monitoring Tests

### 1. Response Times

```bash
# Test response time
time curl https://your-app-name.onrender.com/

# Should be < 1 second
```

### 2. Memory Usage

Check in Render Dashboard:
- Should be < 512MB (free tier)
- Monitor for memory leaks

### 3. Database Size

```sql
-- Connect to PostgreSQL
psql $DATABASE_URL

-- Check database size
SELECT pg_size_pretty(pg_database_size('ip_tracking_db'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## Error Testing

### 1. Test 404 Not Found

```bash
curl -I https://your-app-name.onrender.com/nonexistent/

# Expected: 404 Not Found
```

### 2. Test 403 Forbidden

```bash
# Block your IP first, then access
curl -I https://your-app-name.onrender.com/

# Expected: 403 Forbidden
```

### 3. Test 429 Rate Limit

```bash
# Exceed rate limit
# Expected: 429 Too Many Requests
```

### 4. Test 500 Internal Server Error

Monitor logs for any 500 errors and fix immediately.

---

## Automated Testing Script

Create `test_deployment.sh`:

```bash
#!/bin/bash

BASE_URL="https://your-app-name.onrender.com"
PASSED=0
FAILED=0

echo "Testing Deployed Application..."
echo "================================"

# Test 1: Health Check
echo -n "Test 1: Health Check... "
if curl -f -s "$BASE_URL" > /dev/null; then
    echo "✓ PASSED"
    ((PASSED++))
else
    echo "✗ FAILED"
    ((FAILED++))
fi

# Test 2: Admin Available
echo -n "Test 2: Admin Interface... "
if curl -f -s "$BASE_URL/admin/" > /dev/null; then
    echo "✓ PASSED"
    ((PASSED++))
else
    echo "✗ FAILED"
    ((FAILED++))
fi

# Test 3: API Available
echo -n "Test 3: API Endpoints... "
if curl -f -s "$BASE_URL/api/v1/logs/" > /dev/null; then
    echo "✓ PASSED"
    ((PASSED++))
else
    echo "✗ FAILED"
    ((FAILED++))
fi

# Test 4: Swagger Available
echo -n "Test 4: Swagger Documentation... "
if curl -f -s "$BASE_URL/swagger/" > /dev/null; then
    echo "✓ PASSED"
    ((PASSED++))
else
    echo "✗ FAILED"
    ((FAILED++))
fi

# Test 5: HTTPS Redirect
echo -n "Test 5: HTTPS Redirect... "
if curl -I -s "http://your-app-name.onrender.com" | grep -q "301"; then
    echo "✓ PASSED"
    ((PASSED++))
else
    echo "✗ FAILED"
    ((FAILED++))
fi

echo "================================"
echo "Results: $PASSED passed, $FAILED failed"

if [ $FAILED -eq 0 ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Some tests failed"
    exit 1
fi
```

Run tests:
```bash
chmod +x test_deployment.sh
./test_deployment.sh
```

---

## Performance Benchmarks

### Expected Performance

| Metric | Target | Free Tier | Starter Plan |
|--------|--------|-----------|--------------|
| Response Time | <500ms | ~1000ms | ~300ms |
| Requests/sec | >50 | ~20 | ~100 |
| Uptime | 99.9% | 95% | 99.9% |
| Memory | <256MB | <512MB | <1GB |

---

## Continuous Testing

### Set Up Automated Tests

1. **GitHub Actions** (runs on each commit)
2. **Uptime Monitoring** (Render, UptimeRobot)
3. **Performance Monitoring** (New Relic, DataDog)
4. **Error Tracking** (Sentry)

---

## Test Results Documentation

Create test report:

```markdown
# Test Report

**Date:** 2026-01-18
**Tester:** Your Name
**Environment:** Production (Render)

## Results

| Test | Status | Response Time | Notes |
|------|--------|---------------|-------|
| Health Check | ✓ | 250ms | |
| Admin Interface | ✓ | 300ms | |
| API Endpoints | ✓ | 180ms | |
| Rate Limiting | ✓ | - | Working as expected |
| Swagger Docs | ✓ | 200ms | All endpoints documented |
| Celery Worker | ✓ | - | Tasks processing |
| Load Test | ✓ | - | 50 req/sec sustained |

## Issues Found

None

## Recommendations

- Monitor memory usage
- Consider upgrading to Starter plan for production
- Add more Celery workers for high load
```

---

**Testing Completed:** ✓  
**Deployment Status:** Production Ready  
**Version:** 1.0.0
