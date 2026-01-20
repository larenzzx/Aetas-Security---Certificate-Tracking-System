# Quick Start Guide - Security Features

## ⚡ 3-Minute Setup

### Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements_security.txt
```

**What this installs**:
- `python-magic` - Detects file types
- `Pillow` - Validates images
- `python-magic-bin` - Windows DLLs (Windows only)

### Step 2: Verify Installation (30 seconds)

```bash
python manage.py check
```

**Expected output**:
```
System check identified no issues (0 silenced).
```

### Step 3: Start Server (30 seconds)

```bash
python manage.py runserver
```

### Step 4: Test It Works (1 minute)

**Test 1: Login Enforcement**
1. Open browser
2. Logout if logged in
3. Try going to `http://localhost:8000/certificates/`
4. ✅ Should redirect to login page

**Test 2: Profile Photo Upload**
1. Login
2. Go to your profile → Edit Profile
3. Upload a JPG/PNG image
4. ✅ Should work
5. Try uploading a .txt file renamed to .jpg
6. ✅ Should reject it

**Test 3: View Logs**
```bash
cat logs/security.log
```
✅ Should see login events

---

## ✅ You're Done!

All security features are now active:
- ✅ Login required on all pages
- ✅ Security headers added
- ✅ File uploads validated
- ✅ All actions logged

---

## 🔍 Quick Tests

### Test Login Enforcement:
```bash
# Logout, then:
curl http://localhost:8000/certificates/
# Should redirect to login
```

### Test Security Headers:
```bash
curl -I http://localhost:8000/
# Should see X-Content-Type-Options, X-Frame-Options, etc.
```

### View Recent Logins:
```bash
tail logs/security.log
```

### View User Activity:
```bash
tail logs/audit.log
```

---

## 📖 More Information

- **Summary**: `STEP_12_SUMMARY.md`
- **Technical Details**: `SECURITY_HARDENING_STEP12.md`

---

**That's it!** Your system is now production-ready with enterprise-grade security.
