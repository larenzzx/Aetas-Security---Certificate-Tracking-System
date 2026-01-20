"""
Django admin configuration for certificate models.

This module configures the Django admin interface for managing:
- Certificate Providers
- Certificate Categories
- Certificates

Features:
- Custom list displays with relevant fields
- Search functionality
- Filtering options
- Inline editing where appropriate
- Custom actions for bulk operations
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import CertificateProvider, CertificateCategory, Certificate


@admin.register(CertificateProvider)
class CertificateProviderAdmin(admin.ModelAdmin):
    """
    Admin configuration for CertificateProvider model.

    Features:
    - List display shows name, website, certificate count, and active status
    - Search by provider name
    - Filter by active status
    - Display certificate count
    """

    list_display = [
        'name',
        'website_link',
        'certificate_count',
        'active_certificate_count',
        'is_active',
        'created_at'
    ]

    list_filter = [
        'is_active',
        'created_at',
    ]

    search_fields = [
        'name',
        'description',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'certificate_count',
        'active_certificate_count',
    ]

    fieldsets = (
        ('Provider Information', {
            'fields': ('name', 'website', 'description', 'logo')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Statistics', {
            'fields': ('certificate_count', 'active_certificate_count'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def website_link(self, obj):
        """Display website as clickable link"""
        if obj.website:
            return format_html('<a href="{}" target="_blank">{}</a>', obj.website, 'Visit Website')
        return '-'
    website_link.short_description = 'Website'

    def certificate_count(self, obj):
        """Display total number of certificates from this provider"""
        return obj.get_certificate_count()
    certificate_count.short_description = 'Total Certificates'

    def active_certificate_count(self, obj):
        """Display number of active certificates from this provider"""
        return obj.get_active_certificate_count()
    active_certificate_count.short_description = 'Active Certificates'


@admin.register(CertificateCategory)
class CertificateCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for CertificateCategory model.

    Features:
    - List display shows name, color preview, certificate count
    - Search by category name
    - Display certificate count
    - Color preview in list
    """

    list_display = [
        'name',
        'color_preview',
        'icon_class',
        'certificate_count',
        'active_certificate_count',
        'created_at',
    ]

    search_fields = [
        'name',
        'description',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'certificate_count',
        'active_certificate_count',
    ]

    fieldsets = (
        ('Category Information', {
            'fields': ('name', 'description')
        }),
        ('Display Settings', {
            'fields': ('icon_class', 'color'),
            'description': 'Settings for how this category appears in the UI'
        }),
        ('Statistics', {
            'fields': ('certificate_count', 'active_certificate_count'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def color_preview(self, obj):
        """Display color as a preview box"""
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: {}; border: 1px solid #ccc; border-radius: 4px;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'

    def certificate_count(self, obj):
        """Display total number of certificates in this category"""
        return obj.get_certificate_count()
    certificate_count.short_description = 'Total Certificates'

    def active_certificate_count(self, obj):
        """Display number of active certificates in this category"""
        return obj.get_active_certificate_count()
    active_certificate_count.short_description = 'Active Certificates'


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """
    Admin configuration for Certificate model.

    Features:
    - List display shows key information
    - Search by name, user, certification ID
    - Filter by status, provider, category, expiry
    - Custom actions for bulk status updates
    - Automatic expiry status updates
    """

    list_display = [
        'name',
        'user_link',
        'provider',
        'category',
        'status_badge',
        'issue_date',
        'expiry_date',
        'days_left',
        'created_at',
    ]

    list_filter = [
        'status',
        'provider',
        'category',
        ('expiry_date', admin.DateFieldListFilter),
        'issue_date',
    ]

    search_fields = [
        'name',
        'certification_id',
        'user__first_name',
        'user__last_name',
        'user__email',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'days_left',
        'expiry_status',
    ]

    autocomplete_fields = [
        'user',
    ]

    fieldsets = (
        ('Certificate Details', {
            'fields': ('user', 'name', 'certification_id', 'provider', 'category')
        }),
        ('Dates', {
            'fields': ('issue_date', 'expiry_date', 'days_left', 'expiry_status')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Documentation', {
            'fields': ('certificate_file', 'verification_url', 'notes'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = [
        'mark_as_active',
        'mark_as_expired',
        'mark_as_revoked',
        'update_expiry_status',
    ]

    def user_link(self, obj):
        """Display user as clickable link to user admin"""
        from django.urls import reverse
        from django.utils.html import format_html

        url = reverse('admin:accounts_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
    user_link.short_description = 'User'

    def status_badge(self, obj):
        """Display status as colored badge"""
        badge_class = obj.get_status_display_class()
        color_map = {
            'badge-success': '#36D399',  # Green
            'badge-error': '#F87272',    # Red
            'badge-warning': '#FBBD23',  # Yellow
            'badge-neutral': '#A6ADBB',  # Gray
        }
        color = color_map.get(badge_class, '#A6ADBB')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def days_left(self, obj):
        """Display days until expiry with color coding"""
        days = obj.days_until_expiry()

        if days is None:
            return format_html('<span style="color: #3B82F6;">Lifetime</span>')

        if days < 0:
            return format_html('<span style="color: #F87272;">Expired {} days ago</span>', abs(days))
        elif days == 0:
            return format_html('<span style="color: #F87272;">Expires today!</span>')
        elif days <= 30:
            return format_html('<span style="color: #F87272;">{} days</span>', days)
        elif days <= 90:
            return format_html('<span style="color: #FBBD23;">{} days</span>', days)
        else:
            return format_html('<span style="color: #36D399;">{} days</span>', days)
    days_left.short_description = 'Days Until Expiry'

    def expiry_status(self, obj):
        """Display expiry status with badge"""
        badge_class = obj.get_expiry_status_class()
        color_map = {
            'badge-success': '#36D399',  # Green - Valid
            'badge-error': '#F87272',    # Red - Expired
            'badge-warning': '#FBBD23',  # Yellow - Expiring Soon
            'badge-info': '#3B82F6',     # Blue - Lifetime
        }
        color = color_map.get(badge_class, '#A6ADBB')

        if not obj.expiry_date:
            text = 'Lifetime'
        elif obj.is_expired():
            text = 'Expired'
        elif obj.is_expiring_soon():
            text = 'Expiring Soon'
        else:
            text = 'Valid'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{}</span>',
            color,
            text
        )
    expiry_status.short_description = 'Expiry Status'

    # Custom Actions
    def mark_as_active(self, request, queryset):
        """Bulk action to mark certificates as active"""
        updated = queryset.update(status='ACTIVE')
        self.message_user(request, f'{updated} certificate(s) marked as active.')
    mark_as_active.short_description = 'Mark selected certificates as Active'

    def mark_as_expired(self, request, queryset):
        """Bulk action to mark certificates as expired"""
        updated = queryset.update(status='EXPIRED')
        self.message_user(request, f'{updated} certificate(s) marked as expired.')
    mark_as_expired.short_description = 'Mark selected certificates as Expired'

    def mark_as_revoked(self, request, queryset):
        """Bulk action to mark certificates as revoked"""
        updated = queryset.update(status='REVOKED')
        self.message_user(request, f'{updated} certificate(s) marked as revoked.')
    mark_as_revoked.short_description = 'Mark selected certificates as Revoked'

    def update_expiry_status(self, request, queryset):
        """Bulk action to auto-update expiry status based on expiry date"""
        updated_count = 0
        for certificate in queryset:
            if certificate.status == 'ACTIVE' and certificate.is_expired():
                certificate.status = 'EXPIRED'
                certificate.save()
                updated_count += 1

        self.message_user(request, f'{updated_count} certificate(s) auto-updated to expired status.')
    update_expiry_status.short_description = 'Auto-update expiry status'
