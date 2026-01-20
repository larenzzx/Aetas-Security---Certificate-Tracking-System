# Aetas Security Branding Customization

## Overview

This document outlines all the branding customizations made to the Certificate Tracking System for Aetas Security LLC.

## Logo Implementation

### Logo File Location
- **Path**: `static/images/ATS-LOGO.png`
- **File Size**: 147,904 bytes (144 KB)
- **Format**: PNG

### Logo Usage

The Aetas Security logo is displayed in the following locations:

1. **Main Navigation Bar** (`templates/base.html`)
   - Logo image with company name
   - Height: 32px (h-8)
   - Company name hidden on mobile, visible on desktop

2. **Login/Authentication Pages** (`templates/accounts/base_auth.html`)
   - Logo image at 80px height (h-20)
   - Displayed above company name and system title

3. **Footer** (`templates/base.html`)
   - Logo at 48px height (h-12)
   - Displayed above company information

4. **Favicon** (Both `base.html` and `base_auth.html`)
   - Logo used as browser favicon
   - Displays in browser tab

## Branding Elements Updated

### 1. Company Name & Identity

**Primary Branding**:
- Company Name: **Aetas Security LLC**
- Full Legal Name: Aetas Security LLC
- Short Name: Aetas Security
- Acronym: ATS (Aetas Tracking System)

### 2. Page Titles

All page titles follow the format: `[Page Name] - Aetas Security`

**Updated Templates**:
- `templates/base.html`: "Certificate Tracking System - Aetas Security"
- `templates/accounts/base_auth.html`: "Authentication - Aetas Security"
- `templates/accounts/login.html`: "Login - Aetas Security"
- `templates/dashboard/home.html`: "Dashboard - Aetas Security"

### 3. Meta Tags

Added branding-specific meta tags for SEO and branding:

```html
<meta name="description" content="Aetas Security Certificate Tracking System - Manage and track employee certifications">
<meta name="author" content="Aetas Security">
```

### 4. Headers & Subtitles

**Dashboard** (`templates/dashboard/home.html`):
- Header: "Aetas Security Dashboard"
- Subtitle: "Certification tracking and employee management overview"

**Login Page** (`templates/accounts/login.html`):
- Title: "Aetas Security"
- Subtitle: "Certificate Tracking System"
- Additional: "Sign in to manage your certifications"

**Navigation Bar**:
- Logo + "Aetas Security" text (hidden on mobile)

### 5. Email Placeholder

**Login Page**:
- Changed from: `your.email@company.com`
- Changed to: `your.email@aetassecurity.com`

This reflects the company's email domain.

### 6. Footer Branding

**Updated Footer** (`templates/base.html`):
```
[Logo Image]
Aetas Security LLC
Certificate Tracking System
© 2026 Aetas Security. All rights reserved.
```

## File Modifications Summary

### Templates Modified

1. **`templates/base.html`**
   - Added `{% load static %}` at top
   - Added meta description and author tags
   - Added favicon reference
   - Updated page title
   - Replaced navigation logo with Aetas Security logo
   - Updated company name in navigation
   - Enhanced footer with logo and company information

2. **`templates/accounts/base_auth.html`**
   - Added `{% load static %}` at top
   - Added meta description and author tags
   - Added favicon reference
   - Updated page title
   - Replaced icon with Aetas Security logo
   - Updated company name and system title
   - Improved branding hierarchy

3. **`templates/accounts/login.html`**
   - Updated page title
   - Changed subtitle text
   - Updated email placeholder to company domain

4. **`templates/dashboard/home.html`**
   - Updated page title
   - Changed dashboard header to "Aetas Security Dashboard"
   - Updated subtitle for better branding

## Static Files Configuration

### Django Settings

**File**: `cert_tracker/settings.py`

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Project-level static files
]
STATIC_ROOT = BASE_DIR / 'staticfiles'  # For production (collectstatic)
```

### Directory Structure

```
Certificate Tracking System/
├── static/
│   └── images/
│       └── ATS-LOGO.png
├── templates/
│   ├── base.html
│   ├── accounts/
│   │   ├── base_auth.html
│   │   └── login.html
│   └── dashboard/
│       └── home.html
└── ...
```

## Visual Branding Guidelines

### Logo Usage

**Recommended Sizes**:
- Navigation bar: 32px height (h-8)
- Login page: 80px height (h-20)
- Footer: 48px height (h-12)
- Favicon: Original size

**Display Rules**:
- Always maintain aspect ratio (use `w-auto` with Tailwind)
- Include alt text: "Aetas Security"
- Logo should be visible in both light and dark themes

### Typography Hierarchy

**Login/Auth Pages**:
1. Company Name (h1): `text-3xl font-bold`
2. System Name: `text-xl text-base-content/80`
3. Subtitle: `text-base-content/60`

**Dashboard**:
1. Page Header: `text-3xl font-bold`
2. Subtitle: `text-base-content/60`

**Footer**:
1. Company Name: `font-bold text-lg`
2. System Name: `text-sm`
3. Copyright: `text-xs`

### Color Scheme

Using DaisyUI default theme with:
- Primary color for branding elements
- Base-content for text
- Base-300 for footer background

## Testing Checklist

- [x] Logo displays correctly in navigation bar
- [x] Logo displays on login page
- [x] Logo displays in footer
- [x] Favicon appears in browser tab
- [x] Company name displays correctly everywhere
- [x] Email placeholder uses company domain
- [x] Page titles include "Aetas Security"
- [x] Meta tags include company information
- [x] Dark mode compatibility maintained
- [x] Mobile responsive design preserved

## Deployment Notes

### For Production

When deploying to production, remember to:

1. **Collect Static Files**:
   ```bash
   python manage.py collectstatic
   ```

2. **Verify Logo Path**:
   Ensure `static/images/ATS-LOGO.png` is included in collected static files

3. **Check Static Files Serving**:
   Configure web server (nginx/Apache) to serve static files from STATIC_ROOT

4. **Test All Pages**:
   - Login page
   - Dashboard
   - Employee profiles
   - Certificate pages
   - Footer on all pages

### Environment-Specific Settings

**Development**:
- Static files served automatically by Django
- DEBUG = True (only in development)

**Production**:
- Static files served by web server
- DEBUG = False
- Use STATIC_ROOT for collected static files
- Consider CDN for static assets

## Future Enhancements

### Potential Additions

1. **Custom Favicon Sizes**:
   - Create 16x16, 32x32, 180x180 versions
   - Add apple-touch-icon for iOS devices

2. **Loading Screen**:
   - Add Aetas Security branded loading animation

3. **Email Templates**:
   - Add logo to password reset emails
   - Brand notification emails

4. **Error Pages**:
   - Custom 404/500 pages with Aetas Security branding

5. **PDF Reports**:
   - Include logo in certificate PDF exports
   - Add company letterhead to reports

## Maintenance

### Updating the Logo

If the logo needs to be updated:

1. Replace `static/images/ATS-LOGO.png` with new logo file
2. Keep the same filename to avoid template changes
3. Clear browser cache to see changes
4. Run `python manage.py collectstatic` for production
5. Restart development server to reload static files

### Adding New Branded Pages

When creating new pages, remember to:

1. Use `{% load static %}` at the top
2. Include favicon reference in custom base templates
3. Use "- Aetas Security" suffix in page titles
4. Include company branding in headers
5. Maintain consistent typography hierarchy

## Summary

The Certificate Tracking System has been fully customized for Aetas Security LLC with:

- ✅ Company logo displayed in navigation, login, and footer
- ✅ Favicon for browser tabs
- ✅ Company name throughout the application
- ✅ Professional branding hierarchy
- ✅ Company-specific email placeholders
- ✅ SEO meta tags with company information
- ✅ Consistent branding across all pages
- ✅ Dark mode compatibility
- ✅ Mobile responsive design

All branding elements are production-ready and follow Django best practices for static file management.
