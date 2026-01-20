# Production Settings Configuration Guide

## Overview

Before deploying to production, you MUST update `cert_tracker/settings.py` to use environment variables instead of hardcoded values. This guide shows you exactly what to change.

---

## Critical Changes Required

### 1. Install Required Packages

First, ensure these are in your `requirements.txt` (already added):
```
python-decouple>=3.8
python-dotenv>=1.0.0
dj-database-url>=2.1.0
whitenoise>=6.6.0
gunicorn>=21.2.0
```

Install them:
```bash
pip install -r requirements.txt
```

---

### 2. Update settings.py

Open `cert_tracker/settings.py` and make these changes:

#### Change #1: Import Required Modules (Line ~13)

**Add after the imports**:
```python
from pathlib import Path
import os
from decouple import config, Csv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
```

#### Change #2: SECRET_KEY (Line ~23)

**FIND**:
```python
SECRET_KEY = 'django-insecure-26#&a59%v3y&%-dq7$-4-jk@do)x0s=ov&te*2k8v3rm(7oqe+'
```

**REPLACE WITH**:
```python
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-26#&a59%v3y&%-dq7$-4-jk@do)x0s=ov&te*2k8v3rm(7oqe+')
```

#### Change #3: DEBUG (Line ~26)

**FIND**:
```python
DEBUG = True
```

**REPLACE WITH**:
```python
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)
```

#### Change #4: ALLOWED_HOSTS (Line ~28)

**FIND**:
```python
ALLOWED_HOSTS = []
```

**REPLACE WITH**:
```python
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())
```

#### Change #5: Add WhiteNoise to MIDDLEWARE (Line ~48)

**FIND**:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
```

**REPLACE WITH** (add WhiteNoise AFTER SecurityMiddleware):
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← ADD THIS LINE
    'django.contrib.sessions.middleware.SessionMiddleware',
```

#### Change #6: Database Configuration (Around Line ~90)

**FIND**:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**REPLACE WITH**:
```python
# Database configuration
# Supports both SQLite (development) and PostgreSQL (production)
DATABASE_URL = config('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}')

DATABASES = {
    'default': dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

#### Change #7: Static Files Configuration (Around Line ~140)

**FIND**:
```python
STATIC_URL = 'static/'
```

**REPLACE WITH**:
```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Additional directories to search for static files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# WhiteNoise configuration for serving static files in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

#### Change #8: Media Files Configuration (Add after STATIC_URL)

**ADD**:
```python
# Media files (User uploaded files)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

#### Change #9: Email Configuration (Around Line ~166)

**FIND**:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production

# SMTP settings for production (uncomment and configure when deploying)
# EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@company.com'
# EMAIL_HOST_PASSWORD = 'your-email-password'  # Use environment variable!
# DEFAULT_FROM_EMAIL = 'Certificate Tracking System <noreply@company.com>'
```

**REPLACE WITH**:
```python
# Email Configuration
# Use environment variables for production
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

# SMTP settings (only used if EMAIL_BACKEND is smtp)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default=f'Aetas Security CTS <{config("EMAIL_HOST_USER", default="noreply@aetassecurity.com")}>'
)
```

#### Change #10: Security Settings (Add at end of file)

**ADD** at the end of `settings.py`:
```python
# Production Security Settings
# These are only enabled when DEBUG=False
if not DEBUG:
    # HTTPS/SSL Settings
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
    CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)

    # HSTS Settings (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
    SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)

    # Content Security
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

    # Referrer Policy
    SECURE_REFERRER_POLICY = 'same-origin'
```

---

## 3. Create .env File

Create a `.env` file in your project root:

```env
# Django Core Settings
SECRET_KEY=your-generated-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
# For SQLite (PythonAnywhere):
DATABASE_URL=sqlite:///db.sqlite3

# For PostgreSQL (Render/Railway/Production):
# DATABASE_URL=postgresql://user:password@host:port/database

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=Aetas Security CTS <your-email@gmail.com>

# Security Settings (Production Only)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

---

## 4. Generate Secure SECRET_KEY

**Never use the default SECRET_KEY in production!**

Generate a new one:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as your SECRET_KEY in `.env`

---

## 5. Update .gitignore

**CRITICAL**: Never commit your `.env` file!

Add to `.gitignore`:
```
# Environment variables
.env
.env.*
!.env.example

# Database
*.sqlite3
db.sqlite3

# Static/Media files
staticfiles/
media/

# Logs
logs/
*.log
```

---

## 6. Test Configuration

### Test Locally

1. **Create .env file**:
```bash
cp .env.example .env
# Edit .env with your values
```

2. **Test with DEBUG=False**:
```bash
python manage.py check --deploy
```

This command shows production security warnings.

3. **Collect static files**:
```bash
python manage.py collectstatic
```

4. **Run development server**:
```bash
python manage.py runserver
```

### Expected Output

```bash
$ python manage.py check --deploy
System check identified no issues (0 silenced).
```

If you see warnings, review them carefully.

---

## 7. Environment-Specific Configuration

### Development (.env.development)
```env
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production (.env.production)
```env
DEBUG=False
SECRET_KEY=your-super-long-random-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:port/database
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=your-production-smtp-password
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 8. Platform-Specific Settings

### PythonAnywhere

**WSGI Configuration** (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):
```python
import os
import sys
from dotenv import load_dotenv

# Add project directory
path = '/home/yourusername/certificate-tracking-system'
if path not in sys.path:
    sys.path.insert(0, path)

# Load environment variables
load_dotenv(os.path.join(path, '.env'))

# Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'cert_tracker.settings'

# Activate virtualenv
activate_this = f'{path}/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### Render

**Environment Variables** (set in Render dashboard):
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=${{RENDER_EXTERNAL_HOSTNAME}}
DATABASE_URL=${{DATABASE_URL}}
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

### Railway

**Environment Variables** (set in Railway dashboard):
```
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
DATABASE_URL=${{DATABASE_URL}}
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
```

---

## 9. Verification Checklist

Before deploying, verify:

- [ ] SECRET_KEY is generated and unique (not default)
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS includes your domain
- [ ] Database is PostgreSQL (not SQLite) for production
- [ ] Static files collect successfully
- [ ] .env file is in .gitignore
- [ ] Environment variables are set on hosting platform
- [ ] Email configuration is tested
- [ ] `python manage.py check --deploy` passes

---

## 10. Troubleshooting

### Issue: "ImproperlyConfigured: The SECRET_KEY setting must not be empty"

**Solution**: Ensure SECRET_KEY is set in .env file or environment variables.

### Issue: "DisallowedHost at /"

**Solution**: Add your domain to ALLOWED_HOSTS:
```env
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Issue: Static files not loading

**Solution**:
1. Check WhiteNoise is in MIDDLEWARE
2. Run `python manage.py collectstatic`
3. Verify STATIC_ROOT is set correctly

### Issue: Database connection failed

**Solution**: Check DATABASE_URL format:
```
postgresql://username:password@hostname:port/database_name
```

### Issue: "Environment variable not found"

**Solution**:
- Ensure .env file exists
- Check python-decouple is installed
- Verify .env is in correct directory (project root)

---

## Summary

After making these changes:

1. ✅ Settings use environment variables
2. ✅ Production-ready security headers
3. ✅ WhiteNoise for static files
4. ✅ PostgreSQL support
5. ✅ Secure secret management
6. ✅ Environment-specific configuration
7. ✅ No hardcoded secrets

Your application is now ready for production deployment!

---

**IMPORTANT**: Always test with DEBUG=False locally before deploying to production.

---

Last Updated: January 20, 2026
