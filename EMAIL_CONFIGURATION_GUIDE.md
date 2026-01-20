# Email Configuration Guide

## Overview

By default, the system is in **development mode** and emails are printed to the console instead of being sent. This guide shows you how to configure real email sending.

---

## Option 1: Gmail (Recommended for Testing)

### Step 1: Enable App Password in Gmail

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** (left sidebar)
3. Enable **2-Step Verification** (if not already enabled)
4. Search for "App passwords" or go to: https://myaccount.google.com/apppasswords
5. Select app: **Mail**
6. Select device: **Other (Custom name)** → Type "Django CTS"
7. Click **Generate**
8. **Copy the 16-character password** (you'll need it in Step 2)

### Step 2: Update Django Settings

**File**: `cert_tracker/settings.py`

**Find these lines** (around line 166):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production
```

**Change to**:
```python
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production
```

**Find these lines** (around line 170):
```python
# SMTP settings for production (uncomment and configure when deploying)
# EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@company.com'
# EMAIL_HOST_PASSWORD = 'your-email-password'  # Use environment variable!
# DEFAULT_FROM_EMAIL = 'Certificate Tracking System <noreply@company.com>'
```

**Change to** (remove the `#` and update values):
```python
# SMTP settings for Gmail
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@aetassecurity.com'  # ← Your Gmail address
EMAIL_HOST_PASSWORD = 'xxxx xxxx xxxx xxxx'  # ← The 16-char app password from Step 1
DEFAULT_FROM_EMAIL = 'Aetas Security CTS <noreply@aetassecurity.com>'
```

**⚠️ IMPORTANT**: Replace:
- `your-email@aetassecurity.com` with your actual Gmail address
- `xxxx xxxx xxxx xxxx` with the 16-character app password from Step 1

### Step 3: Test

1. **Restart your Django server**:
   ```bash
   # Stop the server (Ctrl+C)
   python manage.py runserver
   ```

2. **Test password reset**:
   - Go to login page
   - Click "Forgot Password?"
   - Enter your email
   - Click "Reset Password"
   - **Check your actual email inbox** ✅

---

## Option 2: Microsoft Outlook / Office 365

### Configuration

**File**: `cert_tracker/settings.py`

**Update these settings**:
```python
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production

# SMTP settings for Outlook
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@outlook.com'  # ← Your Outlook email
EMAIL_HOST_PASSWORD = 'your-password'  # ← Your Outlook password
DEFAULT_FROM_EMAIL = 'Aetas Security CTS <your-email@outlook.com>'
```

**Note**: Outlook may require additional security settings. You may need to:
1. Enable "Less secure app access" in Outlook settings
2. Or use an app-specific password

---

## Option 3: Custom SMTP Server (Company Email)

If Aetas Security has its own email server:

### Configuration

**File**: `cert_tracker/settings.py`

```python
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production

# SMTP settings for company email server
EMAIL_HOST = 'mail.aetassecurity.com'  # ← Your company's SMTP server
EMAIL_PORT = 587  # or 465 for SSL
EMAIL_USE_TLS = True  # or EMAIL_USE_SSL = True for port 465
EMAIL_HOST_USER = 'system@aetassecurity.com'  # ← System email account
EMAIL_HOST_PASSWORD = 'your-smtp-password'  # ← SMTP password
DEFAULT_FROM_EMAIL = 'Aetas Security Certificate System <noreply@aetassecurity.com>'
```

**You'll need from your IT department**:
- SMTP server address (e.g., `smtp.aetassecurity.com` or `mail.aetassecurity.com`)
- SMTP port (usually 587 for TLS or 465 for SSL)
- Whether to use TLS or SSL
- Email account credentials for sending

---

## Option 4: SendGrid (Production-Grade)

For production deployments, consider using SendGrid (free tier: 100 emails/day).

### Step 1: Create SendGrid Account

1. Go to: https://sendgrid.com/
2. Sign up for free account
3. Verify your email
4. Create an API Key:
   - Settings → API Keys → Create API Key
   - Name: "Django CTS"
   - Permissions: Full Access
   - Copy the API key

### Step 2: Install SendGrid Package

```bash
pip install sendgrid
```

### Step 3: Configure Django

**File**: `cert_tracker/settings.py`

```python
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production

# SendGrid SMTP settings
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # ← Literally the word "apikey"
EMAIL_HOST_PASSWORD = 'SG.xxxxxxxxxxxxxxxxxxxxx'  # ← Your SendGrid API key
DEFAULT_FROM_EMAIL = 'Aetas Security CTS <noreply@aetassecurity.com>'

# Verify sender email in SendGrid dashboard
```

**Note**: You must verify your sender email in SendGrid dashboard before sending.

---

## 🔒 Security Best Practices

### ⚠️ NEVER Commit Passwords to Git

**Option A: Environment Variables (Recommended)**

1. **Create `.env` file** (in project root):
```env
# Email Configuration
EMAIL_HOST_USER=your-email@aetassecurity.com
EMAIL_HOST_PASSWORD=your-app-password-here
```

2. **Add `.env` to `.gitignore`**:
```bash
echo ".env" >> .gitignore
```

3. **Install python-decouple**:
```bash
pip install python-decouple
```

4. **Update settings.py**:
```python
from decouple import config

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

**Option B: Django Secrets File**

1. **Create `secrets.py`** (in cert_tracker/ folder):
```python
# secrets.py - DO NOT COMMIT THIS FILE
EMAIL_HOST_USER = 'your-email@aetassecurity.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

2. **Add to `.gitignore`**:
```bash
echo "cert_tracker/secrets.py" >> .gitignore
```

3. **Import in settings.py**:
```python
try:
    from .secrets import *
except ImportError:
    pass  # secrets.py not found, use defaults
```

---

## Testing Email Configuration

### Method 1: Django Shell

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email from CTS',
    'This is a test email from Certificate Tracking System.',
    'noreply@aetassecurity.com',
    ['your-email@aetassecurity.com'],
    fail_silently=False,
)
```

**Expected**:
- ✅ Returns `1` (email sent successfully)
- ✅ Check your email inbox

### Method 2: Password Reset Test

1. Go to login page
2. Click "Forgot Password?"
3. Enter your email
4. Submit
5. ✅ Check your email inbox for reset link

### Method 3: Check Django Logs

If email fails, check the console output for error messages:
```
SMTPAuthenticationError: ...
SMTPException: ...
ConnectionRefusedError: ...
```

---

## Troubleshooting

### Issue 1: "SMTPAuthenticationError: Username and Password not accepted"

**Gmail**:
- ✅ Make sure you're using an **App Password**, not your regular Gmail password
- ✅ Enable 2-Step Verification first
- ✅ Generate a new App Password if needed

**Outlook**:
- ✅ Enable "Less secure app access"
- ✅ Or generate an app-specific password

### Issue 2: "SMTPException: STARTTLS extension not supported"

**Solution**: Change `EMAIL_USE_TLS = True` to `EMAIL_USE_SSL = True` and port to 465:
```python
EMAIL_PORT = 465
EMAIL_USE_SSL = True
# EMAIL_USE_TLS = True  # Comment this out
```

### Issue 3: "Connection refused" or "Timed out"

**Possible causes**:
- ✅ Firewall blocking SMTP ports (587, 465)
- ✅ Wrong SMTP server address
- ✅ ISP blocking SMTP

**Solution**:
- Check firewall settings
- Try different port (587 vs 465)
- Contact your IT department

### Issue 4: Emails go to Spam

**Solutions**:
1. **Add sender to contacts** in your email client
2. **Verify SPF/DKIM records** (for production)
3. **Use company domain** instead of Gmail
4. **Use SendGrid** or other email service (better deliverability)

---

## Quick Setup (Gmail - 2 Minutes)

**If you just want to test quickly with Gmail**:

1. **Get Gmail App Password**:
   - https://myaccount.google.com/apppasswords
   - Generate password for "Django CTS"

2. **Edit `cert_tracker/settings.py`** (lines 166-175):
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'YOUR_GMAIL@gmail.com'
   EMAIL_HOST_PASSWORD = 'YOUR_16_CHAR_APP_PASSWORD'
   DEFAULT_FROM_EMAIL = 'Aetas Security CTS <YOUR_GMAIL@gmail.com>'
   ```

3. **Restart server**:
   ```bash
   python manage.py runserver
   ```

4. **Test**:
   - Go to "Forgot Password"
   - Enter your email
   - Check inbox ✅

---

## Current Configuration Status

**File**: `cert_tracker/settings.py:166`

**Current Mode**: Development (Console)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**To Switch to Production (Real Emails)**:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

---

## Recommendation for Aetas Security

For a production system, I recommend:

1. **Short-term (Testing)**: Use Gmail with App Password
2. **Long-term (Production)**:
   - Use company email server (if available)
   - Or use SendGrid/AWS SES for reliability
   - Configure SPF/DKIM records for deliverability

---

## Support

If you encounter issues:

1. Check console output for error messages
2. Test with Django shell method above
3. Verify credentials are correct
4. Check firewall settings
5. Contact your email provider if needed

---

**Quick Checklist**:
- [ ] Choose email provider (Gmail, Outlook, Company, SendGrid)
- [ ] Get SMTP credentials
- [ ] Update `EMAIL_BACKEND` to smtp
- [ ] Configure SMTP settings in settings.py
- [ ] Restart Django server
- [ ] Test password reset
- [ ] Verify email received ✅

---

**Last Updated**: January 20, 2026
