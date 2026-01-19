from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    """
    Custom user manager for creating users and superusers.

    Why this exists:
    - Django requires a custom manager when using AbstractBaseUser
    - Handles user creation logic (hashing passwords, setting defaults)
    - Ensures email is used as the username field instead of username
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.

        Args:
            email: Company email address (must be unique)
            password: Plain text password (will be hashed)
            **extra_fields: Additional user fields (first_name, department, etc.)

        Returns:
            User instance
        """
        if not email:
            raise ValueError('Users must have an email address')

        # Normalize email (lowercase domain, preserve case for local part)
        email = self.normalize_email(email)

        # Set default values
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', 'EMPLOYEE')

        # Create user instance (doesn't save to DB yet)
        user = self.model(email=email, **extra_fields)

        # Hash the password (NEVER store plain text passwords)
        user.set_password(password)

        # Save to database
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.

        Superusers have:
        - is_staff=True (can access Django admin)
        - is_superuser=True (has all permissions)
        - role=ADMIN (our custom role system)
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model for the Certificate Tracking System.

    Why a custom user model?
    - Default Django user uses 'username' - we need email-based authentication
    - We need additional fields (department, position, role, etc.)
    - MUST be created BEFORE first migration (can't change later)

    Inherits from:
    - AbstractBaseUser: Provides password hashing and session management
    - PermissionsMixin: Provides is_superuser, groups, and permissions
    """

    # Role choices for authorization
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('EMPLOYEE', 'Employee'),
    ]

    # ============================================
    # CORE AUTHENTICATION FIELDS
    # ============================================

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
        help_text='Company email address - used for login',
        verbose_name='Email Address'
    )
    # Why unique? Each employee needs their own account
    # Why EmailValidator? Ensures proper email format

    password = models.CharField(
        max_length=128,
        help_text='Hashed password - never stored in plain text'
    )
    # Inherited from AbstractBaseUser but documented here
    # Password is automatically hashed by set_password() method

    # ============================================
    # PERSONAL INFORMATION FIELDS
    # ============================================

    first_name = models.CharField(
        max_length=50,
        help_text='Employee first name'
    )

    last_name = models.CharField(
        max_length=50,
        help_text='Employee last name'
    )

    # ============================================
    # COMPANY INFORMATION FIELDS
    # ============================================

    department = models.CharField(
        max_length=100,
        blank=True,
        help_text='Department or team (e.g., Engineering, HR, Sales)'
    )
    # Why blank=True? Admin can create account first, update details later

    position = models.CharField(
        max_length=100,
        blank=True,
        help_text='Job title or role (e.g., Software Engineer, Manager)'
    )

    # ============================================
    # ROLE & PERMISSIONS FIELDS
    # ============================================

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='EMPLOYEE',
        help_text='User role - determines permissions in the system'
    )
    # ADMIN: Can create users, manage all certificates, assign roles
    # EMPLOYEE: Can only manage their own certificates

    is_staff = models.BooleanField(
        default=False,
        help_text='Can access Django admin panel'
    )
    # Required by Django admin - only admins should have this

    is_active = models.BooleanField(
        default=True,
        help_text='Account status - inactive users cannot log in'
    )
    # Soft delete: Set to False instead of deleting user
    # Preserves data integrity (certificates still linked to user)

    is_superuser = models.BooleanField(
        default=False,
        help_text='Has all permissions without explicitly assigning them'
    )
    # Required by PermissionsMixin - for Django admin superusers

    # ============================================
    # PROFILE & MEDIA FIELDS
    # ============================================

    profile_image = models.ImageField(
        upload_to='profiles/%Y/%m/',
        blank=True,
        null=True,
        help_text='Optional profile photo'
    )
    # upload_to: Organizes uploads by year/month (e.g., profiles/2024/01/photo.jpg)
    # Why? Prevents one huge folder with thousands of files
    # blank=True, null=True: Profile photo is optional

    # ============================================
    # PASSWORD MANAGEMENT FIELDS
    # ============================================

    must_change_password = models.BooleanField(
        default=False,
        help_text='Force password change on next login'
    )
    # Set to True when admin creates user with temporary password
    # User must change it before accessing the system

    # ============================================
    # TIMESTAMP FIELDS
    # ============================================

    date_joined = models.DateTimeField(
        default=timezone.now,
        help_text='Account creation date'
    )
    # Audit trail: When was this account created?

    last_login = models.DateTimeField(
        blank=True,
        null=True,
        help_text='Last successful login timestamp'
    )
    # Inherited from AbstractBaseUser - tracks login activity

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last profile update timestamp'
    )
    # auto_now: Automatically updates whenever user.save() is called

    # ============================================
    # DJANGO AUTH CONFIGURATION
    # ============================================

    # Tell Django to use email for authentication instead of username
    USERNAME_FIELD = 'email'

    # Additional required fields when creating superuser via command line
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # Use our custom manager
    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']  # Newest users first
        indexes = [
            models.Index(fields=['email']),  # Faster email lookups
            models.Index(fields=['role']),   # Faster role-based queries
        ]

    def __str__(self):
        """String representation of user"""
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return user's first name"""
        return self.first_name

    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'ADMIN' or self.is_superuser

    def is_employee(self):
        """Check if user has employee role"""
        return self.role == 'EMPLOYEE'

    @property
    def certificate_count(self):
        """Return total number of certificates owned by this user"""
        return self.certificates.count()

    @property
    def active_certificate_count(self):
        """Return number of active (non-expired) certificates"""
        return self.certificates.filter(status='ACTIVE').count()
