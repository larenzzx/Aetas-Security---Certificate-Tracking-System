# Role-Based Permissions System

## Overview

The Certificate Tracking System uses a role-based access control (RBAC) system with two user roles:

- **ADMIN**: Full access to all features, can create users, manage all certificates
- **EMPLOYEE**: Limited access, can only view data and manage their own certificates

## Architecture

### 1. User Model (`accounts/models.py`)

The custom User model includes a `role` field with two choices:

```python
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('EMPLOYEE', 'Employee'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE')

    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'ADMIN' or self.is_superuser
```

### 2. Permission Decorators (`core/permissions.py`)

#### `@admin_required`
Restricts view access to admin users only.

**Usage:**
```python
from core.permissions import admin_required

@admin_required
def user_create(request):
    # Only admins can access this view
    pass
```

**How it works:**
1. Requires user to be logged in (`@login_required`)
2. Checks if `user.is_admin()` returns True
3. If not admin, redirects to dashboard with error message

#### `@employee_or_admin_required`
Allows any authenticated user (both employees and admins).

**Usage:**
```python
from core.permissions import employee_or_admin_required

@employee_or_admin_required
def view_certificates(request):
    # Any authenticated user can access
    pass
```

**Note:** This is essentially the same as `@login_required`, but provided for consistency.

#### `@owner_or_admin_required`
Restricts access to object owners or admins (object-level permissions).

**Usage:**
```python
from core.permissions import owner_or_admin_required
from django.shortcuts import get_object_or_404

def get_certificate(request, certificate_id):
    return get_object_or_404(Certificate, id=certificate_id)

@owner_or_admin_required(get_certificate, owner_field='user')
def edit_certificate(request, certificate_id):
    certificate = get_certificate(request, certificate_id)
    # Only certificate owner or admin can edit
    pass
```

**Parameters:**
- `get_object_func`: Function that retrieves the object
- `owner_field`: Name of the field storing the owner (default: 'user')

### 3. Permission Helper Functions

#### `check_object_permission(request, obj, owner_field='user')`
Helper function to check object-level permissions within views.

**Usage:**
```python
from core.permissions import check_object_permission

def edit_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)

    if not check_object_permission(request, certificate, 'user'):
        messages.error(request, 'Permission denied.')
        return redirect('certificates:list')

    # User has permission, proceed with edit
    ...
```

**Returns:**
- `True` if user is admin OR owner of the object
- `False` otherwise

#### `is_admin(user)` and `is_employee(user)`
Standalone functions to check user roles.

**Usage:**
```python
from core.permissions import is_admin, is_employee

if is_admin(request.user):
    # Show admin-only content
    pass

if is_employee(request.user):
    # Employee-specific logic
    pass
```

### 4. Template Tags (`core/templatetags/permission_tags.py`)

Load the tags in templates:
```django
{% load permission_tags %}
```

#### `is_admin_user` Filter
Check if user is an admin.

**Usage:**
```django
{% if user|is_admin_user %}
    <a href="{% url 'accounts:user_create' %}">Create User</a>
{% endif %}
```

#### `is_employee_user` Filter
Check if user is an employee (not admin).

**Usage:**
```django
{% if user|is_employee_user %}
    <p>Employee-level access</p>
{% endif %}
```

#### `can_edit_object` Filter
Check if user can edit a specific object.

**Usage:**
```django
{% if user|can_edit_object:certificate %}
    <a href="{% url 'certificates:edit' certificate.id %}">Edit</a>
    <a href="{% url 'certificates:delete' certificate.id %}">Delete</a>
{% endif %}
```

**Note:** Assumes object has a `user` field for ownership.

#### `can_user_edit` Template Tag
More flexible version with custom owner field.

**Usage:**
```django
{% can_user_edit user certificate 'owner' as can_edit %}
{% if can_edit %}
    <button>Edit</button>
{% endif %}

{# Or directly in if statement #}
{% if can_user_edit user certificate 'user' %}
    <button>Edit</button>
{% endif %}
```

#### `user_can_create_users` Template Tag
Check if user can create new users (admin only).

**Usage:**
```django
{% user_can_create_users user as can_create %}
{% if can_create %}
    <a href="{% url 'accounts:user_create' %}">Create New User</a>
{% endif %}
```

#### `user_can_manage_all_certificates` Template Tag
Check if user can manage all certificates (admin only).

**Usage:**
```django
{% user_can_manage_all_certificates user as can_manage_all %}
{% if can_manage_all %}
    <p>Showing all certificates in the system</p>
{% else %}
    <p>Showing only your certificates</p>
{% endif %}
```

#### `get_role_badge_class` Filter
Get DaisyUI badge class for user role styling.

**Usage:**
```django
<span class="badge {{ user.role|get_role_badge_class }}">
    {{ user.get_role_display }}
</span>
```

**Returns:**
- `badge-error` for ADMIN (red)
- `badge-primary` for EMPLOYEE (blue)

#### `show_permission_denied` Inclusion Tag
Display a permission denied message component.

**Usage:**
```django
{% show_permission_denied %}

{% show_permission_denied "You need admin privileges to access this." %}
```

**Renders:** A styled alert box with the error message.

## Permission Rules by Feature

### User Management

| Action | Admin | Employee |
|--------|-------|----------|
| Create new users | ✅ Yes | ❌ No |
| View user list | ✅ Yes | ✅ Yes |
| Edit own profile | ✅ Yes | ✅ Yes |
| Edit other profiles | ✅ Yes | ❌ No |
| Delete users | ✅ Yes | ❌ No |
| Change user roles | ✅ Yes | ❌ No |

### Certificate Management

| Action | Admin | Employee |
|--------|-------|----------|
| View all certificates | ✅ Yes | ✅ Yes |
| Create certificate | ✅ Yes | ✅ Yes (for self) |
| Edit own certificate | ✅ Yes | ✅ Yes |
| Edit other's certificate | ✅ Yes | ❌ No |
| Delete own certificate | ✅ Yes | ✅ Yes |
| Delete other's certificate | ✅ Yes | ❌ No |
| Assign certificates to others | ✅ Yes | ❌ No |

### Dashboard & Reports

| Action | Admin | Employee |
|--------|-------|----------|
| View dashboard | ✅ Yes | ✅ Yes |
| View own statistics | ✅ Yes | ✅ Yes |
| View company-wide stats | ✅ Yes | ❌ No |
| Export reports | ✅ Yes | ✅ Yes (own data) |

## Implementation Examples

### Example 1: Admin-Only View

```python
# views.py
from core.permissions import admin_required

@admin_required
def user_create(request):
    """Only admins can create users"""
    # ... implementation
    pass
```

### Example 2: Owner or Admin Can Edit

```python
# views.py
from core.permissions import check_object_permission
from django.shortcuts import get_object_or_404

@login_required
def edit_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)

    # Check permission
    if not check_object_permission(request, certificate, 'user'):
        messages.error(request, 'You can only edit your own certificates.')
        return redirect('certificates:list')

    # Process edit
    if request.method == 'POST':
        # ... handle form submission
        pass

    return render(request, 'certificates/edit.html', {'certificate': certificate})
```

### Example 3: Conditional Template Display

```django
{# template.html #}
{% load permission_tags %}

<div class="card">
    <h2>{{ certificate.name }}</h2>

    {# Only show edit/delete to owner or admin #}
    {% if user|can_edit_object:certificate %}
        <div class="actions">
            <a href="{% url 'certificates:edit' certificate.id %}" class="btn btn-primary">Edit</a>
            <a href="{% url 'certificates:delete' certificate.id %}" class="btn btn-error">Delete</a>
        </div>
    {% endif %}

    {# Only admins can reassign #}
    {% if user|is_admin_user %}
        <a href="{% url 'certificates:reassign' certificate.id %}" class="btn btn-ghost">
            Reassign to Another User
        </a>
    {% endif %}
</div>
```

### Example 4: Filtering Querysets by Permission

```python
# views.py
@login_required
def certificate_list(request):
    """Show certificates based on user role"""

    if request.user.is_admin():
        # Admins see all certificates
        certificates = Certificate.objects.all()
    else:
        # Employees see only their own certificates
        certificates = Certificate.objects.filter(user=request.user)

    return render(request, 'certificates/list.html', {
        'certificates': certificates
    })
```

### Example 5: API Permissions (Future)

```python
# For API views (if implementing REST API later)
from rest_framework.permissions import BasePermission

class IsAdminOrOwner(BasePermission):
    """
    Custom permission: Admin can access anything, others can only access own objects
    """
    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.is_admin():
            return True

        # Check if user owns the object
        return obj.user == request.user
```

## Security Best Practices

### 1. Always Require Authentication
```python
# ✅ Good - Uses @login_required
@login_required
def view_profile(request, user_id):
    pass

# ❌ Bad - No authentication check
def view_profile(request, user_id):
    pass
```

### 2. Check Permissions at View Level
```python
# ✅ Good - Permission checked in view
@admin_required
def delete_user(request, user_id):
    # Safe - decorator ensures only admins can access
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('accounts:user_list')

# ❌ Bad - No permission check
@login_required
def delete_user(request, user_id):
    # Dangerous - any authenticated user could delete users
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('accounts:user_list')
```

### 3. Use Template Tags for UI Only
```python
# ⚠️ Important Note
# Template tags hide UI elements but DO NOT enforce security
# Always check permissions in views as well
```

```django
{# This hides the button from non-admins #}
{% if user|is_admin_user %}
    <a href="{% url 'accounts:delete_user' user.id %}">Delete</a>
{% endif %}

{# But users could still access the URL directly! #}
{# The view MUST have @admin_required decorator #}
```

### 4. Double-Check Object Ownership
```python
@login_required
def edit_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)

    # ✅ Good - Explicitly check permission
    if not check_object_permission(request, certificate):
        return HttpResponseForbidden("You don't have permission")

    # Now safe to proceed
    # ...
```

### 5. Use get_object_or_404 for Security
```python
# ✅ Good - Returns 404 if not found
certificate = get_object_or_404(Certificate, id=certificate_id)

# ❌ Bad - Exposes object existence
try:
    certificate = Certificate.objects.get(id=certificate_id)
except Certificate.DoesNotExist:
    # User knows the object doesn't exist
    return HttpResponse("Certificate doesn't exist")
```

## Testing Permissions

### Manual Testing Checklist

1. **Admin User Testing:**
   - ✅ Can create new users
   - ✅ Can edit all certificates
   - ✅ Can delete any certificate
   - ✅ Can view all users
   - ✅ Can access admin dashboard

2. **Employee User Testing:**
   - ✅ Can view own profile
   - ✅ Can edit own certificates
   - ✅ Cannot create users (redirected with error)
   - ✅ Cannot edit other users' certificates
   - ✅ Cannot delete other users' certificates

3. **Unauthenticated User Testing:**
   - ✅ Cannot access any protected pages
   - ✅ Redirected to login page
   - ✅ Can only access login/password reset pages

### Unit Test Example

```python
# tests/test_permissions.py
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User

class PermissionTests(TestCase):
    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='password123',
            role='ADMIN',
            first_name='Admin',
            last_name='User'
        )

        # Create employee user
        self.employee = User.objects.create_user(
            email='employee@example.com',
            password='password123',
            role='EMPLOYEE',
            first_name='Employee',
            last_name='User'
        )

        self.client = Client()

    def test_admin_can_create_users(self):
        """Test that admins can access user creation page"""
        self.client.login(email='admin@example.com', password='password123')
        response = self.client.get(reverse('accounts:user_create'))
        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_create_users(self):
        """Test that employees cannot access user creation page"""
        self.client.login(email='employee@example.com', password='password123')
        response = self.client.get(reverse('accounts:user_create'))
        self.assertEqual(response.status_code, 302)  # Redirected
        self.assertRedirects(response, reverse('dashboard:home'))

    def test_unauthenticated_user_redirected(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('accounts:login')))
```

## Troubleshooting

### Issue: Permission denied even for admin users

**Cause:** User role is set to 'EMPLOYEE' instead of 'ADMIN'

**Solution:**
```python
# Fix via Django shell
python manage.py shell

from accounts.models import User
user = User.objects.get(email='admin@example.com')
user.role = 'ADMIN'
user.save()
```

### Issue: Template tags not working

**Cause:** Forgot to load permission_tags

**Solution:**
```django
{# Add this at the top of your template #}
{% load permission_tags %}

{# Now you can use the tags #}
{% if user|is_admin_user %}
    ...
{% endif %}
```

### Issue: Object permission check failing

**Cause:** Object doesn't have the expected owner field

**Solution:**
```python
# Specify the correct field name
if not check_object_permission(request, certificate, owner_field='owner'):
    # Use 'owner' instead of default 'user'
    pass
```

## Future Enhancements

Potential improvements for more complex permission scenarios:

1. **Group-Based Permissions**: Add department-level permissions
2. **Permission Matrix**: More granular permissions (view, edit, delete separately)
3. **Audit Logging**: Track all permission checks and denials
4. **Time-Based Permissions**: Temporary admin access
5. **IP-Based Restrictions**: Restrict admin access to office network

## Summary

The Certificate Tracking System uses a simple but effective role-based permission system:

- **Two roles**: ADMIN and EMPLOYEE
- **Decorators** enforce permissions at the view level
- **Template tags** conditionally display UI elements
- **Helper functions** provide object-level permission checks
- **Security-first approach**: Always check permissions in views, not just templates

This system ensures that:
- ✅ Admins have full control over the system
- ✅ Employees can manage their own data
- ✅ Unauthorized access is prevented
- ✅ Clear error messages guide users
- ✅ Code is maintainable and testable
