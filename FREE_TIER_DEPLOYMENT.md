# Free Tier Deployment Guide

## What Works on Render's Free Tier

Good news! Most of your application works perfectly on the **100% FREE** tier:

### ✅ Fully Functional (FREE)

| Feature | Status | Notes |
|---------|--------|-------|
| **Web Service** | ✅ Works | Django app with Gunicorn |
| **PostgreSQL Database** | ✅ Works | 90 days free, then $7/month |
| **Redis Key Value** | ✅ Works | Full Redis caching |
| **IP Tracking** | ✅ Works | All requests logged |
| **Geolocation** | ✅ Works | With 24hr caching |
| **Rate Limiting** | ✅ Works | Redis-backed |
| **IP Blacklisting** | ✅ Works | Fast blocking |
| **Admin Dashboard** | ✅ Works | Full Django admin |
| **REST API** | ✅ Works | All endpoints |
| **Swagger Docs** | ✅ Works | Interactive API docs |
| **Static Files** | ✅ Works | WhiteNoise serving |

### ⚠️ Limited on Free Tier

| Feature | Status | Workaround |
|---------|--------|------------|
| **Celery Workers** | ❌ Requires Paid | Upgrade to Starter ($7/month) |
| **Anomaly Detection** | ❌ Requires Celery | Manual checks or upgrade |
| **Scheduled Tasks** | ❌ Requires Celery | On-demand execution or upgrade |

---

## What You're Missing Without Celery

### Background Tasks (Celery Workers)

**What it does:**
- Process tasks asynchronously without blocking web requests
- Handle long-running operations

**Impact without it:**
- ✅ All web features still work
- ✅ Admin can manually trigger checks
- ⚠️ No automatic background processing

### Anomaly Detection (Celery Beat)

**What it does:**
- Runs hourly task to flag suspicious IPs
- Detects IPs exceeding 100 requests/hour
- Flags access to sensitive paths

**Workaround:**
```python
# Manual trigger in Django shell or create a view
from ip_tracking.tasks import detect_anomalies
detect_anomalies()
```

---

## Free Tier Deployment Steps

### 1. In Render Dashboard

You should see:
```
✅ Create Key Value ip-tracking-redis
✅ Create web service ip-tracking-web
✅ Create database ip-tracking-db
❌ Create background worker ip-tracking-celery-worker (SKIP)
❌ Create background worker ip-tracking-celery-beat (SKIP)
```

**Action:** Click "Apply" and skip the worker errors.

### 2. Set ALLOWED_HOSTS

Once deployed, add:
```
ALLOWED_HOSTS: *.onrender.com
```

Or your specific URL:
```
ALLOWED_HOSTS: your-app-name.onrender.com
```

### 3. Create Superuser

In Render Shell:
```bash
python manage.py createsuperuser
```

---

## Cost Breakdown

### Free Tier (What You'll Deploy)

| Service | Plan | Cost | Monthly Hours |
|---------|------|------|---------------|
| Web Service | Free | $0 | 750 hrs shared |
| PostgreSQL | Free | $0 | 90 days, then $7/month |
| Redis | Free | $0 | 750 hrs shared |
| **Total** | **FREE** | **$0** | **First 90 days completely free!** |

**Limitations:**
- Web service sleeps after 15 min inactivity (50-100ms cold start)
- Shared 750 instance hours/month across all free services
- No background workers

### Starter Plan (Full Features)

| Service | Plan | Cost |
|---------|------|------|
| Web Service | Starter | $7/month |
| PostgreSQL | Starter | $7/month |
| Redis | Starter | $7/month |
| Celery Worker | Starter | $7/month |
| Celery Beat | Starter | $7/month |
| **Total** | **Starter** | **$35/month** |

**Benefits:**
- No sleep/cold starts
- Background task processing
- Automatic anomaly detection
- More resources
- Better uptime

---

## Upgrade Path (When Ready)

### Option 1: Add Workers Only ($14/month)

Keep web/DB/Redis on free tier, add just workers:

```yaml
# Uncomment in render.yaml and change plan to "starter"
- type: worker
  name: ip-tracking-celery-worker
  plan: starter  # $7/month
```

**Result:** $14/month for full background processing

### Option 2: Full Production ($35/month)

Upgrade all services to Starter plan for best performance.

---

## Manual Anomaly Detection

Since Celery isn't available, you can run anomaly detection manually:

### Option 1: Django Shell

```bash
# In Render Shell
python manage.py shell

# Run detection
from ip_tracking.tasks import detect_anomalies
detect_anomalies()
```

### Option 2: Create Management Command

Create: `ip_tracking/management/commands/detect_anomalies.py`

```python
from django.core.management.base import BaseCommand
from ip_tracking.tasks import detect_anomalies

class Command(BaseCommand):
    help = 'Detect anomalous IP activity'

    def handle(self, *args, **options):
        detect_anomalies()
        self.stdout.write(self.style.SUCCESS('Anomaly detection complete'))
```

Run:
```bash
python manage.py detect_anomalies
```

### Option 3: Create Admin Action

Already implemented in `admin.py`:
1. Go to Admin → Suspicious IPs
2. Select IPs to review
3. Use bulk actions

---

## Testing Without Celery

### What to Test

1. **Web Application**
   ```
   https://your-app.onrender.com/
   ```

2. **Admin Interface**
   ```
   https://your-app.onrender.com/admin/
   ```

3. **Swagger API Docs**
   ```
   https://your-app.onrender.com/swagger/
   ```

4. **IP Logging**
   - Visit pages
   - Check admin → Request Logs
   - Verify IPs are logged

5. **Rate Limiting**
   - Make multiple rapid requests
   - Should see 429 errors after limit

6. **Geolocation**
   - Check Request Logs
   - Should show country/city

7. **IP Blocking**
   ```bash
   python manage.py block_ip 1.2.3.4 --reason "Testing"
   ```

### What Won't Work (Yet)

- ❌ Automatic hourly anomaly detection
- ❌ Background task queue
- ❌ Scheduled jobs

**Workaround:** Run manually as needed

---

## When to Upgrade

### Stick with Free If:
- ✅ Personal project or portfolio
- ✅ Low traffic (<1000 visits/day)
- ✅ Can tolerate cold starts
- ✅ Don't need automatic anomaly detection
- ✅ Can run tasks manually
- ✅ Budget is $0

### Upgrade to Paid If:
- ⚠️ Production application
- ⚠️ Need 24/7 uptime
- ⚠️ Need background tasks
- ⚠️ Need automatic anomaly detection
- ⚠️ High traffic (>10,000/day)
- ⚠️ Can't tolerate cold starts
- ⚠️ Budget is $7-35/month

---

## Deployment Checklist

### Before Clicking "Apply"

- [ ] Latest code pushed to GitHub
- [ ] `render.yaml` has workers commented out
- [ ] `.gitignore` includes `.env`, `db.sqlite3`
- [ ] No secrets committed to git

### During Deployment

- [ ] Skip worker service errors
- [ ] Wait for web service to build (5-10 min)
- [ ] Wait for database to create
- [ ] Wait for Redis to create

### After Deployment

- [ ] Set `ALLOWED_HOSTS` environment variable
- [ ] Create superuser in Shell
- [ ] Test admin login
- [ ] Test API endpoints
- [ ] Test Swagger docs
- [ ] Verify IP logging works
- [ ] Test rate limiting

---

## Monitoring Free Tier

### Check Usage

Render Dashboard → Account:
- Instance hours used
- Bandwidth used
- Build minutes used

**Free limits (monthly):**
- 750 instance hours shared
- 100 GB bandwidth
- 500 build minutes

### Performance Expectations

| Metric | Free Tier | Paid Tier |
|--------|-----------|-----------|
| Response Time | ~1000ms (cold start) | ~200ms |
| Response Time | ~300ms (warm) | ~200ms |
| Uptime | 95% (sleeps) | 99.9% |
| Database | Shared | Dedicated |
| Redis | Shared | Dedicated |

---

## Alternative: Run Celery Locally

You can run Celery workers on your local machine or another server:

### Setup

1. **Install dependencies locally:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   # .env
   DATABASE_URL=<render-postgres-url>
   REDIS_URL=<render-redis-url>
   SECRET_KEY=<render-secret-key>
   ```

3. **Run Celery worker:**
   ```bash
   celery -A ip_tracking_project worker -l info
   ```

4. **Run Celery beat:**
   ```bash
   celery -A ip_tracking_project beat -l info
   ```

**Result:** Free Render hosting + local background processing!

---

## Common Issues

### Issue: "Service sleeps after 15 minutes"

**Impact:** First request after sleep takes 50-100ms to wake up

**Solutions:**
1. Accept it (totally fine for demos/portfolios)
2. Use cron-job.org to ping every 10 minutes (keeps it awake)
3. Upgrade to Starter ($7/month, no sleep)

### Issue: "Can't access database from local Celery"

**Solution:** Get external database URL from Render:
1. Dashboard → PostgreSQL → Info
2. Copy "External Database URL"
3. Use in local `.env`

### Issue: "Shared 750 hours = 31 days?"

**Clarification:**
- 750 hours shared across ALL services
- 1 service = 744 hours/month (31 days * 24 hrs)
- 2 services = need 1488 hours (exceeds limit)
- Solution: Services sleep when inactive to save hours

---

## Success Criteria

Your free deployment is successful when:

- [x] Web app loads at your Render URL
- [x] Admin interface accessible
- [x] Swagger docs load
- [x] Can create superuser
- [x] IP logging works
- [x] Rate limiting works
- [x] Geolocation caching works
- [x] Redis connected
- [x] Database persistent
- [x] Static files load

**Congratulations! You have a working production app on 100% free tier!** 🎉

---

## Next Steps

1. **Deploy Now:**
   - Click "Apply" in Render (skip worker errors)
   - Wait for build
   - Set ALLOWED_HOSTS
   - Create superuser
   - Test all features

2. **Test Thoroughly:**
   - Follow [TESTING_GUIDE.md](TESTING_GUIDE.md)
   - Verify all features work
   - Check admin dashboard

3. **Decide on Upgrade:**
   - Use free for 30-90 days
   - Monitor usage and needs
   - Upgrade when ready for production

---

## Support

- **Render Docs:** https://render.com/docs
- **Community Forum:** https://community.render.com
- **Project Docs:** [README.md](README.md)
- **Security:** [SECURITY.md](SECURITY.md)

---

**Remember: Free tier is perfect for development, testing, portfolios, and demos!** 🚀

Upgrade to paid only when you need production-level features and performance.
