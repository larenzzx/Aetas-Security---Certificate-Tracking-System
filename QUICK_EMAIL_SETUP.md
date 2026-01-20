# Quick Email Setup (2 Minutes)

## Why Emails Don't Send

**Current Status**: Development mode - emails print to console instead of sending.

**Where to see them**: Look at your terminal where `python manage.py runserver` is running.

---

## Quick Fix: Enable Gmail (2 Minutes)

### Step 1: Get Gmail App Password (1 minute)

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to your Gmail account
3. Create App Password:
   - App: **Mail**
   - Device: **Other** → Type "Django"
4. Click **Generate**
5. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

### Step 2: Update Settings (1 minute)

Open: `cert_tracker/settings.py`

**Find line 166** - Change FROM:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Development
```

**Change TO**:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Production
```

**Find line 170** - Uncomment and update these lines:
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'youremail@gmail.com'  # ← Your Gmail
EMAIL_HOST_PASSWORD = 'abcd efgh ijkl mnop'  # ← App password from Step 1
DEFAULT_FROM_EMAIL = 'Aetas Security <youremail@gmail.com>'
```

### Step 3: Restart & Test (30 seconds)

```bash
# Stop the server (Ctrl+C)
python manage.py runserver
```

Then test:
1. Go to login page
2. Click "Forgot Password?"
3. Enter your email
4. **Check your Gmail inbox** ✅

---

## That's It!

Emails will now be sent to real email addresses instead of just printing to console.

---

## Need Different Email Provider?

See: `EMAIL_CONFIGURATION_GUIDE.md` for:
- Outlook/Office 365 setup
- Company email server setup
- SendGrid setup
- Troubleshooting

---

## ⚠️ Security Warning

**Don't commit your password to Git!**

After testing, move your password to environment variables:

1. Create `.env` file:
```env
EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

2. Add to `.gitignore`:
```bash
echo ".env" >> .gitignore
```

3. Install python-decouple:
```bash
pip install python-decouple
```

4. Update settings.py:
```python
from decouple import config

EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

---

## Quick Test in Django Shell

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test.',
    'noreply@aetassecurity.com',
    ['your-email@gmail.com'],
)
```

If it returns `1` → Success! ✅
