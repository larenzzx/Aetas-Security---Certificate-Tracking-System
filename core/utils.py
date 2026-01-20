"""
Utility functions for the Certificate Tracking System.

This module contains helper functions used across the application:
- Password generation
- Email utilities
- String formatting helpers
"""

import secrets
import string


def generate_temporary_password(length=12):
    """
    Generate a secure temporary password.

    Why this function exists:
    - Admin creates users but shouldn't manually type passwords
    - Passwords must be cryptographically secure
    - Must meet Django's password validation requirements
    - Should be memorable enough to type once

    Args:
        length (int): Length of password (default: 12)

    Returns:
        str: Randomly generated password

    Security considerations:
    - Uses secrets module (cryptographically secure)
    - Includes uppercase, lowercase, digits, and special chars
    - Meets Django's default validators:
      ✓ At least 8 characters
      ✓ Not entirely numeric
      ✓ Not too common
      ✓ Not too similar to user info

    Example output:
        "Kx9#mP2qL5vN"
    """
    # Character sets
    lowercase = string.ascii_lowercase  # a-z
    uppercase = string.ascii_uppercase  # A-Z
    digits = string.digits              # 0-9
    special = "!@#$%^&*"               # Safe special characters (avoid confusing ones like l, I, 0, O)

    # Ensure at least one character from each set
    # This guarantees the password meets complexity requirements
    password_chars = [
        secrets.choice(uppercase),  # At least 1 uppercase
        secrets.choice(lowercase),  # At least 1 lowercase
        secrets.choice(digits),     # At least 1 digit
        secrets.choice(special),    # At least 1 special char
    ]

    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + special
    password_chars.extend(
        secrets.choice(all_chars) for _ in range(length - 4)
    )

    # Shuffle to avoid predictable pattern (uppercase always first, etc.)
    # secrets.SystemRandom() is cryptographically secure
    secrets.SystemRandom().shuffle(password_chars)

    return ''.join(password_chars)


def format_full_name(first_name, last_name):
    """
    Format user's full name consistently.

    Args:
        first_name (str): User's first name
        last_name (str): User's last name

    Returns:
        str: Formatted full name

    Example:
        format_full_name("john", "doe") → "John Doe"
    """
    return f"{first_name.strip().title()} {last_name.strip().title()}"


def mask_password(password, visible_chars=3):
    """
    Mask password for display purposes (e.g., in logs).

    Args:
        password (str): Password to mask
        visible_chars (int): Number of characters to show at the end

    Returns:
        str: Masked password

    Example:
        mask_password("MyPassword123") → "**********123"

    Security note:
    - Never log full passwords
    - Only use masked passwords for audit trails
    """
    if len(password) <= visible_chars:
        return '*' * len(password)

    mask_length = len(password) - visible_chars
    visible_part = password[-visible_chars:]
    return ('*' * mask_length) + visible_part


def normalize_email_domain(email):
    """
    Extract and normalize email domain.

    Args:
        email (str): Email address

    Returns:
        str: Lowercase domain

    Example:
        normalize_email_domain("User@COMPANY.COM") → "company.com"
    """
    if '@' not in email:
        return ''

    domain = email.split('@')[1]
    return domain.lower()


def generate_username_from_email(email):
    """
    Generate a username from email (fallback for systems that need it).

    Args:
        email (str): Email address

    Returns:
        str: Username

    Example:
        generate_username_from_email("john.doe@company.com") → "john.doe"

    Note:
    - Our system uses email as username, so this is rarely needed
    - Provided for compatibility with third-party integrations
    """
    if '@' in email:
        return email.split('@')[0].lower()
    return email.lower()
