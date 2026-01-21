# Development Setup Guide

## Quick Start

Your development environment is now ready to use!

### Start the Development Server

**Option 1: Using Batch Script (Recommended)**
```bash
# Just double-click this file:
run_dev_server.bat
```

**Option 2: Using PowerShell Script**
```powershell
# Right-click run_dev_server.ps1 → Run with PowerShell
# Or in PowerShell:
.\run_dev_server.ps1
```

**Option 3: Manual Commands**
```bash
# Activate virtual environment
venv\Scripts\activate

# Run development server
python manage.py runserver
```

### Access Your Application

Once the server is running, open your browser and visit:
```
http://127.0.0.1:8000/
```

Or:
```
http://localhost:8000/
```

---

## What Was Set Up

✅ **Virtual Environment** - Created at `venv/`
✅ **Dependencies Installed** - All packages from `requirements-pythonanywhere.txt`
✅ **Local .env File** - Configured for development with `DEBUG=True`
✅ **Database Migrations** - Applied and ready to use
✅ **Helper Scripts** - Easy server startup scripts created

---

## Development vs Production

### Development Branch (Local)
- **Branch**: `development`
- **Environment**: `.env` file with `DEBUG=True`
- **Database**: SQLite (`db.sqlite3`)
- **Email**: Console backend (prints to terminal)
- **Server**: Django development server (`runserver`)
- **URL**: `http://localhost:8000/`

### Production (PythonAnywhere)
- **Branch**: `main`
- **Environment**: `.env` file with `DEBUG=False`
- **Database**: SQLite (but could be PostgreSQL)
- **Email**: SMTP backend (real emails via Gmail)
- **Server**: WSGI server (uWSGI/Gunicorn)
- **URL**: `https://larenzzx.pythonanywhere.com`

---

## Common Development Tasks

### Run Development Server
```bash
python manage.py runserver
```

### Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### Make Database Migrations
```bash
# After changing models
python manage.py makemigrations
python manage.py migrate
```

### Collect Static Files (if DEBUG=False)
```bash
python manage.py collectstatic
```

### Run Django Shell
```bash
python manage.py shell
```

### Check for Issues
```bash
python manage.py check
```

### Run Tests (when you create them)
```bash
python manage.py test
```

---

## Git Workflow

### Working on Development Branch

1. **Make sure you're on development branch**:
   ```bash
   git branch
   # Should show * development
   ```

2. **Make your changes** (edit code, add features)

3. **Test locally**:
   ```bash
   python manage.py runserver
   # Visit http://localhost:8000/ and test
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Describe what you changed"
   ```

5. **Push to GitHub**:
   ```bash
   git push origin development
   ```

### Deploying to Production

When your changes are tested and ready:

1. **Switch to main branch**:
   ```bash
   git checkout main
   ```

2. **Merge development into main**:
   ```bash
   git merge development
   ```

3. **Push to GitHub**:
   ```bash
   git push origin main
   ```

4. **Update PythonAnywhere**:
   - Go to PythonAnywhere bash console
   - Run:
     ```bash
     cd ~/Aetas-Security---Certificate-Tracking-System
     git pull origin main
     ```
   - Go to Web tab and click **Reload**

---

## Environment Variables (.env)

Your local `.env` file contains:

```env
DEBUG=True                          # Development mode
SECRET_KEY=...                      # Safe default for local
ALLOWED_HOSTS=localhost,127.0.0.1   # Local addresses
DATABASE_URL=sqlite:///db.sqlite3   # Local SQLite database
EMAIL_BACKEND=console               # Emails print to terminal
```

**Never commit your .env file to Git!** (Already in .gitignore)

---

## Troubleshooting

### Issue: "Command not found: python"

**Solution**: Make sure virtual environment is activated:
```bash
venv\Scripts\activate
```

### Issue: Static files not loading

**Solution**: For development with `DEBUG=True`, Django serves static files automatically. If you set `DEBUG=False`, run:
```bash
python manage.py collectstatic
```

### Issue: "Port 8000 is already in use"

**Solution**: Either:
- Stop the other server running on port 8000
- Or use a different port:
  ```bash
  python manage.py runserver 8001
  ```

### Issue: Database errors after pulling changes

**Solution**: Run migrations:
```bash
python manage.py migrate
```

### Issue: ImportError or ModuleNotFoundError

**Solution**: Reinstall dependencies:
```bash
pip install -r requirements-pythonanywhere.txt
```

---

## File Structure

```
Certificate Tracking System/
├── venv/                      # Virtual environment (don't commit)
├── accounts/                  # User accounts app
├── certificates/              # Certificates app
├── dashboard/                 # Dashboard app
├── core/                      # Core utilities (middleware, validators)
├── cert_tracker/              # Project settings
├── templates/                 # HTML templates
├── static/                    # Static files (CSS, JS, images)
├── staticfiles/               # Collected static files (generated)
├── media/                     # User uploads (profile photos, etc.)
├── logs/                      # Application logs
├── .env                       # Environment variables (LOCAL - don't commit)
├── .gitignore                 # Files to ignore in Git
├── manage.py                  # Django management script
├── requirements-pythonanywhere.txt  # Python dependencies
├── run_dev_server.bat         # Quick server start (Windows)
├── run_dev_server.ps1         # Quick server start (PowerShell)
└── DEV_SETUP.md               # This file
```

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| **Start server** | `python manage.py runserver` |
| **Check for issues** | `python manage.py check` |
| **Create admin user** | `python manage.py createsuperuser` |
| **Make migrations** | `python manage.py makemigrations` |
| **Apply migrations** | `python manage.py migrate` |
| **Django shell** | `python manage.py shell` |
| **Collect static files** | `python manage.py collectstatic` |
| **Switch to dev branch** | `git checkout development` |
| **Switch to main branch** | `git checkout main` |
| **Push changes** | `git push origin development` |
| **Pull latest changes** | `git pull origin development` |

---

## Next Steps

1. **Start the server**: Double-click `run_dev_server.bat`
2. **Visit your site**: http://localhost:8000/
3. **Login**: Use the superuser account you created
4. **Start coding**: Make changes and test locally
5. **Commit often**: Save your work with Git
6. **Deploy when ready**: Merge to main and update PythonAnywhere

---

## Getting Help

- **Django Documentation**: https://docs.djangoproject.com/
- **Django Tutorial**: https://docs.djangoproject.com/en/5.2/intro/tutorial01/
- **Python Decouple**: https://github.com/HBNetwork/python-decouple
- **DaisyUI Components**: https://daisyui.com/components/
- **Tailwind CSS**: https://tailwindcss.com/docs

---

**Happy Coding! 🚀**

---

Last Updated: January 21, 2026
