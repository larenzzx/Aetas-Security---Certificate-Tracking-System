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
                'placeholder': 'Engineering, HR, Sales, etc.',
            }),
            'position': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Software Engineer, Manager, etc.',
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
    - Admins to update any user profile (all fields)

    Features:
    - Profile photo upload with validation
    - Personal information updates
    - Department and position management
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

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'department',
            'position',
            'profile_image',
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
                'placeholder': 'Department or Team'
            }),
            'position': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Job Title or Position'
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

    def clean_profile_image(self):
        """
        Validate uploaded profile image.

        Checks:
        - File size (max 5MB)
        - File type (JPEG, PNG, WebP)
        - Image dimensions (optional)

        Returns:
            File: Cleaned image file

        Raises:
            ValidationError: If image doesn't meet requirements
        """
        image = self.cleaned_data.get('profile_image')

        if not image:
            return image

        # Check file size (5MB max)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if image.size > max_size:
            raise ValidationError(
                f'Image file size cannot exceed 5MB. '
                f'Your file is {image.size / (1024 * 1024):.1f}MB.'
            )

        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if hasattr(image, 'content_type'):
            if image.content_type not in allowed_types:
                raise ValidationError(
                    'Invalid image format. Please upload a JPG, PNG, or WebP image.'
                )

        # Check file extension
        if hasattr(image, 'name'):
            ext = image.name.lower().split('.')[-1]
            if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                raise ValidationError(
                    'Invalid file extension. Allowed: jpg, jpeg, png, webp'
                )

        return image

    def save(self, commit=True):
        """
        Save the user profile with optional image removal.

        Handles:
        - Profile image upload
        - Profile image removal
        - Personal information updates
        """
        user = super().save(commit=False)

        # Handle profile image removal
        if self.cleaned_data.get('remove_profile_image'):
            # Delete old image file
            if user.profile_image:
                user.profile_image.delete(save=False)
            user.profile_image = None

        if commit:
            user.save()

        return user
