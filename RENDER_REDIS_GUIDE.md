# Render Built-in Redis (Key Value) Setup Guide

Great news! Render has a **built-in Redis service** called "Key Value" with a **FREE tier**. No need for external providers like Upstash!

---

## What is Render Key Value?

Render Key Value is a managed Redis-compatible service (uses Valkey 8) that's perfect for:
- Caching
- Session storage
- Celery job queues
- Rate limiting

---

## Free Tier Benefits

### What You Get (FREE)
- ✅ Redis-compatible Key Value store
- ✅ One free instance per workspace
- ✅ Auto-configured connection URLs
- ✅ Built-in metrics dashboard
- ✅ Internal URL (no auth needed)
- ✅ Perfect for development & testing

### Limitations
- ⚠️ **No disk persistence** - data is lost on restart
- ⚠️ Memory eviction when full (uses LRU policy)
- ⚠️ Not suitable for critical production data
- ⚠️ One free instance limit per workspace

### When to Upgrade to Paid ($7/month)
- ✅ Disk-backed persistence (data survives restarts)
- ✅ Production SLA
- ✅ More memory options
- ✅ Loses only 1 second of data in worst case

---

## How It's Already Configured

Your `render.yaml` is **already set up** to use Render's Key Value! Here's what happens automatically:

### 1. Key Value Instance Created
```yaml
databases:
  - name: ip-tracking-redis
    plan: free
    maxmemoryPolicy: allkeys-lru  # Least Recently Used eviction
    ipAllowList: []                # Internal access only
```

### 2. Auto-Connected to All Services
```yaml
envVars:
  - key: REDIS_URL
    fromService:
      type: redis
      name: ip-tracking-redis
      property: connectionString
```

This automatically:
- Creates Redis instance
- Generates connection URL
- Injects URL into all your services (web, workers)
- No manual configuration needed!

---

## Deployment Steps (Super Simple!)

### Option 1: Automatic Deployment (Recommended)

1. **Push to GitHub** (already done)
   ```bash
   git push origin main
   ```

2. **Go to Render Dashboard**
   - Visit [https://render.com](https://render.com)
   - Sign up / Log in

3. **Create New Blueprint**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - Render detects `render.yaml`
   - Click "Apply"

4. **Wait 5-10 minutes**
   Render will automatically create:
   - PostgreSQL database
   - Redis Key Value instance
   - Django web service
   - Celery worker
   - Celery beat scheduler

5. **Add ALLOWED_HOSTS**
   - Go to Web Service → Environment
   - Add: `ALLOWED_HOSTS=your-app-name.onrender.com`
   - Save (auto-redeploys)

6. **Create Superuser**
   - Web Service → Shell tab
   - Run: `python manage.py createsuperuser`

7. **Access Your App**
   - Web: `https://your-app-name.onrender.com/`
   - Admin: `https://your-app-name.onrender.com/admin/`
   - Swagger: `https://your-app-name.onrender.com/swagger/`

---

## Verifying Redis Connection

### Check in Render Dashboard

1. Go to Dashboard → Databases
2. You should see:
   - `ip-tracking-db` (PostgreSQL)
   - `ip-tracking-redis` (Key Value)

### Test Redis in Shell

```bash
# In Render Web Service Shell
python manage.py shell

# Test connection
>>> from django.core.cache import cache
>>> cache.set('test', 'Hello Redis!', 60)
>>> cache.get('test')
'Hello Redis!'
```

### Check Celery Workers

```bash
# In Celery Worker logs (Render Dashboard)
# You should see:
# [tasks]
#   . ip_tracking.tasks.detect_anomalies

# Connected to redis://...
```

---

## What Works Now (With Free Tier)

### Fully Functional Features
✅ **IP Tracking** - All requests logged  
✅ **Geolocation Caching** - 24-hour cache (survives until restart)  
✅ **Rate Limiting** - Redis-backed rate limiting  
✅ **IP Blocking** - Fast Redis-cached checks  
✅ **Celery Workers** - Background task processing  
✅ **Anomaly Detection** - Hourly scheduled tasks  
✅ **Admin Dashboard** - Full access  
✅ **REST API** - All endpoints working  
✅ **Swagger Docs** - Interactive API docs  

### Acceptable Trade-offs (Free Tier)
⚠️ **Cache clears on restart** - Happens during:
  - Render maintenance
  - App redeployment
  - Service restarts

**Impact:**
- Geolocation will need to re-fetch after restart (minor)
- Rate limit counters reset (acceptable for dev/testing)
- Celery tasks in queue lost (re-run when worker restarts)

**For Production:**
- Upgrade Redis to paid tier ($7/month) for persistence
- Or keep free tier if cache clearing is acceptable

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│              Render Platform (Free)                  │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────────┐   ┌──────────────┐               │
│  │  PostgreSQL  │   │  Key Value   │               │
│  │  (Database)  │   │   (Redis)    │               │
│  │   Free 90d   │   │   Free ✨    │               │
│  └──────┬───────┘   └──────┬───────┘               │
│         │                   │                        │
│  ┌──────┴───────────────────┴───────┐              │
│  │                                    │              │
│  │  ┌──────────────┐                │              │
│  │  │  Web Service │◄────Redis      │              │
│  │  │   (Django)   │     Cache      │              │
│  │  │  + Gunicorn  │                │              │
│  │  └──────────────┘                │              │
│  │                                    │              │
│  │  ┌──────────────┐                │              │
│  │  │Celery Worker │◄────Redis      │              │
│  │  │ (Background) │     Queue      │              │
│  │  └──────────────┘                │              │
│  │                                    │              │
│  │  ┌──────────────┐                │              │
│  │  │ Celery Beat  │◄────Redis      │              │
│  │  │ (Scheduler)  │     Backend    │              │
│  │  └──────────────┘                │              │
│  │                                    │              │
│  └────────────────────────────────────┘             │
│                                                       │
└─────────────────────────────────────────────────────┘
           │
           ▼
   ┌──────────────┐
   │    User      │
   │  (Browser)   │
   └──────────────┘
```

---

## Monitoring Your Redis

### In Render Dashboard

1. Go to `ip-tracking-redis` service
2. View metrics:
   - Memory usage
   - Active connections
   - Commands per second
   - CPU usage

### Check Connection Count

```python
# In Django shell
from django.core.cache import cache
from django.core.cache.backends.redis import RedisCache

backend = cache._cache
info = backend.get_client().info()
print(f"Connected clients: {info['connected_clients']}")
print(f"Used memory: {info['used_memory_human']}")
```

---

## Troubleshooting

### Issue: "Can't connect to Redis"

**Check:**
1. Verify `ip-tracking-redis` service is created
2. Check Web Service → Environment → `REDIS_URL` is set
3. Look at Redis service logs
4. Ensure services are in same region

**Fix:**
- Redeploy: Render → Web Service → Manual Deploy

### Issue: "Cache not working"

**Test:**
```python
from django.core.cache import cache
cache.set('test', 'value')
result = cache.get('test')
print(result)  # Should print: value
```

If `None`, check `REDIS_URL` environment variable.

### Issue: "Celery not processing tasks"

**Check Celery Worker Logs:**
1. Render Dashboard → `ip-tracking-celery-worker`
2. Look for "Connected to redis://..."
3. Should see registered tasks

**Manual Test:**
```python
from ip_tracking.tasks import detect_anomalies
detect_anomalies.delay()
```

---

## Cost Breakdown (FREE!)

| Service | Plan | Cost | Features |
|---------|------|------|----------|
| Web Service | Free | $0 | 750 hrs/month, sleeps after 15min |
| PostgreSQL | Free | $0 | 90 days, then $7/month |
| Key Value (Redis) | Free | $0 | No persistence, 750 hrs/month |
| Celery Worker | Free | $0 | 750 hrs/month |
| Celery Beat | Free | $0 | 750 hrs/month |
| **Total** | **Free** | **$0** | **Perfect for testing!** |

### Upgrade Path (When Ready)

| Service | Starter | Monthly Cost |
|---------|---------|--------------|
| Web Service | Starter | $7 |
| PostgreSQL | Starter | $7 |
| Key Value | Starter | $7 (with persistence) |
| Workers (2x) | Starter | $14 ($7 each) |
| **Total Production** | **Starter** | **$35/month** |

---

## Comparison with External Redis

| Feature | Render Key Value | Upstash | Redis Cloud |
|---------|-----------------|---------|-------------|
| **Setup** | ✅ Automatic | ⚠️ Manual | ⚠️ Manual |
| **Free Tier** | ✅ Yes | ✅ Yes (10K cmd/day) | ✅ Yes (30MB) |
| **Integration** | ✅ Native | ⚠️ External URL | ⚠️ External URL |
| **Latency** | ✅ Same DC | ⚠️ Internet | ⚠️ Internet |
| **Config** | ✅ Zero config | ⚠️ Manual env vars | ⚠️ Manual env vars |
| **Persistence** | ⚠️ Paid only | ✅ Free tier | ✅ Free tier |

**Winner: Render Key Value** for simplicity and integration!

---

## Next Steps

### You're Ready to Deploy!

Your configuration is complete with Render's built-in Redis:

1. ✅ `render.yaml` configured
2. ✅ Redis Key Value included
3. ✅ All services connected
4. ✅ Celery workers configured
5. ✅ Ready for one-click deployment

### Deploy Now:

```bash
# Already pushed to GitHub
# Just go to Render Dashboard and click "New Blueprint"
```

### After Deployment:

1. Set `ALLOWED_HOSTS` in environment
2. Create superuser
3. Test all features
4. Access Swagger docs
5. Monitor Redis metrics

---

## Success Checklist

After deployment, verify:

- [ ] Web service is live
- [ ] Admin login works
- [ ] Swagger accessible at `/swagger/`
- [ ] Redis connected (test in shell)
- [ ] Celery worker running (check logs)
- [ ] Celery beat scheduling (check logs)
- [ ] IP logging works
- [ ] Rate limiting works
- [ ] Geolocation caching works

---

## Support Resources

- [Render Key Value Docs](https://render.com/docs/redis)
- [Render Dashboard](https://dashboard.render.com)
- [Render Community Forum](https://community.render.com)
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

**You're all set! Render's built-in Redis makes deployment super simple.** 🚀

No external services needed. Everything is configured and ready to go!
