# Complete Deployment Checklist

Use this checklist to ensure you've completed all necessary steps before deploying your Certificate Tracking System to production.

---

## Phase 1: Pre-Deployment Preparation

### Code & Configuration
- [ ] All code changes are committed to Git
- [ ] Code is pushed to GitHub repository
- [ ] `requirements.txt` includes production dependencies
- [ ] `.gitignore` includes `.env`, `*.log`, `staticfiles/`, `media/`
- [ ] `build.sh` is executable (`chmod +x build.sh` if on Unix)

### Security Configuration
- [ ] Read `PRODUCTION_SETTINGS_GUIDE.md`
- [ ] Updated `cert_tracker/settings.py` to use environment variables
- [ ] Generated new SECRET_KEY (not using default)
- [ ] Created `.env.example` template
- [ ] Verified `.env` is in `.gitignore`
- [ ] Removed any hardcoded secrets from code

### Database
- [ ] All migrations created (`python manage.py makemigrations`)
- [ ] All migrations applied locally (`python manage.py migrate`)
- [ ] Test data works correctly
- [ ] Database backup strategy planned

### Static Files
- [ ] WhiteNoise added to MIDDLEWARE in settings.py
- [ ] `STATIC_ROOT` configured in settings.py
- [ ] Static files collect successfully (`python manage.py collectstatic`)
- [ ] Static files load correctly in browser

### Email Configuration
- [ ] Email provider chosen (Gmail/Outlook/SMTP/SendGrid)
- [ ] SMTP credentials obtained
- [ ] Email settings configured in `.env`
- [ ] Password reset email tested
- [ ] Read `EMAIL_CONFIGURATION_GUIDE.md` or `QUICK_EMAIL_SETUP.md`

### Testing
- [ ] All features tested locally
- [ ] Login/logout works
- [ ] Password reset works
- [ ] Certificate CRUD works
- [ ] Profile photos upload and display
- [ ] User management works (create/edit/delete)
- [ ] DataTables work (search, sort, export)
- [ ] No console errors in browser

### Documentation Review
- [ ] Read `DEPLOYMENT_GUIDE_FREE_HOSTING.md`
- [ ] Read `PRODUCTION_SETTINGS_GUIDE.md`
- [ ] Read `QUICK_DEPLOY.md` (if using PythonAnywhere)
- [ ] Chosen hosting platform (PythonAnywhere/Render/Railway)

---

## Phase 2: Hosting Platform Setup

### Option A: PythonAnywhere
- [ ] PythonAnywhere account created
- [ ] Bash console opened
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file created with production values
- [ ] Migrations run
- [ ] Static files collected
- [ ] Superuser created
- [ ] Web app configured
- [ ] WSGI file updated
- [ ] Virtual environment path set
- [ ] Static file mappings added
- [ ] Web app reloaded
- [ ] Site loads successfully

### Option B: Render
- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web service created
- [ ] Build command configured (`./build.sh`)
- [ ] Start command configured (`gunicorn cert_tracker.wsgi:application`)
- [ ] PostgreSQL database created
- [ ] Environment variables set
- [ ] DATABASE_URL connected
- [ ] Manual deploy triggered
- [ ] Site loads successfully

### Option C: Railway
- [ ] Railway account created
- [ ] New project created
- [ ] GitHub repository connected
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] `railway.toml` committed to repo
- [ ] Build completed successfully
- [ ] Domain generated
- [ ] Site loads successfully

---

## Phase 3: Production Configuration

### Environment Variables (Set on hosting platform)

**Required:**
- [ ] `SECRET_KEY` - Generated secure random key
- [ ] `DEBUG` - Set to `False`
- [ ] `ALLOWED_HOSTS` - Your domain(s)
- [ ] `DATABASE_URL` - Database connection string

**Email (Required for password reset):**
- [ ] `EMAIL_BACKEND` - Set to smtp backend
- [ ] `EMAIL_HOST_USER` - Your email address
- [ ] `EMAIL_HOST_PASSWORD` - App password or SMTP password
- [ ] `EMAIL_HOST` - SMTP server (e.g., smtp.gmail.com)
- [ ] `EMAIL_PORT` - SMTP port (587 or 465)
- [ ] `EMAIL_USE_TLS` - True/False

**Optional (Production Security):**
- [ ] `SECURE_SSL_REDIRECT` - True
- [ ] `SESSION_COOKIE_SECURE` - True
- [ ] `CSRF_COOKIE_SECURE` - True

### Database Setup
- [ ] Database created (PostgreSQL recommended for production)
- [ ] Database URL obtained
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Test data added (optional)

### Static & Media Files
- [ ] Static files collected on server
- [ ] Static files accessible via browser
- [ ] Media folder created
- [ ] Profile photo upload tested
- [ ] Certificate file upload tested (if applicable)

---

## Phase 4: Post-Deployment Testing

### Basic Functionality
- [ ] Homepage loads
- [ ] Login page accessible
- [ ] Can login with superuser account
- [ ] Dashboard displays correctly
- [ ] Navigation works
- [ ] Static files (CSS/JS) load correctly
- [ ] Profile photos display

### Authentication & Security
- [ ] User login works
- [ ] User logout works
- [ ] Password reset request works
- [ ] Password reset email received
- [ ] Password reset link works
- [ ] Forced password change works (new users)
- [ ] Unauthenticated users redirected to login

### Core Features
- [ ] Create certificate works
- [ ] View certificate works
- [ ] Edit certificate works
- [ ] Delete certificate works
- [ ] Certificate list displays
- [ ] Certificate search works
- [ ] DataTables export works (CSV, Excel, PDF)

### User Management
- [ ] Create employee account works
- [ ] Edit employee profile works
- [ ] Upload profile photo works
- [ ] Delete employee works (with warnings)
- [ ] Employee list displays
- [ ] Employee search works

### Email Functionality
- [ ] Password reset email received in inbox (not spam)
- [ ] Email contains correct reset link
- [ ] Email from address is correct
- [ ] Email templates render correctly

### Performance & Errors
- [ ] No 500 errors
- [ ] No 404 errors (except expected)
- [ ] No JavaScript console errors
- [ ] Page load times acceptable
- [ ] No broken images
- [ ] No broken links

---

## Phase 5: Security Verification

### Django Security Check
- [ ] Run `python manage.py check --deploy`
- [ ] Address any warnings
- [ ] Verify no critical issues

### HTTPS/SSL
- [ ] Site accessible via HTTPS
- [ ] SSL certificate valid
- [ ] HTTP redirects to HTTPS
- [ ] No mixed content warnings

### Headers & Security
- [ ] Security headers present (X-Frame-Options, X-Content-Type-Options, etc.)
- [ ] CSRF protection enabled
- [ ] Session cookies secure
- [ ] No sensitive data in URLs

### Access Control
- [ ] Login required for all pages (except login/password reset)
- [ ] Permissions work correctly
- [ ] Users can't access unauthorized pages
- [ ] Admin panel requires admin permission

---

## Phase 6: Monitoring & Maintenance

### Logging
- [ ] Error logs accessible
- [ ] Security logs working
- [ ] Audit logs working
- [ ] Log rotation configured

### Backups
- [ ] Database backup strategy in place
- [ ] Media files backup strategy in place
- [ ] Backup restoration tested

### Monitoring
- [ ] Error notifications configured (optional)
- [ ] Uptime monitoring set up (optional)
- [ ] Log monitoring in place

### Documentation
- [ ] Deployment notes documented
- [ ] Admin credentials stored securely
- [ ] Database credentials stored securely
- [ ] Recovery procedures documented

---

## Phase 7: User Onboarding

### Initial Setup
- [ ] Admin account created
- [ ] Create initial employee accounts
- [ ] Send welcome emails with temporary passwords
- [ ] Verify users can login and change passwords
- [ ] Add sample certificate data (optional)

### Training
- [ ] Admin trained on user management
- [ ] Users trained on basic features
- [ ] Documentation provided to users
- [ ] Support contact information provided

---

## Phase 8: Go-Live

### Final Checks
- [ ] All checklist items above completed
- [ ] Production URL accessible
- [ ] DNS configured (if using custom domain)
- [ ] Email notifications working
- [ ] All stakeholders notified of go-live

### Communication
- [ ] Users notified of system availability
- [ ] Login instructions sent
- [ ] Support process communicated
- [ ] Feedback mechanism established

---

## Rollback Plan

In case of issues:

1. **Keep old system running** (if replacing existing system)
2. **Document the issue** - What went wrong?
3. **Check logs** - Error logs, security logs
4. **Revert code** - `git revert` or redeploy previous version
5. **Restore database** - From backup if needed
6. **Notify users** - Communicate status

---

## Maintenance Schedule

### Daily
- [ ] Check error logs
- [ ] Verify system is accessible

### Weekly
- [ ] Review security logs
- [ ] Check disk space usage
- [ ] Test backups

### Monthly
- [ ] Update dependencies (security patches)
- [ ] Review user accounts
- [ ] Clean up old logs
- [ ] Performance review

---

## Support Resources

### Documentation
- `DEPLOYMENT_GUIDE_FREE_HOSTING.md` - Full deployment guide
- `PRODUCTION_SETTINGS_GUIDE.md` - Settings configuration
- `QUICK_DEPLOY.md` - Fast deployment guide
- `EMAIL_CONFIGURATION_GUIDE.md` - Email setup
- `SECURITY_HARDENING_STEP12.md` - Security features
- `BUG_FIXES_PASSWORD_AND_DELETE.md` - Bug fixes applied

### Emergency Contacts
- **Developer**: [Your contact]
- **Hosting Support**: [Platform support]
- **Database Admin**: [If applicable]

### Useful Commands

**View logs** (PythonAnywhere):
```bash
tail -f /var/log/yourusername.pythonanywhere.com.error.log
```

**Restart server** (Railway/Render):
- Automatic on git push

**Database backup**:
```bash
python manage.py dumpdata > backup.json
```

**Database restore**:
```bash
python manage.py loaddata backup.json
```

---

## Deployment Status

**Date Deployed**: _______________

**Platform**: _______________

**URL**: _______________

**Database**: _______________

**Status**: 🟢 Live / 🟡 Testing / 🔴 Issues

**Notes**:
_______________________________________________
_______________________________________________
_______________________________________________

---

## Sign-Off

**Deployed by**: _______________

**Date**: _______________

**Verified by**: _______________

**Date**: _______________

---

**Congratulations! Your Certificate Tracking System is now live! 🎉**

---

Last Updated: January 20, 2026
