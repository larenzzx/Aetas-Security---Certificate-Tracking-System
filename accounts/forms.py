"""
Forms for user management in the Certificate Tracking System.

This module contains forms for:
- User creation (admin only)
- User profile updates
- Password management
"""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    """
    Form for admins to create new users.

    Key features:
    - No password field (auto-generated)
    - Email validation (must be unique)
    - Role selection (Admin or Employee)
    - Optional department and position
    - Sets must_change_password=True automatically

    Security:
    - Only accessible to admin users (enforced in view)
    - Temporary password generated server-side
    - User forced to change password on first login
    """

    # Override role field to make it a required choice field with widget styling
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial='EMPLOYEE',
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        help_text='Select the user role (Admin can create users and manage all certificates)'
    )

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'role',
            'department',
            'position',
            'is_active',
        ]

        # Customize widgets for DaisyUI styling
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'user.name@company.com',
                'autofocus': True,
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'John',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Doe',
            }),
            'department': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '',
            }),
            'position': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'SOC Analyst, Helpdesk, etc.',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary',
            }),
        }

        # Custom labels
        labels = {
            'email': 'Company Email Address',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'role': 'User Role',
            'department': 'Department / Team',
            'position': 'Job Title / Position',
            'is_active': 'Active Account',
        }

        # Help texts
        help_texts = {
            'email': 'User will use this email to log in. Must be unique.',
            'first_name': 'User\'s first name',
            'last_name': 'User\'s last name',
            'department': 'Optional: Department or team (e.g., Engineering, HR)',
            'position': 'Optional: Job title or position (e.g., Software Engineer)',
            'is_active': 'Uncheck to create a disabled account (user cannot log in)',
        }

    def clean_email(self):
        """
        Validate email field.

        Checks:
        1. Email is not already taken
        2. Email is from a valid domain (optional - can add company domain check)

        Returns:
            str: Cleaned email (lowercase)

        Raises:
            ValidationError: If email already exists
        """
        email = self.cleaned_data.get('email')

        if not email:
            raise ValidationError('Email is required.')

        # Normalize email (lowercase)
        email = email.lower().strip()

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                f'A user with the email "{email}" already exists. '
                'Please use a different email address.'
            )

        # Optional: Validate company domain
        # Uncomment and modify if you want to restrict to specific domains
        # allowed_domains = ['company.com', 'company.co.uk']
        # domain = email.split('@')[1] if '@' in email else ''
        # if domain not in allowed_domains:
        #     raise ValidationError(
        #         f'Email must be from an approved company domain: {", ".join(allowed_domains)}'
        #     )

        return email

    def clean_first_name(self):
        """Validate and normalize first name."""
        first_name = self.cleaned_data.get('first_name', '').strip()

        if not first_name:
            raise ValidationError('First name is required.')

        if len(first_name) < 2:
            raise ValidationError('First name must be at least 2 characters long.')

        # Capitalize first letter
        return first_name.title()

    def clean_last_name(self):
        """Validate and normalize last name."""
        last_name = self.cleaned_data.get('last_name', '').strip()

        if not last_name:
            raise ValidationError('Last name is required.')

        if len(last_name) < 2:
            raise ValidationError('Last name must be at least 2 characters long.')

        # Capitalize first letter
        return last_name.title()

    def clean_department(self):
        """Normalize department (optional field)."""
        department = self.cleaned_data.get('department', '').strip()
        return department.title() if department else ''

    def clean_position(self):
        """Normalize position (optional field)."""
        position = self.cleaned_data.get('position', '').strip()
        return position.title() if position else ''

    def save(self, commit=True, temporary_password=None):
        """
        Save the user instance.

        This method is called by the view after generating a temporary password.

        Args:
            commit (bool): Whether to save to database
            temporary_password (str): The generated temporary password

        Returns:
            User: The created user instance

        Important:
        - Must set must_change_password=True
        - Must set is_staff=True for admin users
        - Password is hashed automatically by set_password()
        """
        user = super().save(commit=False)

        # Set password (will be hashed automatically)
        if temporary_password:
            user.set_password(temporary_password)
        else:
            raise ValueError('Temporary password must be provided')

        # Force password change on first login
        user.must_change_password = True

        # Set is_staff based on role
        # Admin role users should have access to Django admin
        if user.role == 'ADMIN':
            user.is_staff = True
        else:
            user.is_staff = False

        if commit:
            user.save()

        return user


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user profiles.

    Can be used by:
    - Users to update their own profile (limited fields)
    - Admins to update any user profile (all fields including role)

    Features:
    - Profile photo upload with validation
    - Personal information updates
    - Department and position management
    - Role management (admin only)
    - Image size and format validation
    """

    # Add a checkbox to remove profile image
    remove_profile_image = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'checkbox checkbox-error',
        }),
        label='Remove current profile photo',
        help_text='Check this to remove your profile photo and revert to initials'
    )

    # Role field (will be shown only to admins via __init__)
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        label='User Role',
        help_text='Admin can manage all users and certificates. Employee can manage only their own certificates.'
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'department',
            'position',
            'profile_image',
            'role',  # Added for admin use
        ]

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Last Name'
            }),
            'department': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': ''
            }),
            'position': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'SOC Analyst, Helpdesk, etc.'
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/jpeg,image/png,image/jpg,image/webp'
            }),
        }

        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'department': 'Department',
            'position': 'Position',
            'profile_image': 'Profile Photo',
        }

        help_texts = {
            'first_name': 'Your first name',
            'last_name': 'Your last name',
            'department': 'Optional: Your department or team',
            'position': 'Optional: Your job title',
            'profile_image': 'Upload a profile photo (JPG, PNG, or WebP - Max 5MB)',
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize form with conditional role field visibility.

        The role field is only shown to admin users.
        Regular employees cannot change their own or others' roles.
        """
        # Extract current user from kwargs
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        # Hide role field for non-admin users
        if not self.current_user or not self.current_user.is_admin():
            # Remove role field from form if user is not admin
            self.fields.pop('role', None)
        else:
            # Admin can see and edit role
            # Set initial value to current role
            if self.instance and self.instance.pk:
                self.fields['role'].initial = self.instance.role

    def clean_first_name(self):
        """Validate and normalize first name."""
        first_name = self.cleaned_data.get('first_name', '').strip()

        if not first_name:
            raise ValidationError('First name is required.')

        if len(first_name) < 2:
            raise ValidationError('First name must be at least 2 characters long.')

        return first_name.title()

    def clean_last_name(self):
        """Validate and normalize last name."""
        last_name = self.cleaned_data.get('last_name', '').strip()

        if not last_name:
            raise ValidationError('Last name is required.')

        if len(last_name) < 2:
            raise ValidationError('Last name must be at least 2 characters long.')

        return last_name.title()

    def clean_role(self):
        """
        Validate role changes.

        Security checks:
        - Only admins can change roles
        - Prevent users from elevating their own permissions
        - Validate role is a valid choice
        """
        role = self.cleaned_data.get('role')

        # If role field was removed (non-admin user), return current role
        if 'role' not in self.fields:
            return self.instance.role if self.instance and self.instance.pk else 'EMPLOYEE'

        # Validate that current user is admin
        if not self.current_user or not self.current_user.is_admin():
            raise ValidationError('Only administrators can change user roles.')

        # Validate role is a valid choice
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if role not in valid_roles:
            raise ValidationError(f'Invalid role. Must be one of: {", ".join(valid_roles)}')

        return role

    def clean_profile_image(self):
        """
        Validate uploaded profile image with comprehensive security checks.

        Checks:
        - File size (max 5MB)
        - File type (JPEG, PNG, WebP)
        - MIME type verification
        - Image dimensions
        - File integrity

        Returns:
            File: Cleaned and validated image file

        Raises:
            ValidationError: If image doesn't meet security requirements
        """
        from core.validators import validate_image_file

        image = self.cleaned_data.get('profile_image')

        if not image:
            return image

        # Use comprehensive validator with security checks
        validate_image_file(image)

        return image

    def save(self, commit=True):
        """
        Save the user profile with optional image removal and role changes.

        Handles:
        - Profile image upload
        - Profile image removal
        - Personal information updates
        - Role changes (admin only)
        - Automatic is_staff update based on role
        """
        user = super().save(commit=False)

        # Handle profile image removal
        if self.cleaned_data.get('remove_profile_image'):
            # Delete old image file
            if user.profile_image:
                user.profile_image.delete(save=False)
            user.profile_image = None

        # Handle role changes (only if admin is making the change)
        if 'role' in self.cleaned_data and self.current_user and self.current_user.is_admin():
            new_role = self.cleaned_data['role']
            user.role = new_role

            # Update is_staff based on role
            # Admin role users should have access to Django admin
            if new_role == 'ADMIN':
                user.is_staff = True
            else:
                user.is_staff = False

        if commit:
            user.save()

        return user
