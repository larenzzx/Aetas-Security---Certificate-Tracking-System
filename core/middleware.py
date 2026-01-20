"""
Custom middleware for Aetas Security Certificate Tracking System.

Middleware classes:
- LoginRequiredMiddleware: Enforce authentication globally
- SecurityHeadersMiddleware: Add security headers to all responses
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.conf import settings


class LoginRequiredMiddleware:
    """
    Middleware to enforce login requirement globally.

    This middleware ensures all views require authentication except for
    explicitly whitelisted URLs (login, password reset, etc.).

    Security benefits:
    - Prevents accidental exposure of authenticated-only views
    - Enforces authentication at middleware level (before view execution)
    - Reduces need for @login_required decorator on every view
    - Centralizes authentication logic

    How it works:
    - Checks if user is authenticated
    - If not, checks if current path is in whitelist
    - If not in whitelist, redirects to login page
    - Preserves intended destination in 'next' parameter
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # URLs that don't require authentication
        self.exempt_urls = [
            reverse('accounts:login'),
            reverse('accounts:password_reset'),
            reverse('accounts:password_reset_done'),
            reverse('accounts:password_reset_complete'),
            reverse('accounts:password_change_required'),  # Allow forced password change
        ]

        # URL patterns that don't require authentication (for dynamic URLs)
        self.exempt_url_patterns = [
            '/accounts/password-reset-confirm/',  # Includes uidb64/token
            '/static/',  # Static files
            '/media/',   # Media files
        ]

    def __call__(self, request):
        # Get the current path
        path = request.path_info

        # Check if user is authenticated
        if not request.user.is_authenticated:
            # Check if path is in exempt list
            if path not in self.exempt_urls:
                # Check if path starts with any exempt pattern
                is_exempt = any(path.startswith(pattern) for pattern in self.exempt_url_patterns)

                if not is_exempt:
                    # Store intended destination
                    login_url = reverse('accounts:login')

                    # Don't add 'next' parameter if already on login page
                    if path != login_url:
                        # Redirect to login with 'next' parameter
                        return redirect(f'{login_url}?next={path}')

        # Continue processing request
        response = self.get_response(request)
        return response


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses.

    Headers added:
    - X-Content-Type-Options: Prevent MIME type sniffing
    - X-Frame-Options: Prevent clickjacking
    - X-XSS-Protection: Enable XSS filter in older browsers
    - Referrer-Policy: Control referrer information
    - Permissions-Policy: Control browser features

    Note: Some headers are also set in Django settings.py (e.g., SECURE_BROWSER_XSS_FILTER)
    but this middleware provides additional defense in depth.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # Prevent clickjacking
        if 'X-Frame-Options' not in response:
            response['X-Frame-Options'] = 'DENY'

        # XSS Protection (for older browsers)
        if 'X-XSS-Protection' not in response:
            response['X-XSS-Protection'] = '1; mode=block'

        # Referrer Policy - only send referrer for same-origin requests
        if 'Referrer-Policy' not in response:
            response['Referrer-Policy'] = 'same-origin'

        # Permissions Policy - restrict browser features
        if 'Permissions-Policy' not in response:
            response['Permissions-Policy'] = (
                'geolocation=(), '
                'microphone=(), '
                'camera=(), '
                'payment=(), '
                'usb=(), '
                'magnetometer=(), '
                'gyroscope=(), '
                'accelerometer=()'
            )

        return response


class ActivityLoggingMiddleware:
    """
    Middleware to log critical user activities.

    This middleware captures important actions for audit trails:
    - Authentication events (login, logout, failed login)
    - User management (create, edit, delete users)
    - Certificate operations (create, edit, delete)
    - Permission changes

    Logs include:
    - Timestamp
    - User (or 'Anonymous' if not authenticated)
    - Action performed
    - IP address
    - User agent
    - Success/failure status
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store request start time
        import time
        request.start_time = time.time()

        # Process request
        response = self.get_response(request)

        # Calculate request duration
        duration = time.time() - request.start_time

        # Log slow requests (> 2 seconds)
        if duration > 2.0:
            import logging
            logger = logging.getLogger('performance')
            logger.warning(
                f'Slow request: {request.method} {request.path} '
                f'took {duration:.2f}s for user {request.user}'
            )

        return response
