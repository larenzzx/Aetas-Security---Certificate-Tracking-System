from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.

    Why customize the admin?
    - Default UserAdmin expects username field - we use email
    - Need to display our custom fields (role, department, position, etc.)
    - Provide easy interface for admins to manage users
    """

    # ============================================
    # LIST VIEW CONFIGURATION
    # ============================================

    list_display = [
        'email',
        'full_name_display',
        'role_badge',
        'department',
        'position',
        'status_badge',
        'date_joined',
        'last_login',
    ]
    # Columns shown in the user list page

    list_filter = [
        'role',
        'is_active',
        'is_staff',
        'department',
        'date_joined',
    ]
    # Filters in the right sidebar

    search_fields = [
        'email',
        'first_name',
        'last_name',
        'department',
        'position',
    ]
    # Fields searchable in the search box

    ordering = ['-date_joined']
    # Default ordering (newest first)

    list_per_page = 25
    # Show 25 users per page

    # ============================================
    # DETAIL VIEW CONFIGURATION
    # ============================================

    fieldsets = (
        # Authentication section
        ('Authentication', {
            'fields': ('email', 'password')
        }),

        # Personal information section
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'profile_image')
        }),

        # Company information section
        ('Company Information', {
            'fields': ('department', 'position')
        }),

        # Permissions section
        ('Permissions', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'must_change_password',
            ),
            'description': 'Control user access and permissions'
        }),

        # Metadata section
        ('Metadata', {
            'fields': ('date_joined', 'last_login', 'updated_at'),
            'classes': ('collapse',),  # Collapsed by default
        }),
    )
    # Organization of fields in the detail/edit page

    readonly_fields = ['date_joined', 'last_login', 'updated_at']
    # Fields that cannot be edited (auto-generated)

    # ============================================
    # ADD USER CONFIGURATION
    # ============================================

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2',
                'role',
                'department',
                'position',
                'is_active',
                'must_change_password',
            ),
        }),
    )
    # Fields shown when creating a new user

    # ============================================
    # CUSTOM DISPLAY METHODS
    # ============================================

    def full_name_display(self, obj):
        """Display full name"""
        return obj.get_full_name()
    full_name_display.short_description = 'Full Name'

    def role_badge(self, obj):
        """Display role as a colored badge"""
        if obj.role == 'ADMIN':
            color = '#dc2626'  # Red for admin
            icon = '👑'
        else:
            color = '#2563eb'  # Blue for employee
            icon = '👤'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_role_display()
        )
    role_badge.short_description = 'Role'

    def status_badge(self, obj):
        """Display account status as a colored badge"""
        if obj.is_active:
            color = '#16a34a'  # Green
            icon = '✓'
            text = 'Active'
        else:
            color = '#dc2626'  # Red
            icon = '✗'
            text = 'Inactive'

        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, text
        )
    status_badge.short_description = 'Status'

    # ============================================
    # ACTIONS
    # ============================================

    actions = [
        'activate_users',
        'deactivate_users',
        'reset_password_flag',
    ]

    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} user(s) were successfully activated.'
        )
    activate_users.short_description = 'Activate selected users'

    def deactivate_users(self, request, queryset):
        """Deactivate selected users (soft delete)"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} user(s) were successfully deactivated.'
        )
    deactivate_users.short_description = 'Deactivate selected users'

    def reset_password_flag(self, request, queryset):
        """Force selected users to change password on next login"""
        updated = queryset.update(must_change_password=True)
        self.message_user(
            request,
            f'{updated} user(s) will be required to change password on next login.'
        )
    reset_password_flag.short_description = 'Force password change on next login'


# Register the User model with our custom admin
admin.site.register(User, UserAdmin)

# Customize admin site header and title
admin.site.site_header = 'Certificate Tracking System - Administration'
admin.site.site_title = 'CTS Admin'
admin.site.index_title = 'System Administration'
