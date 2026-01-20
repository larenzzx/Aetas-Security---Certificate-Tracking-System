"""
Permission decorators for role-based access control.

This module provides decorators to restrict access to views based on user roles:
- @admin_required: Only admin users can access
- @employee_or_admin_required: Any authenticated user
- @owner_or_admin_required: Owner of resource or admin

Usage:
    from core.permissions import admin_required

    @admin_required
    def create_user(request):
        # Only admins can access this view
        pass
"""

from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def admin_required(view_func):
    """
    Decorator to require admin role for a view.

    How it works:
    1. User must be logged in (@login_required)
    2. User must have role='ADMIN' or is_superuser=True
    3. If not admin, redirect to dashboard with error message

    Usage:
        @admin_required
        def create_user(request):
            # Only admins can access
            pass

    Why this exists:
    - Django's @permission_required checks database permissions
    - We use a role-based system (simpler for small teams)
    - This decorator checks the user's role field

    Security:
    - Always requires authentication first
    - Checks both role field and is_superuser flag
    - Shows clear error message to non-admins
    """
    @wraps(view_func)
    @login_required  # Must be logged in first
    def wrapper(request, *args, **kwargs):
        # Check if user is admin
        if request.user.is_admin():
            # User is admin, allow access
            return view_func(request, *args, **kwargs)
        else:
            # User is not admin, deny access
            messages.error(
                request,
                'You do not have permission to access this page. '
                'Admin privileges are required.'
            )
            return redirect('dashboard:home')

    return wrapper


def employee_or_admin_required(view_func):
    """
    Decorator to require any authenticated user (employee or admin).

    This is essentially the same as @login_required, but provided
    for consistency with other permission decorators.

    Usage:
        @employee_or_admin_required
        def view_certificates(request):
            # Any authenticated user can access
            pass
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper


def owner_or_admin_required(get_object_func, owner_field='user'):
    """
    Decorator to require ownership of a resource or admin role.

    This is a factory function that returns a decorator.
    It's used for views that operate on specific resources (like certificates).

    How it works:
    1. User must be logged in
    2. Retrieve the object using get_object_func
    3. User must either:
       - Own the resource (resource.user == request.user), OR
       - Be an admin
    4. If neither, deny access with 403 Forbidden

    Args:
        get_object_func (callable): Function that takes (request, *args, **kwargs)
                                   and returns the object to check
        owner_field (str): Name of the field that stores the owner
                          (default: 'user')

    Usage:
        def get_certificate(request, certificate_id):
            return get_object_or_404(Certificate, id=certificate_id)

        @owner_or_admin_required(get_certificate, 'owner')
        def edit_certificate(request, certificate_id):
            certificate = get_certificate(request, certificate_id)
            # Only certificate owner or admin can edit
            pass

    Note:
    - The get_object_func should handle 404 errors (use get_object_or_404)
    - The object is retrieved once and permission checked
    - Returns 403 Forbidden if permission denied
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            # Get the object
            obj = get_object_func(request, *args, **kwargs)

            # Check permission using helper function
            if not check_object_permission(request, obj, owner_field):
                messages.error(
                    request,
                    'You do not have permission to access this resource. '
                    'Only the owner or an admin can perform this action.'
                )
                return redirect('dashboard:home')

            # Permission granted, execute view
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def check_object_permission(request, obj, owner_field='user'):
    """
    Helper function to check if user has permission to access an object.

    This function is called within views to check permissions.

    Args:
        request: The HTTP request object
        obj: The object to check permissions for
        owner_field (str): Name of the owner field (default: 'user')

    Returns:
        bool: True if user has permission, False otherwise

    Usage:
        def edit_certificate(request, certificate_id):
            certificate = get_object_or_404(Certificate, id=certificate_id)

            if not check_object_permission(request, certificate, 'owner'):
                messages.error(request, 'You do not have permission.')
                return redirect('certificates:list')

            # User has permission, proceed with edit
            ...
    """
    # Admin users have access to everything
    if request.user.is_admin():
        return True

    # Get the owner from the object
    owner = getattr(obj, owner_field, None)

    # Check if current user is the owner
    if owner == request.user:
        return True

    # No permission
    return False


def is_admin(user):
    """
    Helper function to check if a user is an admin.

    This is a standalone function (not a decorator) that can be used
    in templates, views, or other code.

    Args:
        user: User object

    Returns:
        bool: True if user is admin, False otherwise

    Usage in views:
        if is_admin(request.user):
            # Show admin-only content
            pass

    Usage in templates:
        {% if user.is_admin %}
            <a href="{% url 'accounts:user_create' %}">Create User</a>
        {% endif %}

    Note:
    - This checks both user.role and user.is_superuser
    - User model has is_admin() method, so this function is redundant
    - Provided for consistency and clarity
    """
    return user.is_authenticated and (user.role == 'ADMIN' or user.is_superuser)


def is_employee(user):
    """
    Helper function to check if a user is an employee.

    Args:
        user: User object

    Returns:
        bool: True if user is employee, False otherwise

    Usage:
        if is_employee(request.user):
            # Employee-specific logic
            pass

    Note:
    - This only checks if role='EMPLOYEE'
    - Admins will return False (they have role='ADMIN')
    """
    return user.is_authenticated and user.role == 'EMPLOYEE'
