# Deployment Documentation - Quick Reference

## 📚 Documentation Index

This folder contains everything you need to deploy your Certificate Tracking System to production.

---

## 🚀 Quick Start (Choose Your Path)

### Path 1: Fast Deploy (30 minutes)
**Best for**: Quick testing, beginners

1. Read: **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** (5-minute guide)
2. Follow: PythonAnywhere setup
3. Done! ✅

### Path 2: Full Production Deploy (1-2 hours)
**Best for**: Production-ready deployment

1. Read: **[DEPLOYMENT_GUIDE_FREE_HOSTING.md](DEPLOYMENT_GUIDE_FREE_HOSTING.md)** (comprehensive)
2. Read: **[PRODUCTION_SETTINGS_GUIDE.md](PRODUCTION_SETTINGS_GUIDE.md)** (configure settings)
3. Follow: **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** (verify everything)
4. Done! ✅

### Path 3: Email Setup Only
**Already deployed? Just need email?**

1. Read: **[QUICK_EMAIL_SETUP.md](QUICK_EMAIL_SETUP.md)** (2 minutes)
2. Or: **[EMAIL_CONFIGURATION_GUIDE.md](EMAIL_CONFIGURATION_GUIDE.md)** (comprehensive)
3. Done! ✅

---

## 📖 Document Descriptions

### Main Deployment Guides

| Document | Purpose | Time | Audience |
|----------|---------|------|----------|
| **[DEPLOYMENT_GUIDE_FREE_HOSTING.md](DEPLOYMENT_GUIDE_FREE_HOSTING.md)** | Complete deployment guide for 4 platforms | 60 min | Everyone |
| **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** | Fast PythonAnywhere deployment | 5 min | Beginners |
| **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** | Complete pre-flight checklist | 30 min | Before go-live |

### Configuration Guides

| Document | Purpose | Time | When Needed |
|----------|---------|------|-------------|
| **[PRODUCTION_SETTINGS_GUIDE.md](PRODUCTION_SETTINGS_GUIDE.md)** | Configure settings.py for production | 30 min | Before deployment |
| **[EMAIL_CONFIGURATION_GUIDE.md](EMAIL_CONFIGURATION_GUIDE.md)** | Comprehensive email setup | 15 min | Password reset needed |
| **[QUICK_EMAIL_SETUP.md](QUICK_EMAIL_SETUP.md)** | Fast Gmail setup | 2 min | Quick email test |

### Reference Files

| File | Purpose |
|------|---------|
| **[build.sh](build.sh)** | Build script for Render/Railway |
| **[railway.toml](railway.toml)** | Railway configuration |
| **[.env.example](.env.example)** | Environment variables template |
| **[requirements.txt](requirements.txt)** | Python dependencies (production-ready) |

---

## 🎯 Choose Your Hosting Platform

### PythonAnywhere (Easiest)
- ✅ Best for beginners
- ✅ No credit card needed
- ✅ Always-on (no sleep)
- ✅ Free SSL certificate
- ❌ No custom domain on free tier
- ❌ 100k requests/day limit

**Guide**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md) or [DEPLOYMENT_GUIDE_FREE_HOSTING.md](DEPLOYMENT_GUIDE_FREE_HOSTING.md#option-1-pythonanywhere-recommended-for-beginners)

### Render (Modern)
- ✅ Custom domain on free tier
- ✅ Auto-deploy from GitHub
- ✅ Free PostgreSQL database
- ✅ Modern interface
- ❌ Cold starts after 15 min
- ❌ Limited free hours

**Guide**: [DEPLOYMENT_GUIDE_FREE_HOSTING.md](DEPLOYMENT_GUIDE_FREE_HOSTING.md#option-2-render-modern-auto-deploy)

### Railway (Best Database)
- ✅ Best free PostgreSQL
- ✅ $5 free credit/month
- ✅ No cold starts
- ✅ Custom domains
- ❌ Requires credit card
- ❌ Credit limit

**Guide**: [DEPLOYMENT_GUIDE_FREE_HOSTING.md](DEPLOYMENT_GUIDE_FREE_HOSTING.md#option-3-railway-best-free-postgresql)

---

## ✅ Pre-Deployment Checklist

Before you start deploying, make sure:

- [ ] Code is on GitHub
- [ ] All features tested locally
- [ ] Email provider chosen (Gmail/Outlook/SMTP)
- [ ] Read relevant deployment guide
- [ ] `.env` file not committed to Git
- [ ] `requirements.txt` is up to date

---

## 🔐 Security Preparation

### 1. Update settings.py
Follow: **[PRODUCTION_SETTINGS_GUIDE.md](PRODUCTION_SETTINGS_GUIDE.md)**

Key changes:
- SECRET_KEY from environment variable
- DEBUG = False
- ALLOWED_HOSTS configured
- Database from environment
- WhiteNoise for static files

### 2. Generate SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Create .env file
Copy from **[.env.example](.env.example)** and fill in your values.

### 4. Security Review
See: **[SECURITY_HARDENING_STEP12.md](SECURITY_HARDENING_STEP12.md)**

---

## 📧 Email Configuration

### Quick Gmail Setup (2 minutes)
1. Get App Password: https://myaccount.google.com/apppasswords
2. Follow: **[QUICK_EMAIL_SETUP.md](QUICK_EMAIL_SETUP.md)**

### Other Email Providers
Follow: **[EMAIL_CONFIGURATION_GUIDE.md](EMAIL_CONFIGURATION_GUIDE.md)**

Options:
- Gmail (recommended for testing)
- Outlook/Office 365
- Company SMTP server
- SendGrid (production)

---

## 🚦 Deployment Steps Overview

### Step 1: Prepare Code
```bash
# Update requirements.txt (already done)
pip install -r requirements.txt

# Update settings.py for production
# Follow: PRODUCTION_SETTINGS_GUIDE.md

# Test locally
python manage.py check --deploy
python manage.py collectstatic
```

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 3: Choose Platform & Deploy
- **PythonAnywhere**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
- **Render**: [DEPLOYMENT_GUIDE_FREE_HOSTING.md](DEPLOYMENT_GUIDE_FREE_HOSTING.md#option-2-render-modern-auto-deploy)
- **Railway**: [DEPLOYMENT_GUIDE_FREE_HOSTING.md](DEPLOYMENT_GUIDE_FREE_HOSTING.md#option-3-railway-best-free-postgresql)

### Step 4: Configure Environment
Set environment variables on your platform:
```env
SECRET_KEY=your-generated-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=your-database-url
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 5: Run Migrations
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Step 6: Test Deployment
Follow: **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** Phase 4: Post-Deployment Testing

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Site not loading
- Check error logs on platform
- Verify environment variables are set
- Check ALLOWED_HOSTS includes your domain

**Issue**: Static files not loading
- Run `python manage.py collectstatic`
- Check WhiteNoise is in MIDDLEWARE
- Verify STATIC_ROOT is configured

**Issue**: Database connection error
- Check DATABASE_URL format
- Verify database is running
- Check connection string is correct

**Issue**: Email not sending
- Verify EMAIL_BACKEND is set to smtp
- Check Gmail App Password (not regular password)
- Test email settings: [EMAIL_CONFIGURATION_GUIDE.md](EMAIL_CONFIGURATION_GUIDE.md)

**Issue**: "DisallowedHost" error
- Add your domain to ALLOWED_HOSTS in .env
- Restart the application

**More troubleshooting**: See respective deployment guides

---

## 📊 Post-Deployment

### Testing
Use: **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** Phase 4

Key tests:
- Login/logout
- Password reset
- Certificate CRUD
- User management
- Profile photos
- Email notifications

### Monitoring
- Check error logs daily
- Monitor disk space
- Test backups weekly
- Update dependencies monthly

### Maintenance
See: **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** Phase 8

---

## 🆘 Getting Help

### Documentation
1. Check relevant guide above
2. Review error logs on platform
3. Search Django documentation: https://docs.djangoproject.com/

### Platform Support
- **PythonAnywhere**: https://help.pythonanywhere.com/
- **Render**: https://render.com/docs
- **Railway**: https://docs.railway.app/

### Community
- Django Forum: https://forum.djangoproject.com/
- Stack Overflow: https://stackoverflow.com/questions/tagged/django

---

## 📝 Quick Reference

### Generate SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Run Migrations
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Check Deployment
```bash
python manage.py check --deploy
```

### View Logs (PythonAnywhere)
```bash
tail -f ~/logs/error.log
```

### Database Backup
```bash
python manage.py dumpdata > backup.json
```

### Database Restore
```bash
python manage.py loaddata backup.json
```

---

## 📅 Typical Deployment Timeline

### First-Time Deployment
- **Preparation**: 30 minutes
- **Platform setup**: 20 minutes
- **Configuration**: 15 minutes
- **Testing**: 20 minutes
- **Total**: ~90 minutes

### Quick Re-Deploy
- **Code changes**: Push to GitHub
- **Auto-deploy**: 5-10 minutes
- **Verification**: 5 minutes
- **Total**: ~15 minutes

---

## ✨ Success Criteria

Your deployment is successful when:

✅ Site loads at public URL
✅ Login works
✅ Dashboard displays correctly
✅ Certificates can be created/edited/deleted
✅ Profile photos upload and display
✅ Password reset email received
✅ Static files (CSS/JS) load
✅ No console errors
✅ All tests pass

---

## 🎉 Congratulations!

Once deployed, your Certificate Tracking System will be:

- 🌐 Accessible from anywhere
- 🔒 Secure with HTTPS
- 📧 Sending real emails
- 💾 Backed by production database
- 📊 Tracking all user activity
- ✅ Production-ready

---

## 📚 Additional Resources

### Security Documentation
- **[SECURITY_HARDENING_STEP12.md](SECURITY_HARDENING_STEP12.md)** - Security features implemented
- **[BUG_FIXES_PASSWORD_AND_DELETE.md](BUG_FIXES_PASSWORD_AND_DELETE.md)** - Recent bug fixes

### Feature Documentation
- **[STEP_12_SUMMARY.md](STEP_12_SUMMARY.md)** - Latest features
- User guides (in respective feature documentation)

---

## 💡 Tips for Success

1. **Start simple**: Deploy to PythonAnywhere first
2. **Test locally**: Always test with DEBUG=False before deploying
3. **Use checklists**: Follow DEPLOYMENT_CHECKLIST.md
4. **Monitor logs**: Check logs daily after deployment
5. **Keep backups**: Regular database backups are critical
6. **Update regularly**: Keep dependencies updated for security
7. **Document changes**: Note any customizations you make

---

## 🔄 Update Your Deployment

To update after deployment:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Platform auto-deploys (Render/Railway)
# OR manually pull on PythonAnywhere:
cd ~/certificate-tracking-system
git pull
python manage.py migrate
python manage.py collectstatic --noinput
# Then reload web app
```

---

**Ready to deploy? Start with [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for the fastest path! 🚀**

---

Last Updated: January 20, 2026
