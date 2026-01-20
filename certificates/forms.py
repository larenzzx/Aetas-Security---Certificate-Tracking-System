"""
Forms for certificate CRUD operations.

This module provides forms for:
- Creating new certificates
- Editing existing certificates
- Filtering/searching certificates

Forms include:
- Proper field widgets for better UX
- Validation rules
- Help text for users
- DaisyUI styling via CSS classes
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Certificate, CertificateProvider, CertificateCategory


class CertificateForm(forms.ModelForm):
    """
    Form for creating and editing certificates.

    Features:
    - Date pickers for issue/expiry dates
    - File upload for certificate documents
    - Validation to ensure expiry > issue date
    - Optional fields marked clearly
    - DaisyUI-compatible widgets
    - Manual provider input (auto-creates if doesn't exist)

    Usage:
        # Create form
        form = CertificateForm(request.POST, request.FILES)

        # Edit form
        form = CertificateForm(request.POST, instance=certificate)

    Permission handling:
    - User field is set in the view based on permissions
    - Admins can assign to any user
    - Employees can only assign to themselves
    """

    # Override provider field to be a text input instead of select
    provider_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'e.g., CompTIA, Microsoft, AWS',
            'list': 'provider-datalist',
        }),
        label='Certification Provider',
        help_text='Type the provider name. If it doesn\'t exist, it will be created automatically.'
    )

    class Meta:
        model = Certificate
        fields = [
            'user',
            'name',
            'certification_id',
            'issue_date',
            'expiry_date',
            'status',
            'certificate_file',
            'verification_url',
            'notes',
        ]

        widgets = {
            'user': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., CompTIA Security+ CE',
            }),
            'certification_id': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., COMP001234567 (optional)',
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date',
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date',
                'placeholder': 'Leave blank for lifetime certification',
            }),
            'status': forms.Select(attrs={
                'class': 'select select-bordered w-full',
            }),
            'certificate_file': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': '.pdf,.jpg,.jpeg,.png',
            }),
            'verification_url': forms.URLInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'https://verify.provider.com (optional)',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 4,
                'placeholder': 'Additional notes, renewal requirements, etc. (optional)',
            }),
        }

        labels = {
            'user': 'Employee',
            'name': 'Certificate Name',
            'certification_id': 'Certification ID',
            'issue_date': 'Issue Date',
            'expiry_date': 'Expiry Date',
            'status': 'Status',
            'certificate_file': 'Certificate File',
            'verification_url': 'Verification URL',
            'notes': 'Notes',
        }

        help_texts = {
            'name': 'Full name of the certification',
            'certification_id': 'Unique credential ID from provider (if applicable)',
            'issue_date': 'Date the certificate was issued',
            'expiry_date': 'Leave blank if this is a lifetime certification',
            'status': 'Current status of the certificate',
            'certificate_file': 'Upload certificate PDF or image (optional)',
            'verification_url': 'URL for online verification (if available)',
            'notes': 'Any additional information about this certificate',
        }

    def __init__(self, *args, **kwargs):
        """
        Initialize form with custom configurations.

        Args:
            user: Current user (for permission-based field filtering)
            is_admin: Whether current user is admin
        """
        self.current_user = kwargs.pop('current_user', None)
        self.is_admin = kwargs.pop('is_admin', False)
        super().__init__(*args, **kwargs)

        # If editing existing certificate, populate provider_name with current provider
        if self.instance.pk and self.instance.provider:
            self.fields['provider_name'].initial = self.instance.provider.name

        # If not admin, hide user field (will be set in view)
        if not self.is_admin:
            self.fields['user'].widget = forms.HiddenInput()
            self.fields['user'].required = False
        else:
            # Admins can assign to any user
            from accounts.models import User
            self.fields['user'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')

        # Set today as default for issue_date if creating new certificate
        if not self.instance.pk:
            self.fields['issue_date'].initial = timezone.now().date()

    def clean_provider_name(self):
        """
        Clean and process the provider name.

        Gets existing provider by name (case-insensitive) or prepares to create new one.
        Returns the provider name (will be converted to provider object in save).
        """
        provider_name = self.cleaned_data.get('provider_name', '').strip()

        if not provider_name:
            raise ValidationError('Provider name is required.')

        # Validate length
        if len(provider_name) > 100:
            raise ValidationError('Provider name must be 100 characters or less.')

        return provider_name

    def clean(self):
        """
        Custom validation for the form.

        Validates:
        1. Expiry date must be after issue date (if provided)
        2. Issue date cannot be in the future
        3. User is set (either from form or from view)
        4. Provider name is processed
        """
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')
        user = cleaned_data.get('user')

        # Validate issue date is not in the future
        if issue_date and issue_date > timezone.now().date():
            raise ValidationError({
                'issue_date': 'Issue date cannot be in the future.'
            })

        # Validate expiry date is after issue date
        if issue_date and expiry_date:
            if expiry_date <= issue_date:
                raise ValidationError({
                    'expiry_date': 'Expiry date must be after issue date.'
                })

        # Ensure user is set
        if not self.is_admin and not user:
            if self.current_user:
                cleaned_data['user'] = self.current_user

        return cleaned_data

    def save(self, commit=True):
        """
        Save the certificate.

        Handles:
        1. Getting or creating provider based on provider_name
        2. Setting user to current user if not admin
        3. Saving the certificate
        """
        certificate = super().save(commit=False)

        # Get or create provider based on provider_name
        provider_name = self.cleaned_data.get('provider_name')
        if provider_name:
            # Try to get existing provider (case-insensitive)
            try:
                provider = CertificateProvider.objects.get(name__iexact=provider_name)
            except CertificateProvider.DoesNotExist:
                # Create new provider if it doesn't exist
                provider = CertificateProvider.objects.create(
                    name=provider_name,
                    is_active=True
                )

            certificate.provider = provider

        # Set user to current user if not admin and not already set
        if not self.is_admin and not certificate.user_id:
            if self.current_user:
                certificate.user = self.current_user

        if commit:
            certificate.save()

        return certificate


class CertificateFilterForm(forms.Form):
    """
    Form for filtering and searching certificates.

    Used in the certificate list view for:
    - Search by name or certification ID
    - Filter by provider
    - Filter by category
    - Filter by status

    Note: This form is used with DataTables server-side processing
    """

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input input-bordered w-full',
            'placeholder': 'Search certificates...',
        }),
        label='Search'
    )

    provider = forms.ModelChoiceField(
        required=False,
        queryset=CertificateProvider.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        label='Provider',
        empty_label='All Providers'
    )

    category = forms.ModelChoiceField(
        required=False,
        queryset=CertificateCategory.objects.all(),
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        label='Category',
        empty_label='All Categories'
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Certificate.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'select select-bordered w-full',
        }),
        label='Status'
    )


class QuickAddProviderForm(forms.ModelForm):
    """
    Quick form for adding a provider from the certificate creation page.

    Features:
    - Minimal fields for quick addition
    - Can be used in a modal popup
    - Automatically sets is_active=True
    """

    class Meta:
        model = CertificateProvider
        fields = ['name', 'website', 'description']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., CompTIA',
            }),
            'website': forms.URLInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'https://www.provider.com (optional)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Brief description (optional)',
            }),
        }

    def save(self, commit=True):
        """Ensure is_active is set to True"""
        provider = super().save(commit=False)
        provider.is_active = True

        if commit:
            provider.save()

        return provider


class QuickAddCategoryForm(forms.ModelForm):
    """
    Quick form for adding a category from the certificate creation page.

    Features:
    - Minimal fields for quick addition
    - Can be used in a modal popup
    - Default color set
    """

    class Meta:
        model = CertificateCategory
        fields = ['name', 'description', 'color']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g., Security',
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea textarea-bordered w-full',
                'rows': 3,
                'placeholder': 'Brief description (optional)',
            }),
            'color': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'color',
            }),
        }

        help_texts = {
            'color': 'Choose a color for this category in the UI',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default color if not editing
        if not self.instance.pk:
            self.fields['color'].initial = '#3B82F6'
