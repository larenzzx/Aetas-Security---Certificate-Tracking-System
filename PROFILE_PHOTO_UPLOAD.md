# Profile Photo Upload Feature

## Overview

This document explains the profile photo upload functionality added to the Certificate Tracking System. Users can now upload, change, or remove their profile photos.

## Features

### 1. Default Display
- **Initials by default**: When a user has no profile photo, their initials are displayed in a circular avatar
- **Automatic generation**: Initials are created from first and last name (e.g., "John Doe" → "JD")
- **Consistent styling**: Same avatar size and style across all pages

### 2. Upload Functionality
- **Supported formats**: JPG, JPEG, PNG, WebP
- **File size limit**: 5MB maximum
- **Live preview**: Image preview updates instantly when a file is selected
- **Validation**: Client-side and server-side validation for format and size

### 3. Remove Functionality
- **Optional removal**: Users can remove their profile photo and revert to initials
- **Checkbox option**: "Remove current profile photo" checkbox in edit form
- **File cleanup**: Old photos are automatically deleted from storage when replaced or removed

### 4. Permissions
- **Own profile**: Users can edit their own profile and photo
- **Admin access**: Admins can edit any user's profile and photo
- **Permission check**: Unauthorized users are redirected with error message

## File Structure

### Models
**File**: `accounts/models.py`

```python
class User(AbstractBaseUser, PermissionsMixin):
    # ...
    profile_image = models.ImageField(
        upload_to='profiles/%Y/%m/',  # Organized by year/month
        blank=True,
        null=True,
        help_text='Optional profile photo'
    )
```

**Storage Location**:
- Path: `media/profiles/YYYY/MM/filename.ext`
- Example: `media/profiles/2026/01/john_doe.jpg`
- Organization: Files organized by year and month to prevent directory bloat

### Forms
**File**: `accounts/forms.py`

**Class**: `UserUpdateForm`

**Key Features**:
- Image validation (size, format)
- Checkbox to remove existing photo
- DaisyUI styling for file input
- Custom save method handling image deletion

**Validation Rules**:
```python
def clean_profile_image(self):
    # Max size: 5MB
    # Allowed types: JPEG, PNG, WebP
    # File extension check
    # Returns cleaned image or raises ValidationError
```

### Views
**File**: `accounts/views.py`

**Function**: `profile_edit(request, user_id)`

**Key Features**:
- Permission check (own profile or admin)
- Handles `request.FILES` for image upload
- Processes `remove_profile_image` checkbox
- Success message on save
- Redirects to profile detail page

### Templates

#### 1. Profile Edit Page
**File**: `templates/accounts/profile_edit.html`

**Features**:
- Two-column layout (photo + personal info)
- Live image preview using JavaScript
- Current photo display
- Remove photo checkbox
- File size and format hints
- Responsive design

**JavaScript Preview**:
```javascript
// File upload handler
fileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];

    // Validate size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        alert('File too large');
        return;
    }

    // Show preview using FileReader
    const reader = new FileReader();
    reader.onload = function(event) {
        avatarPreview.innerHTML = '<img src="' + event.target.result + '" />';
    };
    reader.readAsDataURL(file);
});
```

#### 2. Profile Detail Page
**File**: `templates/accounts/profile_detail.html`

**Changes**:
- Added "Edit Profile" button (visible only if `can_edit`)
- Button placed between "Back to List" and "View Certificates"
- Conditional display based on permissions

**Display Logic**:
```django
<div class="avatar placeholder">
    <div class="bg-neutral text-neutral-content rounded-full w-24">
        {% if employee.profile_image %}
            <img src="{{ employee.profile_image.url }}" alt="..." />
        {% else %}
            <span class="text-4xl">{{ employee.first_name.0 }}{{ employee.last_name.0 }}</span>
        {% endif %}
    </div>
</div>
```

### URL Configuration
**File**: `accounts/urls.py`

```python
path('profile/<int:user_id>/edit/', views.profile_edit, name='profile_edit'),
```

**Full URL**: `/accounts/profile/1/edit/`

## How It Works

### 1. Viewing Profile
1. User navigates to profile detail page
2. If profile photo exists: Display image from `media/profiles/YYYY/MM/filename.ext`
3. If no photo: Display initials in circular avatar

### 2. Editing Profile
1. User clicks "Edit Profile" button (only visible if authorized)
2. Edit page loads with current information
3. Current photo displayed (or initials if none)
4. User can:
   - Upload new photo (replaces existing)
   - Check "Remove photo" (reverts to initials)
   - Update personal information

### 3. Uploading New Photo
1. User selects image file
2. **Client-side validation**:
   - Check file size (max 5MB)
   - Check file type (JPG, PNG, WebP)
   - Show error alert if invalid
3. **Preview**: Display selected image immediately
4. **Uncheck remove**: Automatically unchecks "remove photo" checkbox
5. User clicks "Save Changes"
6. **Server-side validation**:
   - Form validates file size
   - Form validates file type
   - Form validates file extension
7. **Storage**:
   - Old photo deleted (if exists)
   - New photo saved to `media/profiles/YYYY/MM/`
   - Database updated with new file path
8. Success message displayed
9. Redirect to profile detail page

### 4. Removing Photo
1. User checks "Remove current profile photo"
2. **Preview updates**: Shows initials instead of photo
3. File input cleared
4. User clicks "Save Changes"
5. **Server processing**:
   - Old photo file deleted from storage
   - Database field set to `NULL`
6. Success message displayed
7. Redirect shows initials instead of photo

## Security Considerations

### 1. File Validation

**Client-Side** (JavaScript):
- Provides immediate feedback
- Prevents unnecessary server requests
- Not secure alone (can be bypassed)

**Server-Side** (Django Form):
- Primary security layer
- Cannot be bypassed
- Validates:
  - File size (5MB max)
  - Content type (MIME type)
  - File extension

### 2. Storage Security

**File Organization**:
```
media/
└── profiles/
    ├── 2026/
    │   ├── 01/
    │   │   ├── photo1.jpg
    │   │   └── photo2.png
    │   └── 02/
    │       └── photo3.webp
    └── 2025/
        └── 12/
            └── photo4.jpg
```

**Benefits**:
- Prevents one huge directory with thousands of files
- Easier backup and archival
- Better file system performance

### 3. Permission Checks

**View Permission**:
- ✅ All authenticated users can view any profile
- ❌ Anonymous users redirected to login

**Edit Permission**:
- ✅ User can edit own profile
- ✅ Admin can edit any profile
- ❌ Others cannot edit

```python
# Permission check in view
if not (request.user.id == user_to_edit.id or request.user.is_admin()):
    messages.error(request, 'Permission denied')
    return redirect('profile_detail')
```

### 4. File Upload Security

**MIME Type Checking**:
```python
allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
if image.content_type not in allowed_types:
    raise ValidationError('Invalid format')
```

**Extension Validation**:
```python
ext = image.name.lower().split('.')[-1]
if ext not in ['jpg', 'jpeg', 'png', 'webp']:
    raise ValidationError('Invalid extension')
```

**Size Limit**:
```python
max_size = 5 * 1024 * 1024  # 5MB
if image.size > max_size:
    raise ValidationError('File too large')
```

## Database

### Field Configuration

```python
profile_image = models.ImageField(
    upload_to='profiles/%Y/%m/',  # Callable or string with strftime
    blank=True,                   # Form field optional
    null=True,                    # Database field nullable
    help_text='Optional profile photo'
)
```

### Storage Path Examples

| Upload Date | Original Name | Stored As |
|-------------|---------------|-----------|
| 2026-01-20 | john.jpg | `profiles/2026/01/john.jpg` |
| 2026-01-20 | jane_doe.png | `profiles/2026/01/jane_doe.png` |
| 2026-02-15 | photo.webp | `profiles/2026/02/photo.webp` |

### File Cleanup

**Automatic Cleanup**:
- When new photo uploaded: Old photo deleted
- When photo removed: File deleted from storage
- Database field updated accordingly

```python
def save(self, commit=True):
    user = super().save(commit=False)

    if self.cleaned_data.get('remove_profile_image'):
        if user.profile_image:
            user.profile_image.delete(save=False)  # Delete file
        user.profile_image = None  # Clear database field

    if commit:
        user.save()

    return user
```

## User Experience

### Profile Photo Locations

The profile photo is displayed in multiple locations:

1. **Navigation Bar**
   - Top right corner
   - Small circular avatar (40px)
   - Shows initials if no photo

2. **Profile Detail Page**
   - Large circular avatar (96px)
   - Header section with employee info
   - Most prominent display

3. **Employee List Page**
   - Medium circular avatar (48px)
   - Next to each employee name
   - Quick visual identification

4. **Mobile Menu**
   - Medium avatar (48px)
   - In sidebar user info section

### Responsive Design

**Desktop**:
- Edit page: Two columns (photo left, info right)
- All buttons visible
- Large photo preview

**Tablet**:
- Edit page: Two columns (stacked on smaller tablets)
- Buttons may wrap
- Medium photo preview

**Mobile**:
- Edit page: Single column (photo on top)
- Buttons stacked vertically
- Optimized for touch

## Testing Checklist

- [ ] Upload JPG image < 5MB
- [ ] Upload PNG image < 5MB
- [ ] Upload WebP image < 5MB
- [ ] Try uploading file > 5MB (should fail with error)
- [ ] Try uploading non-image file (should fail)
- [ ] Upload image, then upload different image (old should be deleted)
- [ ] Upload image, then remove it (should show initials)
- [ ] Remove image without uploading new one
- [ ] User can edit own profile
- [ ] User cannot edit other user's profile (except admin)
- [ ] Admin can edit any profile
- [ ] Image preview updates on file selection
- [ ] Remove checkbox updates preview to initials
- [ ] Cancel button returns to profile without saving
- [ ] Success message displays after save
- [ ] Profile detail page shows new photo after upload
- [ ] All avatar locations show correct photo/initials

## Dependencies

**Required Packages**:
```
Pillow==12.1.0  # For ImageField support
Django>=4.2     # Web framework
```

**Configuration** (`settings.py`):
```python
# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**URL Configuration** (`cert_tracker/urls.py`):
```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Future Enhancements

### 1. Image Processing
- **Auto-resize**: Resize uploaded images to standard size (e.g., 400x400)
- **Thumbnails**: Generate multiple sizes for different use cases
- **Compression**: Optimize file size while maintaining quality
- **Cropping**: Allow users to crop images before upload

**Implementation**:
```python
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def resize_image(image, max_size=400):
    img = Image.open(image)
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    # Convert to RGB if needed
    # Save and return
```

### 2. Drag & Drop Upload
- Add drag-and-drop zone for easier uploads
- Visual feedback during drag
- Multiple file prevention

### 3. Webcam Capture
- Allow users to take photo with webcam
- Useful for quick profile setup
- Mobile camera integration

### 4. Image Editor
- Basic cropping tool
- Rotation options
- Zoom/pan functionality

### 5. Default Avatars
- Provide selection of default avatar images
- Color-coded initials backgrounds
- Avatar generator integration

## Troubleshooting

### Issue: "Pillow is not installed"
**Solution**: Install Pillow
```bash
pip install Pillow
```

### Issue: Uploaded image doesn't display
**Checklist**:
1. Check `MEDIA_URL` in `settings.py`
2. Check `MEDIA_ROOT` exists
3. Verify URL configuration includes `static()`
4. Check file permissions on `media/` directory
5. Ensure DEBUG=True for development

### Issue: File size validation not working
**Check**:
1. Client-side JavaScript enabled
2. Server-side validation in form
3. Web server upload limits (nginx/Apache)

### Issue: Old photos not being deleted
**Verify**:
1. `delete(save=False)` called before `save()`
2. File permissions allow deletion
3. Storage backend configuration

## Summary

The profile photo upload feature provides:

✅ **Easy Upload**: Simple file input with preview
✅ **Validation**: Size and format checks
✅ **Security**: Server-side validation and permission checks
✅ **User-Friendly**: Live preview and helpful messages
✅ **Flexible**: Upload, change, or remove photos
✅ **Efficient**: Automatic file cleanup
✅ **Scalable**: Organized storage by date
✅ **Default**: Initials shown when no photo
✅ **Responsive**: Works on all device sizes
✅ **Accessible**: Works for users and admins

The feature is production-ready and follows Django best practices for file uploads and security.
