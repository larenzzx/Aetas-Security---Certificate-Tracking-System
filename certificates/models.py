"""
Certificate models for the Certificate Tracking System.

This module contains models for:
1. CertificateProvider - Organizations that issue certificates (CompTIA, AWS, Microsoft, etc.)
2. CertificateCategory - Categories for organizing certificates (Security, Cloud, Networking, etc.)
3. Certificate - Main model tracking employee certifications

Relationships:
- Certificate belongs to one User (employee)
- Certificate belongs to one Provider
- Certificate belongs to one Category
- Provider and Category can have many Certificates

Business Logic:
- Certificates can have expiry dates (or be lifetime)
- Status tracking: ACTIVE, EXPIRED, REVOKED
- File uploads for certificate images/PDFs
- Automatic expiry status calculation
- Days until expiry calculation for renewals
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class CertificateProvider(models.Model):
    """
    Model representing organizations that issue certifications.

    Examples:
    - CompTIA (Security+, Network+, A+)
    - Microsoft (Azure certifications, MCSA, MCSE)
    - AWS (Solutions Architect, Developer)
    - Cisco (CCNA, CCNP)
    - Google (Cloud certifications)
    - ISC2 (CISSP, SSCP)

    Why this model exists:
    - Centralize provider information
    - Maintain consistent provider names
    - Link to provider websites for verification
    - Track which providers are most common
    - Display provider logos in UI

    Fields explained:
    - name: Provider name (must be unique)
    - website: Official provider website
    - description: What this provider specializes in
    - logo: Optional logo image for UI display
    - is_active: Soft delete - hide obsolete providers
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the certification provider (e.g., CompTIA, Microsoft, AWS)"
    )

    website = models.URLField(
        blank=True,
        null=True,
        help_text="Official website of the provider"
    )

    description = models.TextField(
        blank=True,
        help_text="Brief description of what this provider offers"
    )

    logo = models.ImageField(
        upload_to='providers/%Y/%m/',
        blank=True,
        null=True,
        help_text="Provider logo for UI display"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Is this provider still active? (Soft delete)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Certificate Provider"
        verbose_name_plural = "Certificate Providers"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def get_certificate_count(self):
        """Return the number of certificates from this provider"""
        return self.certificates.count()

    def get_active_certificate_count(self):
        """Return the number of active certificates from this provider"""
        return self.certificates.filter(status='ACTIVE').count()


class CertificateCategory(models.Model):
    """
    Model representing categories for organizing certificates.

    Examples:
    - Security (CISSP, Security+, CEH)
    - Cloud Computing (AWS, Azure, GCP)
    - Networking (CCNA, Network+)
    - Development (Certified Developer)
    - Database (Oracle DBA, SQL certifications)
    - Project Management (PMP, PRINCE2)

    Why this model exists:
    - Organize certificates by topic/domain
    - Enable filtering by category
    - Dashboard statistics by category
    - Skill distribution visualization
    - Help identify skill gaps

    Fields explained:
    - name: Category name (unique)
    - description: What types of certs belong here
    - icon_class: CSS class for icon (e.g., 'fa-shield' for security)
    - color: Hex color code for UI theming
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., Security, Cloud Computing, Networking)"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of what certifications belong in this category"
    )

    icon_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="CSS icon class for display (e.g., 'fa-shield', 'fa-cloud')"
    )

    color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Hex color code for UI theming (e.g., #3B82F6 for blue)"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Certificate Category"
        verbose_name_plural = "Certificate Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def get_certificate_count(self):
        """Return the number of certificates in this category"""
        return self.certificates.count()

    def get_active_certificate_count(self):
        """Return the number of active certificates in this category"""
        return self.certificates.filter(status='ACTIVE').count()


class Certificate(models.Model):
    """
    Main model representing an employee's certification.

    This model tracks:
    - Who has the certificate (employee)
    - What certificate it is (name)
    - Who issued it (provider)
    - What category it belongs to
    - When it was issued and when it expires
    - Current status (active, expired, revoked)
    - Supporting documentation (file upload)

    Relationships:
    - Belongs to one User (the employee who earned it)
    - Belongs to one Provider (organization that issued it)
    - Belongs to one Category (for organization)

    Status choices explained:
    - ACTIVE: Certificate is valid and current
    - EXPIRED: Certificate has passed expiry date
    - REVOKED: Certificate was revoked by provider or admin

    Why certain fields are optional:
    - expiry_date: Some certifications are lifetime (no expiry)
    - certification_id: Not all providers issue credential IDs
    - certificate_file: User may not have digital copy
    - verification_url: Not all providers offer online verification
    """

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('REVOKED', 'Revoked'),
    ]

    # Core relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        help_text="Employee who holds this certificate"
    )

    provider = models.ForeignKey(
        CertificateProvider,
        on_delete=models.PROTECT,
        related_name='certificates',
        help_text="Organization that issued this certificate"
    )

    category = models.ForeignKey(
        CertificateCategory,
        on_delete=models.PROTECT,
        related_name='certificates',
        help_text="Category this certificate belongs to"
    )

    # Certificate details
    name = models.CharField(
        max_length=200,
        help_text="Full name of the certification (e.g., 'CompTIA Security+ CE')"
    )

    certification_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Unique credential/certification ID from provider (if applicable)"
    )

    # Dates
    issue_date = models.DateField(
        help_text="Date the certificate was issued"
    )

    expiry_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date the certificate expires (leave blank if lifetime certification)"
    )

    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        help_text="Current status of the certificate"
    )

    # Supporting documentation
    certificate_file = models.FileField(
        upload_to='certificates/%Y/%m/',
        blank=True,
        null=True,
        help_text="Upload certificate file (PDF, image, etc.)"
    )

    verification_url = models.URLField(
        blank=True,
        help_text="URL for online certificate verification (if available)"
    )

    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this certificate (renewal requirements, etc.)"
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )

    class Meta:
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"
        ordering = ['-issue_date']  # Newest first
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['provider']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['-issue_date']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.get_full_name()}"

    def is_expired(self):
        """
        Check if the certificate has expired.

        Returns:
            bool: True if certificate has expired, False otherwise

        Logic:
        - If no expiry_date, certificate is lifetime (never expires)
        - If expiry_date is in the past, certificate is expired
        - Status field may not always reflect actual expiry (can be manually overridden)
        """
        if not self.expiry_date:
            return False  # No expiry date means lifetime certification

        return self.expiry_date < timezone.now().date()

    def days_until_expiry(self):
        """
        Calculate days remaining until certificate expires.

        Returns:
            int: Number of days until expiry (negative if already expired)
            None: If certificate has no expiry date (lifetime)

        Use cases:
        - Show "Expiring soon" warnings
        - Sort certificates by urgency
        - Trigger renewal reminders
        - Dashboard statistics
        """
        if not self.expiry_date:
            return None  # Lifetime certification

        delta = self.expiry_date - timezone.now().date()
        return delta.days

    def is_expiring_soon(self, days_threshold=90):
        """
        Check if certificate is expiring within the specified threshold.

        Args:
            days_threshold (int): Number of days to consider "expiring soon" (default: 90)

        Returns:
            bool: True if expiring within threshold, False otherwise

        Use cases:
        - Dashboard warnings
        - Email reminders
        - Filter for "action needed" certificates
        """
        days_left = self.days_until_expiry()

        if days_left is None:
            return False  # Lifetime certification

        return 0 < days_left <= days_threshold

    def get_status_display_class(self):
        """
        Get DaisyUI badge class for status display.

        Returns:
            str: DaisyUI badge class name

        Mapping:
        - ACTIVE: badge-success (green)
        - EXPIRED: badge-error (red)
        - REVOKED: badge-warning (yellow/orange)
        """
        status_classes = {
            'ACTIVE': 'badge-success',
            'EXPIRED': 'badge-error',
            'REVOKED': 'badge-warning',
        }
        return status_classes.get(self.status, 'badge-neutral')

    def get_expiry_status_class(self):
        """
        Get DaisyUI badge class based on expiry status.

        Returns:
            str: DaisyUI badge class name

        Logic:
        - No expiry: badge-info (blue) - lifetime
        - Expired: badge-error (red)
        - Expiring soon (< 90 days): badge-warning (yellow)
        - Valid: badge-success (green)
        """
        if not self.expiry_date:
            return 'badge-info'  # Lifetime

        if self.is_expired():
            return 'badge-error'  # Expired

        if self.is_expiring_soon():
            return 'badge-warning'  # Expiring soon

        return 'badge-success'  # Valid

    def auto_update_status(self):
        """
        Automatically update status based on expiry date.

        This should be called:
        - In a daily cron job
        - Before displaying certificate lists
        - When certificate is saved

        Logic:
        - If expired and status is ACTIVE, change to EXPIRED
        - Doesn't change REVOKED status
        """
        if self.status == 'ACTIVE' and self.is_expired():
            self.status = 'EXPIRED'
            self.save(update_fields=['status', 'updated_at'])

    def save(self, *args, **kwargs):
        """
        Override save method to auto-update status.

        This ensures status is always accurate when certificate is saved.
        """
        # Auto-update status if certificate is expired
        if self.status == 'ACTIVE' and self.is_expired():
            self.status = 'EXPIRED'

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Get the URL for viewing this certificate's details.

        Returns:
            str: URL path to certificate detail view
        """
        from django.urls import reverse
        return reverse('certificates:detail', kwargs={'pk': self.pk})
