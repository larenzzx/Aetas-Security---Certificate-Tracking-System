"""
Audit logging utilities for Aetas Security Certificate Tracking System.

Provides functions for logging security-critical events:
- Authentication events (login, logout, failed attempts)
- User management (create, update, delete)
- Certificate operations (create, update, delete)
- Permission changes
- Data exports
"""

import logging
from django.contrib.auth import get_user_model

# Get logger instances
security_logger = logging.getLogger('security')
audit_logger = logging.getLogger('audit')

User = get_user_model()


def get_client_ip(request):
    """
    Extract client IP address from request.

    Handles proxies and load balancers.

    Args:
        request: Django HTTP request

    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    Extract user agent from request.

    Args:
        request: Django HTTP request

    Returns:
        str: User agent string
    """
    return request.META.get('HTTP_USER_AGENT', 'Unknown')


# ==============================================================================
# AUTHENTICATION LOGGING
# ==============================================================================

def log_login_success(request, user):
    """
    Log successful user login.

    Args:
        request: Django HTTP request
        user: User object that logged in
    """
    security_logger.info(
        f'LOGIN SUCCESS | User: {user.email} (ID: {user.id}) | '
        f'IP: {get_client_ip(request)} | '
        f'User-Agent: {get_user_agent(request)}'
    )


def log_login_failure(request, email, reason='Invalid credentials'):
    """
    Log failed login attempt.

    Args:
        request: Django HTTP request
        email: Email address used in login attempt
        reason: Reason for failure
    """
    security_logger.warning(
        f'LOGIN FAILED | Email: {email} | Reason: {reason} | '
        f'IP: {get_client_ip(request)} | '
        f'User-Agent: {get_user_agent(request)}'
    )


def log_logout(request, user):
    """
    Log user logout.

    Args:
        request: Django HTTP request
        user: User object that logged out
    """
    security_logger.info(
        f'LOGOUT | User: {user.email} (ID: {user.id}) | '
        f'IP: {get_client_ip(request)}'
    )


def log_password_change(request, user, forced=False):
    """
    Log password change event.

    Args:
        request: Django HTTP request
        user: User who changed password
        forced: Whether it was a forced password change
    """
    change_type = 'FORCED' if forced else 'VOLUNTARY'
    security_logger.info(
        f'PASSWORD CHANGE ({change_type}) | User: {user.email} (ID: {user.id}) | '
        f'IP: {get_client_ip(request)}'
    )


def log_password_reset_request(request, email):
    """
    Log password reset request.

    Args:
        request: Django HTTP request
        email: Email address for reset request
    """
    security_logger.info(
        f'PASSWORD RESET REQUEST | Email: {email} | '
        f'IP: {get_client_ip(request)}'
    )


# ==============================================================================
# USER MANAGEMENT LOGGING
# ==============================================================================

def log_user_created(request, created_user, created_by):
    """
    Log user account creation.

    Args:
        request: Django HTTP request
        created_user: User object that was created
        created_by: User who created the account
    """
    audit_logger.info(
        f'USER CREATED | New User: {created_user.email} (ID: {created_user.id}) | '
        f'Created By: {created_by.email} (ID: {created_by.id}) | '
        f'Role: {created_user.get_role_display()} | '
        f'IP: {get_client_ip(request)}'
    )


def log_user_updated(request, updated_user, updated_by, fields_changed):
    """
    Log user profile update.

    Args:
        request: Django HTTP request
        updated_user: User object that was updated
        updated_by: User who made the update
        fields_changed: List of field names that were changed
    """
    audit_logger.info(
        f'USER UPDATED | User: {updated_user.email} (ID: {updated_user.id}) | '
        f'Updated By: {updated_by.email} (ID: {updated_by.id}) | '
        f'Fields Changed: {", ".join(fields_changed)} | '
        f'IP: {get_client_ip(request)}'
    )


def log_user_deleted(request, deleted_user_info, deleted_by):
    """
    Log user account deletion.

    Args:
        request: Django HTTP request
        deleted_user_info: Dict with user info (email, ID, name)
        deleted_by: User who deleted the account
    """
    audit_logger.warning(
        f'USER DELETED | Deleted User: {deleted_user_info["email"]} '
        f'(ID: {deleted_user_info["id"]}) | '
        f'Deleted By: {deleted_by.email} (ID: {deleted_by.id}) | '
        f'IP: {get_client_ip(request)}'
    )


def log_profile_photo_upload(request, user):
    """
    Log profile photo upload.

    Args:
        request: Django HTTP request
        user: User who uploaded photo
    """
    audit_logger.info(
        f'PROFILE PHOTO UPLOADED | User: {user.email} (ID: {user.id}) | '
        f'IP: {get_client_ip(request)}'
    )


# ==============================================================================
# CERTIFICATE OPERATIONS LOGGING
# ==============================================================================

def log_certificate_created(request, certificate, created_by):
    """
    Log certificate creation.

    Args:
        request: Django HTTP request
        certificate: Certificate object that was created
        created_by: User who created the certificate
    """
    audit_logger.info(
        f'CERTIFICATE CREATED | Certificate: {certificate.name} (ID: {certificate.id}) | '
        f'Employee: {certificate.user.email} | '
        f'Provider: {certificate.provider.name} | '
        f'Expiry: {certificate.expiry_date} | '
        f'Created By: {created_by.email} (ID: {created_by.id}) | '
        f'IP: {get_client_ip(request)}'
    )


def log_certificate_updated(request, certificate, updated_by, fields_changed):
    """
    Log certificate update.

    Args:
        request: Django HTTP request
        certificate: Certificate object that was updated
        updated_by: User who updated the certificate
        fields_changed: List of field names that were changed
    """
    audit_logger.info(
        f'CERTIFICATE UPDATED | Certificate: {certificate.name} (ID: {certificate.id}) | '
        f'Employee: {certificate.user.email} | '
        f'Updated By: {updated_by.email} (ID: {updated_by.id}) | '
        f'Fields Changed: {", ".join(fields_changed)} | '
        f'IP: {get_client_ip(request)}'
    )


def log_certificate_deleted(request, certificate_info, deleted_by):
    """
    Log certificate deletion.

    Args:
        request: Django HTTP request
        certificate_info: Dict with certificate info
        deleted_by: User who deleted the certificate
    """
    audit_logger.warning(
        f'CERTIFICATE DELETED | Certificate: {certificate_info["name"]} '
        f'(ID: {certificate_info["id"]}) | '
        f'Employee: {certificate_info["employee"]} | '
        f'Deleted By: {deleted_by.email} (ID: {deleted_by.id}) | '
        f'IP: {get_client_ip(request)}'
    )


def log_certificate_file_upload(request, certificate, uploaded_by):
    """
    Log certificate file upload.

    Args:
        request: Django HTTP request
        certificate: Certificate object
        uploaded_by: User who uploaded the file
    """
    audit_logger.info(
        f'CERTIFICATE FILE UPLOADED | Certificate: {certificate.name} (ID: {certificate.id}) | '
        f'Uploaded By: {uploaded_by.email} (ID: {uploaded_by.id}) | '
        f'IP: {get_client_ip(request)}'
    )


# ==============================================================================
# DATA EXPORT LOGGING
# ==============================================================================

def log_data_export(request, export_type, record_count):
    """
    Log data export (CSV, Excel, PDF).

    Args:
        request: Django HTTP request
        export_type: Type of export (CSV, Excel, PDF, etc.)
        record_count: Number of records exported
    """
    audit_logger.info(
        f'DATA EXPORT | Type: {export_type} | Records: {record_count} | '
        f'User: {request.user.email} (ID: {request.user.id}) | '
        f'IP: {get_client_ip(request)}'
    )


# ==============================================================================
# PERMISSION & ROLE LOGGING
# ==============================================================================

def log_permission_denied(request, resource, action):
    """
    Log unauthorized access attempt.

    Args:
        request: Django HTTP request
        resource: Resource attempted to access
        action: Action attempted
    """
    security_logger.warning(
        f'PERMISSION DENIED | User: {request.user.email if request.user.is_authenticated else "Anonymous"} | '
        f'Resource: {resource} | Action: {action} | '
        f'IP: {get_client_ip(request)} | '
        f'Path: {request.path}'
    )


def log_role_change(request, user, old_role, new_role, changed_by):
    """
    Log user role change.

    Args:
        request: Django HTTP request
        user: User whose role changed
        old_role: Previous role
        new_role: New role
        changed_by: User who made the change
    """
    audit_logger.warning(
        f'ROLE CHANGED | User: {user.email} (ID: {user.id}) | '
        f'Old Role: {old_role} | New Role: {new_role} | '
        f'Changed By: {changed_by.email} (ID: {changed_by.id}) | '
        f'IP: {get_client_ip(request)}'
    )


# ==============================================================================
# SECURITY EVENTS
# ==============================================================================

def log_suspicious_activity(request, description, severity='MEDIUM'):
    """
    Log suspicious activity.

    Args:
        request: Django HTTP request
        description: Description of suspicious activity
        severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
    """
    security_logger.warning(
        f'SUSPICIOUS ACTIVITY [{severity}] | {description} | '
        f'User: {request.user.email if request.user.is_authenticated else "Anonymous"} | '
        f'IP: {get_client_ip(request)} | '
        f'Path: {request.path} | '
        f'User-Agent: {get_user_agent(request)}'
    )


def log_security_event(event_type, description, user=None, ip_address=None):
    """
    Log general security event.

    Args:
        event_type: Type of security event
        description: Event description
        user: User involved (optional)
        ip_address: IP address (optional)
    """
    user_info = f'User: {user.email} (ID: {user.id})' if user else 'User: System'
    ip_info = f'IP: {ip_address}' if ip_address else ''

    security_logger.info(
        f'{event_type} | {description} | {user_info} | {ip_info}'
    )
