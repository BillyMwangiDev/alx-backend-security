# Deployment Guide - Render Platform

Complete guide for deploying the IP Tracking & Security System to Render with Celery workers and Swagger documentation.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Render Account Setup](#render-account-setup)
3. [Database Configuration](#database-configuration)
4. [Redis Configuration](#redis-configuration)
5. [Environment Variables](#environment-variables)
6. [Deploy Web Service](#deploy-web-service)
7. [Deploy Celery Workers](#deploy-celery-workers)
8. [Verify Deployment](#verify-deployment)
9. [Access Swagger Documentation](#access-swagger-documentation)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- [x] GitHub account with repository access
- [x] Render account (free tier available)
- [x] Git installed locally
- [x] All code committed and pushed to GitHub

---

## Render Account Setup

### 1. Create Render Account

1. Go to [https://render.com/](https://render.com/)
2. Click "Get Started" or "Sign Up"
3. Sign up with GitHub (recommended) or email
4. Verify your email address

### 2. Connect GitHub Repository

1. In Render Dashboard, click "New +"
2. Select "Web Service"
3. Click "Connect account" next to GitHub
4. Authorize Render to access your repositories
5. Select your repository: `alx-backend-security`

---

## Database Configuration

### Create PostgreSQL Database

1. From Render Dashboard, click "New +" → "PostgreSQL"
2. Configure database:
   - **Name:** `ip-tracking-db`
   - **Database:** `ip_tracking_db`
   - **User:** `ip_tracking_user`
   - **Region:** Select closest to your users
   - **Plan:** Free (or Starter for production)
3. Click "Create Database"
4. **Save credentials** (you'll need the Internal Database URL)

**Note:** Keep the Internal Database URL handy - format:
```
postgresql://user:password@hostname:port/database
```

---

## Redis Configuration

### Create Redis Instance

1. From Render Dashboard, click "New +" → "Redis"
2. Configure Redis:
   - **Name:** `ip-tracking-redis`
   - **Region:** Same as your database
   - **Plan:** Free (or Starter for production)
   - **Maxmemory Policy:** `allkeys-lru` (recommended)
3. Click "Create Redis"
4. **Save the Redis URL** (Internal Redis URL)

---

## Environment Variables

### Required Environment Variables

Create a `.env.production` file locally (for reference only - don't commit):

```bash
# Django Settings
SECRET_KEY=<generate-a-secure-random-key-minimum-50-characters>
DEBUG=False
ALLOWED_HOSTS=<your-app-name>.onrender.com

# Database (from Render PostgreSQL)
DATABASE_URL=postgresql://user:password@hostname:port/database

# Redis (from Render Redis)
REDIS_URL=redis://hostname:port

# Optional: RabbitMQ (if using CloudAMQP)
RABBITMQ_URL=amqp://user:password@hostname/vhost

# Security
CSRF_TRUSTED_ORIGINS=https://<your-app-name>.onrender.com
```

### Generate SECRET_KEY

```python
# Run in Python shell
import secrets
print(secrets.token_urlsafe(50))
```

---

## Deploy Web Service

### Step 1: Create Web Service

1. From Render Dashboard, click "New +" → "Web Service"
2. Select your GitHub repository
3. Configure service:
   - **Name:** `ip-tracking-web`
   - **Region:** Same as database
   - **Branch:** `main`
   - **Root Directory:** `ip_tracking_project`
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn ip_tracking_project.wsgi:application`
   - **Plan:** Free (or Starter)

### Step 2: Add Environment Variables

In the web service settings, add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11.0` | Python runtime version |
| `SECRET_KEY` | `<your-secret-key>` | Generate using method above |
| `DEBUG` | `False` | Never True in production |
| `ALLOWED_HOSTS` | `ip-tracking-web.onrender.com` | Your Render URL |
| `DATABASE_URL` | `<postgres-internal-url>` | From PostgreSQL service |
| `REDIS_URL` | `<redis-internal-url>` | From Redis service |

### Step 3: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Pull code from GitHub
   - Install dependencies
   - Run migrations
   - Collect static files
   - Start the application

**Deployment time:** ~5-10 minutes

---

## Deploy Celery Workers

### Option 1: Using render.yaml (Recommended)

The `render.yaml` file in the repository root automatically configures:
- Web service
- Celery worker
- Celery beat scheduler

Render will detect and deploy all services automatically.

### Option 2: Manual Setup

#### Celery Worker Service

1. Click "New +" → "Background Worker"
2. Configure:
   - **Name:** `ip-tracking-celery-worker`
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `celery -A ip_tracking_project worker -l info`
3. Add the same environment variables as web service
4. Click "Create Background Worker"

#### Celery Beat Scheduler

1. Click "New +" → "Background Worker"
2. Configure:
   - **Name:** `ip-tracking-celery-beat`
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `celery -A ip_tracking_project beat -l info`
3. Add the same environment variables
4. Click "Create Background Worker"

---

## Verify Deployment

### 1. Check Web Service

Visit your application URL: `https://your-app-name.onrender.com`

You should see the dashboard.

### 2. Check Admin Interface

1. Visit: `https://your-app-name.onrender.com/admin/`
2. Create superuser (if needed):
   ```bash
   # In Render Shell
   python manage.py createsuperuser
   ```

### 3. Check API Endpoints

Test endpoints:
```bash
# Get request logs
curl https://your-app-name.onrender.com/api/v1/logs/

# Get statistics
curl https://your-app-name.onrender.com/api/v1/logs/stats/

# Get blocked IPs
curl https://your-app-name.onrender.com/api/v1/blocked/
```

### 4. Check Celery Workers

1. Go to Render Dashboard
2. Click on "ip-tracking-celery-worker"
3. Check logs for:
   ```
   [tasks]
     . ip_tracking.tasks.detect_anomalies
   
   [celery ready]
   ```

### 5. Test Background Tasks

The anomaly detection task runs every hour. To test immediately:

```bash
# In Render Shell (web service)
python manage.py shell

# Run task manually
from ip_tracking.tasks import detect_anomalies
result = detect_anomalies.delay()
print(result.status)
```

---

## Access Swagger Documentation

### Public Swagger UI

Once deployed, access interactive API documentation at:

**Swagger UI:** `https://your-app-name.onrender.com/swagger/`

**ReDoc:** `https://your-app-name.onrender.com/redoc/`

**OpenAPI Schema (JSON):** `https://your-app-name.onrender.com/swagger.json`

### Features Available in Swagger

1. **Interactive Testing**
   - Try all API endpoints directly
   - View request/response formats
   - Test with different parameters

2. **Authentication**
   - Test with and without authentication
   - View rate limiting in action

3. **Documentation**
   - Complete endpoint descriptions
   - Request/response schemas
   - Example values

### Share Documentation

Share the Swagger URL with:
- Frontend developers
- API consumers
- Stakeholders
- Documentation

---

## Monitoring & Maintenance

### View Logs

#### Web Service Logs
1. Go to Render Dashboard
2. Click "ip-tracking-web"
3. Click "Logs" tab
4. View real-time logs

#### Celery Worker Logs
1. Go to "ip-tracking-celery-worker"
2. Click "Logs" tab
3. Monitor task execution

### Metrics

Render provides:
- CPU usage
- Memory usage
- Request count
- Response times

Access via service dashboard.

### Database Management

```bash
# Connect to PostgreSQL
# Get connection string from Render dashboard

# Using psql
psql $DATABASE_URL

# View tables
\dt

# Check request logs count
SELECT COUNT(*) FROM ip_tracking_requestlog;
```

### Redis Management

```bash
# Connect to Redis
redis-cli -u $REDIS_URL

# Check keys
KEYS *

# Check cache hit rate
INFO stats
```

---

## Troubleshooting

### Issue: Deployment Failed

**Solution:**
1. Check build logs in Render
2. Verify `build.sh` is executable:
   ```bash
   chmod +x ip_tracking_project/build.sh
   ```
3. Check requirements.txt for syntax errors

### Issue: Static Files Not Loading

**Solution:**
1. Verify WhiteNoise is in MIDDLEWARE
2. Run collectstatic manually:
   ```bash
   python manage.py collectstatic --no-input
   ```
3. Check `STATICFILES_STORAGE` setting

### Issue: Database Connection Error

**Solution:**
1. Verify DATABASE_URL is correct
2. Check PostgreSQL service is running
3. Ensure database accepts connections from web service
4. Verify `psycopg2-binary` is installed

### Issue: Celery Worker Not Processing Tasks

**Solution:**
1. Check REDIS_URL is correct
2. Verify Celery worker is running
3. Check worker logs for errors
4. Test Redis connection:
   ```python
   from django.core.cache import cache
   cache.set('test', 'value')
   print(cache.get('test'))
   ```

### Issue: Swagger Not Accessible

**Solution:**
1. Verify `drf-yasg` is in INSTALLED_APPS
2. Check URLs are configured correctly
3. Ensure `rest_framework` is installed
4. Clear browser cache and try again

### Issue: Rate Limiting Not Working

**Solution:**
1. Verify Redis is running
2. Check REDIS_URL in environment
3. Test Redis cache configuration
4. Check rate limit settings in views

### Issue: Geolocation Not Working

**Solution:**
Geolocation gracefully falls back if unavailable. To enable:
1. Verify geoip2 packages are installed
2. Check middleware error logs
3. Ensure IP addresses are valid

---

## Production Checklist

Before going to production:

- [ ] Set `DEBUG=False`
- [ ] Generated strong `SECRET_KEY`
- [ ] Configured proper `ALLOWED_HOSTS`
- [ ] Set up PostgreSQL database
- [ ] Configured Redis caching
- [ ] Deployed Celery workers
- [ ] Verified all environment variables
- [ ] Tested all API endpoints
- [ ] Verified Swagger documentation works
- [ ] Set up monitoring and alerts
- [ ] Configured proper logging
- [ ] Set up backup strategy
- [ ] Reviewed security settings
- [ ] Updated privacy policy
- [ ] Tested rate limiting
- [ ] Verified anomaly detection
- [ ] Created superuser account
- [ ] Documented deployment process

---

## Performance Optimization

### Database Optimization

```bash
# Create indexes for better performance
python manage.py dbshell

CREATE INDEX idx_requestlog_ip ON ip_tracking_requestlog(ip_address);
CREATE INDEX idx_requestlog_timestamp ON ip_tracking_requestlog(timestamp);
CREATE INDEX idx_blockedip_ip ON ip_tracking_blockedip(ip_address);
```

### Caching Strategy

- Geolocation: 24 hours
- Rate limits: 1 minute
- API responses: 5 minutes (optional)

### Scaling

For high traffic:
1. Upgrade to Render Starter or Pro plan
2. Add more Celery workers
3. Upgrade PostgreSQL plan
4. Upgrade Redis plan
5. Enable connection pooling
6. Implement API caching

---

## Costs

### Free Tier Limitations

**Render Free Tier includes:**
- 750 hours/month (enough for one 24/7 service)
- 512MB RAM
- Automatic sleep after 15 min of inactivity
- Slower build times

**Recommended for Production:**
- Starter plan ($7/month per service)
- Always-on services
- More resources
- Faster builds

---

## Next Steps

1. **Monitor application** - Check logs regularly
2. **Set up alerts** - Configure email/Slack notifications
3. **Add custom domain** - Configure DNS
4. **Enable HTTPS** - Automatic with Render
5. **Implement authentication** - Add user authentication
6. **Add more tests** - Increase test coverage
7. **Performance testing** - Load test the application
8. **Security audit** - Regular security reviews

---

## Support Resources

- **Render Documentation:** [https://render.com/docs](https://render.com/docs)
- **Django Documentation:** [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **Celery Documentation:** [https://docs.celeryproject.org/](https://docs.celeryproject.org/)
- **Swagger Documentation:** [https://swagger.io/docs/](https://swagger.io/docs/)

---

## Useful Commands

### Render Shell Access

```bash
# Access shell in web service
# Go to Render Dashboard → Service → Shell tab

# Common commands
python manage.py shell
python manage.py dbshell
python manage.py createsuperuser
python manage.py migrate
python manage.py collectstatic
```

### Git Deployment

```bash
# Trigger redeployment
git push origin main

# Render automatically:
# 1. Detects changes
# 2. Runs build
# 3. Deploys new version
```

---

**Deployment Date:** January 18, 2026  
**Version:** 1.0.0  
**Author:** Billy Mwangi  
**Repository:** [alx-backend-security](https://github.com/BillyMwangiDev/alx-backend-security)
