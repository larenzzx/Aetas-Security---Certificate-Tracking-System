# Quick Deploy Checklist (5 Minutes)

Use this if you want to deploy FAST to PythonAnywhere.

## Prerequisites (1 minute)
- [ ] PythonAnywhere account created (https://www.pythonanywhere.com/)
- [ ] Code pushed to GitHub
- [ ] Gmail App Password ready (https://myaccount.google.com/apppasswords)

## Step 1: Clone Repository (1 minute)

Open PythonAnywhere Bash console:
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 2: Configure Environment (1 minute)

Create `.env` file:
```bash
nano .env
```

Add (replace with your values):
```env
DEBUG=False
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
ALLOWED_HOSTS=yourusername.pythonanywhere.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

Save: Ctrl+O, Enter, Ctrl+X

## Step 3: Setup Database (1 minute)

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Step 4: Configure Web App (2 minutes)

1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose **Manual configuration** → **Python 3.10**
4. Click on **WSGI configuration file**
5. Replace ALL content with:

```python
import os
import sys

# CHANGE THIS: Replace 'yourusername' with your actual username
path = '/home/yourusername/your-repo-name'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'cert_tracker.settings'

# Load .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

# Activate virtual environment
activate_this = f'{path}/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

6. Set **Virtualenv** to: `/home/yourusername/your-repo-name/venv`

7. Add **Static files**:
   - `/static/` → `/home/yourusername/your-repo-name/staticfiles`
   - `/media/` → `/home/yourusername/your-repo-name/media`

8. Click **Reload** button

## Step 5: Test (30 seconds)

Visit: `https://yourusername.pythonanywhere.com`

✅ Done! Your app is live!

---

## Troubleshooting

**Error loading?**
1. Check error log in Web tab
2. Verify username in WSGI file is correct
3. Verify paths match your actual directories
4. Click Reload again

**Static files not loading?**
```bash
python manage.py collectstatic --noinput
```
Then Reload web app.

**Can't login?**
- Check you created superuser
- Verify email settings in .env

---

## Next Steps

1. ✅ Login to admin: `https://yourusername.pythonanywhere.com/admin/`
2. ✅ Create employee accounts
3. ✅ Add certificates
4. ✅ Test password reset email

---

For detailed deployment guide with other platforms, see: `DEPLOYMENT_GUIDE_FREE_HOSTING.md`
