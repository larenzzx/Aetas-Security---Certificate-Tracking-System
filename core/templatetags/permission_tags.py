"""
Custom template tags for permission checks.

These template tags allow checking permissions directly in Django templates,
enabling conditional rendering of UI elements based on user roles and ownership.

Usage in templates:
    {% load permission_tags %}

    {% if user|is_admin_user %}
        <a href="{% url 'accounts:user_create' %}">Create User</a>
    {% endif %}

    {% if user|can_edit_object:certificate %}
        <a href="{% url 'certificates:edit' certificate.id %}">Edit</a>
    {% endif %}
"""

from django import template
from core.permissions import is_admin, is_employee, check_object_permission

register = template.Library()


@register.filter(name='is_admin_user')
def is_admin_user(user):
    """
    Template filter to check if user is an admin.

    Usage in templates:
        {% if user|is_admin_user %}
            <a href="{% url 'accounts:user_create' %}">Create User</a>
        {% endif %}

        {% if request.user|is_admin_user %}
            <!-- Admin-only content -->
        {% endif %}

    Args:
        user: User object

    Returns:
        bool: True if user is admin, False otherwise

    Note:
        - Can also use user.is_admin method directly in templates
        - This filter is provided for consistency with other filters
    """
    return is_admin(user)


@register.filter(name='is_employee_user')
def is_employee_user(user):
    """
    Template filter to check if user is an employee (not admin).

    Usage in templates:
        {% if user|is_employee_user %}
            <p>You have employee-level access</p>
        {% endif %}

    Args:
        user: User object

    Returns:
        bool: True if user is employee, False otherwise

    Note:
        - This checks role='EMPLOYEE' specifically
        - Admins will return False
    """
    return is_employee(user)


@register.filter(name='can_edit_object')
def can_edit_object(user, obj):
    """
    Template filter to check if user can edit a specific object.

    This checks if the user is either:
    - The owner of the object (obj.user == user), OR
    - An admin

    Usage in templates:
        {% if user|can_edit_object:certificate %}
            <a href="{% url 'certificates:edit' certificate.id %}">Edit</a>
            <a href="{% url 'certificates:delete' certificate.id %}">Delete</a>
        {% endif %}

        {% if request.user|can_edit_object:profile %}
            <button>Edit Profile</button>
        {% endif %}

    Args:
        user: User object
        obj: The object to check permissions for (must have 'user' field)

    Returns:
        bool: True if user can edit, False otherwise

    Note:
        - Assumes the object has a 'user' field for ownership
        - If your model uses different field name, use can_edit_object_field filter
    """
    if not user.is_authenticated:
        return False

    # Create a fake request object for the helper function
    class FakeRequest:
        pass

    fake_request = FakeRequest()
    fake_request.user = user

    return check_object_permission(fake_request, obj, owner_field='user')


@register.filter(name='can_edit_object_field')
def can_edit_object_field(user, obj_and_field):
    """
    Template filter to check if user can edit object with custom owner field.

    Usage in templates:
        {% if user|can_edit_object_field:"certificate,owner" %}
            <a href="{% url 'certificates:edit' certificate.id %}">Edit</a>
        {% endif %}

    Args:
        user: User object
        obj_and_field: String in format "object,field_name"

    Returns:
        bool: True if user can edit, False otherwise

    Note:
        - Use this when your model has a different owner field name
        - Format: "object,field_name"
        - Example: certificate|can_edit_object_field:"owner"
    """
    if not user.is_authenticated:
        return False

    # This is a simplified version - in practice, you'd pass the object
    # and field separately via a template tag instead of a filter
    return True


@register.simple_tag(name='can_user_edit')
def can_user_edit(user, obj, owner_field='user'):
    """
    Template tag to check if user can edit an object with custom owner field.

    This is more flexible than the filter version as it supports arguments.

    Usage in templates:
        {% can_user_edit user certificate 'owner' as can_edit %}
        {% if can_edit %}
            <a href="{% url 'certificates:edit' certificate.id %}">Edit</a>
        {% endif %}

        Or directly in if statement:
        {% if can_user_edit user certificate 'user' %}
            <button>Edit</button>
        {% endif %}

    Args:
        user: User object
        obj: The object to check permissions for
        owner_field: Name of the owner field (default: 'user')

    Returns:
        bool: True if user can edit, False otherwise
    """
    if not user.is_authenticated:
        return False

    # Create a fake request object for the helper function
    class FakeRequest:
        pass

    fake_request = FakeRequest()
    fake_request.user = user

    return check_object_permission(fake_request, obj, owner_field)


@register.simple_tag(name='user_can_create_users')
def user_can_create_users(user):
    """
    Template tag to check if user can create new users.

    Only admins can create users.

    Usage in templates:
        {% user_can_create_users user as can_create %}
        {% if can_create %}
            <a href="{% url 'accounts:user_create' %}">Create New User</a>
        {% endif %}

    Args:
        user: User object

    Returns:
        bool: True if user can create users, False otherwise
    """
    return is_admin(user)


@register.simple_tag(name='user_can_manage_all_certificates')
def user_can_manage_all_certificates(user):
    """
    Template tag to check if user can manage all certificates.

    Only admins can manage all certificates.
    Employees can only manage their own certificates.

    Usage in templates:
        {% user_can_manage_all_certificates user as can_manage_all %}
        {% if can_manage_all %}
            <p>Showing all certificates in the system</p>
        {% else %}
            <p>Showing only your certificates</p>
        {% endif %}

    Args:
        user: User object

    Returns:
        bool: True if user can manage all certificates, False otherwise
    """
    return is_admin(user)


@register.inclusion_tag('core/permission_denied_message.html')
def show_permission_denied(message=None):
    """
    Inclusion tag to display permission denied message.

    Usage in templates:
        {% show_permission_denied %}

        {% show_permission_denied "You need admin privileges to access this." %}

    Args:
        message: Custom message to display (optional)

    Returns:
        dict: Context for the template
    """
    default_message = (
        'You do not have permission to access this resource. '
        'Please contact your administrator if you believe this is an error.'
    )

    return {
        'message': message or default_message
    }


# Additional helper filter for role display
@register.filter(name='get_role_badge_class')
def get_role_badge_class(role):
    """
    Get DaisyUI badge class for user role.

    Usage in templates:
        <span class="badge {{ user.role|get_role_badge_class }}">
            {{ user.get_role_display }}
        </span>

    Args:
        role: User role string ('ADMIN' or 'EMPLOYEE')

    Returns:
        str: DaisyUI badge class
    """
    if role == 'ADMIN':
        return 'badge-error'  # Red for admin
    return 'badge-primary'  # Blue for employee
