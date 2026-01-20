# Free Deployment Guide - Certificate Tracking System

## Overview

This guide will walk you through deploying your Django Certificate Tracking System to the internet for **FREE**. We'll cover multiple free hosting options and provide step-by-step instructions.

**Estimated Time**: 30-60 minutes

---

## 🎯 Best Free Hosting Options

| Platform | Pros | Cons | Best For |
|----------|------|------|----------|
| **PythonAnywhere** | Easiest setup, Django-friendly | Limited bandwidth | Beginners |
| **Render** | Modern, auto-deploy from Git | Cold starts on free tier | Small teams |
| **Railway** | Generous free tier, PostgreSQL included | $5 credit/month limit | Development/Testing |
| **Heroku** | Popular, well-documented | Dynos sleep after 30 min | General use |

**Recommendation**: Start with **PythonAnywhere** (easiest) or **Render** (most modern).

---

## Option 1: PythonAnywhere (Recommended for Beginners)

### Why PythonAnywhere?
- ✅ Easiest Django deployment
- ✅ No credit card required
- ✅ Free SSL certificate
- ✅ 512MB storage
- ✅ Always-on (no cold starts)
- ❌ Limited to 100k requests/day
- ❌ Custom domain requires paid plan ($5/month)

### Prerequisites

1. **Create PythonAnywhere Account**
   - Go to: https://www.pythonanywhere.com/
   - Click "Start running Python online in less than a minute"
   - Sign up for **FREE Beginner account**

2. **Prepare Your Code**
   - Your code should be in a Git repository (GitHub recommended)
   - If not already on GitHub, create a repository and push your code

### Step-by-Step Deployment

#### Step 1: Open PythonAnywhere Console

1. Login to PythonAnywhere
2. Click **"Consoles"** tab
3. Click **"Bash"** to open a console

#### Step 2: Clone Your Repository

```bash
# Clone your repository
git clone https://github.com/yourusername/certificate-tracking-system.git
cd certificate-tracking-system
```

**If your code is NOT on GitHub yet:**
```bash
# In your local machine, first push to GitHub
cd "C:\Users\MarkTabotabo\OneDrive - Aetas Security LLC\Aetas Security\Certificate Tracking System"
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main
```

#### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

```bash
# Create .env file
nano .env
```

**Add these variables** (press Ctrl+O to save, Ctrl+X to exit):
```env
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here-change-this
ALLOWED_HOSTS=yourusername.pythonanywhere.com

# Database (SQLite for free tier)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration (use Gmail)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

**Generate a secure SECRET_KEY**:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Step 5: Install python-decouple

```bash
pip install python-decouple
```

#### Step 6: Update settings.py

Update `cert_tracker/settings.py`:

```python
from decouple import config
import os

# Security Settings
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f'Aetas Security CTS <{config("EMAIL_HOST_USER")}>'
```

#### Step 7: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

#### Step 8: Run Migrations

```bash
python manage.py migrate
```

#### Step 9: Create Superuser

```bash
python manage.py createsuperuser
```

#### Step 10: Configure Web App in PythonAnywhere

1. Go to **"Web"** tab in PythonAnywhere
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"** (NOT Django)
4. Choose **Python 3.10**

#### Step 11: Configure WSGI File

1. In the Web tab, click on **WSGI configuration file** link
2. **Delete all content** and replace with:

```python
import os
import sys

# Add your project directory to the sys.path
path = '/home/yourusername/certificate-tracking-system'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'cert_tracker.settings'

# Load environment variables from .env
from dotenv import load_dotenv
project_folder = os.path.expanduser(path)
load_dotenv(os.path.join(project_folder, '.env'))

# Activate virtual environment
activate_this = '/home/yourusername/certificate-tracking-system/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Replace `yourusername` with your actual PythonAnywhere username!**

#### Step 12: Configure Virtual Environment

1. In the Web tab, scroll to **"Virtualenv"** section
2. Enter: `/home/yourusername/certificate-tracking-system/venv`
3. Click checkmark

#### Step 13: Configure Static Files

1. In the Web tab, scroll to **"Static files"** section
2. Add these mappings:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/certificate-tracking-system/staticfiles` |
| `/media/` | `/home/yourusername/certificate-tracking-system/media` |

#### Step 14: Reload Web App

1. Scroll to top of Web tab
2. Click green **"Reload"** button
3. Wait 30 seconds

#### Step 15: Test Your Site

1. Visit: `https://yourusername.pythonanywhere.com`
2. ✅ You should see your login page!

### Troubleshooting

**Error 1: "Import Error"**
- Check WSGI file has correct username
- Check virtual environment path is correct
- Reload web app

**Error 2: "502 Bad Gateway"**
- Check error log in Web tab
- Common issue: wrong DJANGO_SETTINGS_MODULE path

**Error 3: Static files not loading**
- Run `python manage.py collectstatic` again
- Check static file mappings in Web tab
- Hard refresh browser (Ctrl+Shift+R)

---

## Option 2: Render (Modern, Auto-Deploy)

### Why Render?
- ✅ Modern platform
- ✅ Auto-deploy from GitHub
- ✅ Free SSL certificate
- ✅ Free PostgreSQL database
- ✅ Custom domain on free tier
- ❌ Services sleep after 15 min inactivity (cold starts)
- ❌ Free tier has limited hours

### Prerequisites

1. **GitHub Account** - Your code must be on GitHub
2. **Render Account** - Sign up at https://render.com/

### Step-by-Step Deployment

#### Step 1: Prepare Your Project

Create `build.sh` in project root:

```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
```

Make it executable:
```bash
chmod +x build.sh
```

#### Step 2: Update requirements.txt

Add these to `requirements.txt`:
```
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-decouple==3.8
whitenoise==6.6.0
```

#### Step 3: Update settings.py

Add to `cert_tracker/settings.py`:

```python
from decouple import config
import dj_database_url

# Security
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Static Files (WhiteNoise)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    # ... rest of middleware
]

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

#### Step 4: Push to GitHub

```bash
git add .
git commit -m "Configure for Render deployment"
git push
```

#### Step 5: Create Render Web Service

1. Login to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: certificate-tracking-system
   - **Environment**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn cert_tracker.wsgi:application`
   - **Instance Type**: Free

#### Step 6: Add Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=(auto-generated by Render PostgreSQL)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

#### Step 7: Create PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: certificate-tracking-db
   - **Database**: cts_db
   - **User**: cts_user
   - **Instance Type**: Free
3. Click **"Create Database"**
4. Copy the **Internal Database URL**

#### Step 8: Link Database to Web Service

1. Go back to your Web Service
2. In **Environment** tab
3. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: (paste Internal Database URL)

#### Step 9: Deploy

1. Click **"Manual Deploy"** → **"Deploy latest commit"**
2. Wait 5-10 minutes for build
3. Visit your site: `https://your-app-name.onrender.com`

#### Step 10: Create Superuser

1. In Render dashboard, click **"Shell"** tab
2. Run:
```bash
python manage.py createsuperuser
```

### Render Troubleshooting

**Error: Build failed**
- Check build.sh has correct syntax
- Check requirements.txt has all dependencies
- View logs in Render dashboard

**Error: Database connection failed**
- Check DATABASE_URL is set correctly
- Use Internal Database URL (not External)
- Ensure database instance is running

---

## Option 3: Railway (Best Free PostgreSQL)

### Why Railway?
- ✅ Generous $5 free credit/month
- ✅ PostgreSQL included
- ✅ Simple deployment
- ✅ No cold starts
- ❌ Requires credit card (not charged on free tier)

### Step-by-Step Deployment

#### Step 1: Sign Up

1. Go to: https://railway.app/
2. Sign up with GitHub

#### Step 2: Create New Project

1. Click **"New Project"**
2. Choose **"Deploy from GitHub repo"**
3. Select your repository

#### Step 3: Add PostgreSQL

1. In project dashboard, click **"New"**
2. Choose **"Database"** → **"PostgreSQL"**
3. PostgreSQL service will be created

#### Step 4: Configure Environment Variables

1. Click on your web service
2. Go to **"Variables"** tab
3. Click **"RAW Editor"** and paste:

```
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

#### Step 5: Add Build Configuration

Create `railway.toml` in project root:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn cert_tracker.wsgi:application"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

#### Step 6: Deploy

1. Push to GitHub
2. Railway auto-deploys
3. Wait for build to complete
4. Click **"Generate Domain"** to get public URL

---

## Production Checklist

Before going live, ensure:

### Security
- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` (50+ random characters)
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] HTTPS enabled (most platforms auto-provide)
- [ ] Environment variables not committed to Git

### Database
- [ ] Migrations run successfully
- [ ] Database backup strategy in place
- [ ] PostgreSQL for production (not SQLite)

### Static Files
- [ ] `collectstatic` runs successfully
- [ ] Static files accessible at /static/
- [ ] Media files accessible at /media/

### Email
- [ ] Email backend configured for production
- [ ] Gmail App Password or SMTP credentials set
- [ ] Test password reset email

### Users
- [ ] Superuser created
- [ ] Test user login
- [ ] Test user registration (if enabled)

### Testing
- [ ] Homepage loads
- [ ] Login works
- [ ] Dashboard displays
- [ ] Certificate CRUD works
- [ ] Profile photos upload/display
- [ ] Password reset works

---

## Updating Your Deployed App

### PythonAnywhere
```bash
# SSH into PythonAnywhere console
cd ~/certificate-tracking-system
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Reload web app from Web tab
```

### Render / Railway
```bash
# Just push to GitHub
git add .
git commit -m "Update feature"
git push

# Auto-deploys! 🎉
```

---

## Custom Domain Setup

### PythonAnywhere (Requires Paid Plan)
1. Upgrade to Hacker plan ($5/month)
2. Go to Web tab → Add custom domain
3. Update DNS records at your domain registrar

### Render (Free!)
1. Go to Settings tab
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records:
   - Type: CNAME
   - Name: www
   - Value: your-app.onrender.com

### Railway (Free!)
1. Click on service
2. Go to Settings
3. Add custom domain
4. Update DNS records

---

## Monitoring & Logs

### PythonAnywhere
- **Error Log**: Web tab → Error log file
- **Server Log**: Web tab → Server log file
- **Access Log**: Web tab → Access log file

### Render
- **Logs**: Logs tab in dashboard
- **Metrics**: Metrics tab shows CPU/Memory
- **Alerts**: Configure in Settings

### Railway
- **Logs**: Deployments → View logs
- **Metrics**: Metrics tab
- **Observability**: Integrated logging

---

## Cost Comparison

| Platform | Free Tier | Paid Tier | When to Upgrade |
|----------|-----------|-----------|-----------------|
| PythonAnywhere | Always-on, 512MB | $5/mo (custom domain) | Need custom domain |
| Render | 750 hours/mo | $7/mo (always-on) | High traffic |
| Railway | $5 credit/mo | $5-20/mo | Credit runs out |
| Heroku | Dyno sleeps | $7/mo (Eco) | Need always-on |

**Recommendation**: Start free, upgrade when needed.

---

## Database Backup

### PythonAnywhere (SQLite)
```bash
# Download database file
# From Web → Files → db.sqlite3 → Download
```

### Render/Railway (PostgreSQL)
```bash
# Export database
pg_dump $DATABASE_URL > backup.sql

# Import backup
psql $DATABASE_URL < backup.sql
```

**Setup automatic backups** (recommended):
```bash
# Add to cron job (daily backups)
0 2 * * * pg_dump $DATABASE_URL > /path/to/backup/cts_$(date +\%Y\%m\%d).sql
```

---

## Common Issues

### Issue 1: "Disallowed Host"
**Error**: `Invalid HTTP_HOST header: 'xyz.com'. You may need to add 'xyz.com' to ALLOWED_HOSTS.`

**Solution**: Add domain to ALLOWED_HOSTS in settings.py or environment variable:
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

### Issue 2: "No module named 'cert_tracker'"
**Error**: Import error for Django settings

**Solution**: Check DJANGO_SETTINGS_MODULE path:
```bash
export DJANGO_SETTINGS_MODULE=cert_tracker.settings
```

### Issue 3: Static files not loading
**Error**: CSS/JS not applying

**Solution**:
```bash
python manage.py collectstatic --noinput
```

Add WhiteNoise to middleware in settings.py

### Issue 4: Database connection failed
**Error**: `OperationalError: could not connect to server`

**Solution**: Check DATABASE_URL environment variable is set correctly

### Issue 5: "Server Error (500)"
**Error**: Generic 500 error

**Solution**:
1. Check logs for details
2. Set DEBUG=True temporarily to see error
3. Check database migrations are run
4. Check SECRET_KEY is set

---

## Next Steps After Deployment

1. **Configure Email**: Follow EMAIL_CONFIGURATION_GUIDE.md
2. **Add Users**: Create employee accounts
3. **Import Certificates**: Add certificate data
4. **Setup Backups**: Configure automatic database backups
5. **Monitor Logs**: Check logs daily for errors
6. **Update Dependencies**: Keep packages updated

---

## Support Resources

### Documentation
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
- PythonAnywhere: https://help.pythonanywhere.com/
- Render: https://render.com/docs
- Railway: https://docs.railway.app/

### Helpful Communities
- Django Forum: https://forum.djangoproject.com/
- Stack Overflow: https://stackoverflow.com/questions/tagged/django
- Reddit: r/django

---

## Summary

You now have multiple options for deploying your Certificate Tracking System for free:

| Best For | Use This |
|----------|----------|
| Beginners, Simple Setup | **PythonAnywhere** |
| Modern, Auto-Deploy | **Render** |
| Best Free Database | **Railway** |
| Popular, Well-Documented | **Heroku** |

**Recommended Path**:
1. Start with **PythonAnywhere** (easiest)
2. If you need custom domain, switch to **Render**
3. If you need always-on + PostgreSQL, use **Railway**

**Total Time**: 30-60 minutes
**Cost**: $0 (free tier)
**Difficulty**: Beginner-friendly

---

**Good luck with your deployment! 🚀**

---

Last Updated: January 20, 2026
