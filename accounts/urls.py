"""
URL configuration for accounts app.

Authentication URLs:
- Login/Logout
- Password reset (forgot password)
- Password change (logged-in users)
- Forced password change (first-time users)

Profile URLs (placeholders for later steps):
- User profile view
- Employee list
- User creation (admin only)
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ============================================
    # AUTHENTICATION URLs
    # ============================================

    # Login & Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Password Reset Flow (Forgot Password)
    path(
        'password-reset/',
        views.CustomPasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        views.CustomPasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        views.CustomPasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'password-reset-complete/',
        views.CustomPasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),

    # Password Change (for logged-in users)
    path(
        'password-change/',
        views.CustomPasswordChangeView.as_view(),
        name='password_change'
    ),

    # Forced Password Change (for users with must_change_password=True)
    path(
        'password-change-required/',
        views.password_change_required_view,
        name='password_change_required'
    ),

    # ============================================
    # PROFILE URLs (Placeholders for later steps)
    # ============================================

    # View user profile
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),

    # Edit user profile
    path('profile/<int:user_id>/edit/', views.profile_edit, name='profile_edit'),

    # View all employees
    path('employees/', views.profile_list, name='profile_list'),

    # Create new user (Admin only)
    path('users/create/', views.user_create, name='user_create'),
    path('users/create/success/', views.user_create_success, name='user_create_success'),

    # Delete user (Admin only)
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
]
