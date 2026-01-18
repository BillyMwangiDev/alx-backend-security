# Local Development Setup Guide

## Quick Setup (Automated)

### Option 1: Run Setup Script (Recommended)

```powershell
# From project root
.\setup_local_dev.ps1
```

**If you get an execution policy error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Manual Setup

### 1. Create Virtual Environment

```powershell
# Navigate to project root
cd c:\Users\USER\Desktop\PROJECTS\alx-backend-security

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
# Navigate to ip_tracking_project
cd ip_tracking_project

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Environment Variables (Optional)

For local development, Django will use sensible defaults (SQLite, local memory cache).

If you want to customize, create a `.env` file in the project root:

```bash
# .env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Run Migrations

```powershell
# Still in ip_tracking_project directory
python manage.py migrate
```

### 5. Create Superuser (Optional)

```powershell
python manage.py createsuperuser
```

### 6. Run Development Server

```powershell
python manage.py runserver
```

---

## Fix VS Code/Cursor Import Warnings

The basedpyright import warnings you're seeing mean your IDE can't find the installed packages.

### Configure Python Interpreter

1. **Open Command Palette:** Press `Ctrl+Shift+P`
2. **Select Interpreter:** Type "Python: Select Interpreter"
3. **Choose Virtual Environment:**
   - Look for: `.\venv\Scripts\python.exe`
   - Full path: `c:\Users\USER\Desktop\PROJECTS\alx-backend-security\venv\Scripts\python.exe`

### Reload Window

1. **Open Command Palette:** Press `Ctrl+Shift+P`
2. **Reload:** Type "Developer: Reload Window"
3. **Verify:** Import warnings should disappear

---

## Running the Application

### Development Server

```powershell
cd ip_tracking_project
python manage.py runserver
```

**Access Points:**
- Web App: http://localhost:8000
- Admin Panel: http://localhost:8000/admin
- API Documentation: http://localhost:8000/swagger/
- API Endpoints: http://localhost:8000/api/

### Run Tests

```powershell
python manage.py test
```

### Run Celery Worker (Optional - requires Redis)

**Terminal 1: Redis Server**
```powershell
# Install Redis for Windows or use Docker
docker run -p 6379:6379 redis:alpine
```

**Terminal 2: Celery Worker**
```powershell
cd ip_tracking_project
celery -A ip_tracking_project worker -l info
```

**Terminal 3: Celery Beat (Scheduled Tasks)**
```powershell
cd ip_tracking_project
celery -A ip_tracking_project beat -l info
```

---

## Common Issues

### Issue: Import errors in IDE

**Solution:** 
1. Make sure virtual environment is activated
2. Configure Python interpreter in IDE
3. Reload window

### Issue: ModuleNotFoundError when running code

**Solution:**
```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Then run your command
python manage.py runserver
```

### Issue: Database errors

**Solution:**
```powershell
# Run migrations
python manage.py migrate

# If issues persist, delete db.sqlite3 and re-run
rm db.sqlite3
python manage.py migrate
```

### Issue: Static files not loading

**Solution:**
```powershell
# Collect static files
python manage.py collectstatic --no-input
```

---

## Project Structure

```
alx-backend-security/
├── ip_tracking_project/          # Django project root
│   ├── manage.py                  # Django management script
│   ├── requirements.txt           # Python dependencies
│   ├── settings.py                # Django settings
│   ├── urls.py                    # Project URLs
│   ├── celery_app.py             # Celery configuration
│   └── ip_tracking/              # Main application
│       ├── models.py              # Database models
│       ├── views.py               # View logic
│       ├── tasks.py               # Celery tasks
│       ├── middleware.py          # IP tracking middleware
│       └── admin.py               # Admin interface
├── venv/                         # Virtual environment (created)
├── setup_local_dev.ps1           # Setup script
└── README.md                     # Project documentation
```

---

## Development Workflow

### Daily Workflow

1. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Navigate to project:**
   ```powershell
   cd ip_tracking_project
   ```

3. **Run server:**
   ```powershell
   python manage.py runserver
   ```

### Making Changes

1. **Edit code** in your IDE
2. **Test locally** with `python manage.py runserver`
3. **Run tests** with `python manage.py test`
4. **Commit changes:**
   ```powershell
   git add .
   git commit -m "Your descriptive message"
   git push origin main
   ```

### Database Migrations

When you modify models:

```powershell
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

---

## Resources

- **Django Documentation:** https://docs.djangoproject.com/
- **Django REST Framework:** https://www.django-rest-framework.org/
- **Celery Documentation:** https://docs.celeryq.dev/
- **Python Virtual Environments:** https://docs.python.org/3/tutorial/venv.html

---

## Need Help?

- Check the main [README.md](README.md) for project overview
- See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment
- See [TESTING_GUIDE.md](TESTING_GUIDE.md) for testing instructions
