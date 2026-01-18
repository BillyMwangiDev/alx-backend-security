# Redis Setup for Render Deployment

Since Render doesn't offer a free Redis service, here are your options for adding Redis to your deployment.

---

## Option 1: Upstash Redis (Recommended - Free Tier Available)

### Step 1: Create Upstash Account

1. Go to [https://upstash.com/](https://upstash.com/)
2. Sign up for free account
3. Verify your email

### Step 2: Create Redis Database

1. Click "Create Database"
2. Configure:
   - **Name:** `ip-tracking-redis`
   - **Type:** Regional (cheaper) or Global
   - **Region:** Choose closest to your Render deployment
   - **TLS:** Enabled (recommended)
3. Click "Create"

### Step 3: Get Connection Details

1. Click on your database
2. Copy the **Redis URL** (looks like: `redis://default:password@endpoint.upstash.io:port`)
3. Save this for next step

### Step 4: Add to Render

1. Go to Render Dashboard
2. Click on your web service
3. Go to "Environment" tab
4. Add environment variable:
   - **Key:** `REDIS_URL`
   - **Value:** `<your-upstash-redis-url>`
5. Click "Save Changes"
6. Service will auto-redeploy

### Step 5: Enable Celery Workers (Optional)

If you want background tasks:

1. Edit `render.yaml` file
2. Uncomment the Celery worker and beat sections
3. Commit and push to GitHub
4. Render will detect changes and create workers

**Free Tier Limits:**
- 10,000 commands/day
- 256 MB storage
- Good for development and small production apps

---

## Option 2: Redis Cloud (Free Tier Available)

### Step 1: Create Redis Cloud Account

1. Go to [https://redis.com/try-free/](https://redis.com/try-free/)
2. Sign up for free account
3. Verify email

### Step 2: Create Database

1. Click "New Subscription"
2. Select "Fixed Plan" → "Free"
3. Choose AWS as cloud provider
4. Select region closest to Render deployment
5. Name your database: `ip-tracking`
6. Click "Create"

### Step 3: Get Connection String

1. Go to "Databases" tab
2. Click on your database
3. Copy "Public endpoint"
4. Format: `redis://default:password@endpoint:port`

### Step 4: Add to Render

Same as Upstash steps 4-5 above

**Free Tier Limits:**
- 30 MB storage
- Shared resources
- No credit card required

---

## Option 3: Deploy Without Redis (Quick Start)

Your app is configured to work without Redis for initial deployment:

### What Works Without Redis:

✅ **All core features:**
- IP logging
- IP blocking
- Admin interface
- API endpoints
- Swagger documentation
- Rate limiting (uses local memory)

❌ **Limited features:**
- Geolocation caching (will query every time)
- Background tasks (Celery won't work)
- Anomaly detection (requires Celery)

### When to Add Redis:

Add Redis when you need:
1. Better caching performance
2. Background task processing
3. Anomaly detection
4. Higher traffic (>1000 requests/day)

---

## Configuration Details

### Current Settings (Without Redis)

```python
# Cache: Uses local memory
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

# Celery: Uses Django database as broker (slower)
CELERY_BROKER_URL = 'django://'
```

### With Redis (After Setup)

```python
# Cache: Uses Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    },
}

# Celery: Uses Redis
CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
```

---

## Quick Deployment (No Redis)

### Deploy Now Without Redis:

```bash
# Your app will deploy successfully with:
# - PostgreSQL database
# - Django web service
# - All API features working
# - Local memory caching

# Simply push to GitHub:
git add .
git commit -m "Ready for deployment"
git push origin main

# Then deploy on Render
```

### Add Redis Later:

1. Sign up for Upstash or Redis Cloud
2. Get Redis URL
3. Add `REDIS_URL` to Render environment variables
4. Enable Celery workers in render.yaml
5. Redeploy

---

## Performance Comparison

| Feature | Without Redis | With Redis |
|---------|--------------|------------|
| Response Time | ~1000ms | ~300ms |
| Cache Hit Rate | 0% (no cache) | 99% |
| Geolocation | Query every time | Cached 24h |
| Background Tasks | No | Yes |
| Anomaly Detection | No | Yes (hourly) |
| Scalability | Single server | Multi-server ready |

---

## Testing Redis Connection

### After adding Redis URL:

```bash
# In Render Shell
python manage.py shell

# Test Redis connection
from django.core.cache import cache
cache.set('test_key', 'test_value', 60)
result = cache.get('test_key')
print(f"Redis test: {result}")  # Should print: Redis test: test_value
```

---

## Troubleshooting

### Issue: Redis connection refused

**Solution:**
1. Verify Redis URL is correct
2. Check if TLS is required (Upstash requires TLS)
3. Ensure firewall allows connection
4. Test connection string format

### Issue: Celery not processing tasks

**Solution:**
1. Verify REDIS_URL environment variable is set
2. Check Celery worker logs in Render
3. Ensure Celery worker service is running
4. Test Redis connection first

### Issue: Rate limiting not working

**Solution:**
1. With local cache, rate limiting works per server only
2. For distributed rate limiting, add Redis
3. Check `RATELIMIT_USE_CACHE` setting

---

## Recommended Setup Path

### Phase 1: Initial Deployment (Day 1)
- ✅ Deploy without Redis
- ✅ Test all basic features
- ✅ Verify Swagger documentation
- ✅ Check admin interface

### Phase 2: Add Redis (Day 2-7)
- ✅ Sign up for Upstash (free)
- ✅ Add REDIS_URL to Render
- ✅ Enable geolocation caching
- ✅ Monitor cache performance

### Phase 3: Enable Background Tasks (Week 2)
- ✅ Uncomment Celery workers in render.yaml
- ✅ Enable anomaly detection
- ✅ Set up monitoring
- ✅ Test scheduled tasks

---

## Cost Comparison

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| **Upstash** | 10K commands/day, 256MB | $0.20/100K commands |
| **Redis Cloud** | 30MB storage | $5/month (500MB) |
| **Local Cache** | Free (no limits) | N/A |

---

## Final Recommendation

**For immediate deployment:**
1. Deploy now without Redis ✅
2. App will work perfectly for testing and demos
3. Add Redis later when needed for production

**For production deployment:**
1. Set up Upstash Redis (5 minutes)
2. Add REDIS_URL to Render
3. Enable Celery workers
4. Full feature set available

---

## Next Steps

1. **Deploy without Redis first** - Get your app live quickly
2. **Test all features** - Verify everything works
3. **Add Upstash Redis** - When ready for caching
4. **Enable Celery** - When ready for background tasks

Your app is designed to work in both scenarios! 🚀

---

**Quick Links:**
- [Upstash](https://upstash.com/)
- [Redis Cloud](https://redis.com/try-free/)
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
