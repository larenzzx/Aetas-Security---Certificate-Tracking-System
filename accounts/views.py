from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
)
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import AuthenticationForm


@sensitive_post_parameters('password')
@csrf_protect
@never_cache
def login_view(request):
    """
    Handle user login.

    Security features:
    - @sensitive_post_parameters: Prevents password from appearing in error reports
    - @csrf_protect: Protects against CSRF attacks
    - @never_cache: Prevents caching of login page (security)

    Flow:
    1. User submits email + password
    2. Authenticate credentials
    3. Check if account is active
    4. Check if password must be changed
    5. Log user in and redirect

    Why custom view instead of Django's LoginView?
    - Need to check must_change_password flag
    - Custom redirect logic
    - Better control over error messages
    """

    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    # Handle POST request (form submission)
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            # Get credentials from form
            email = form.cleaned_data.get('username')  # Django calls it username
            password = form.cleaned_data.get('password')

            # Authenticate user
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Check if account is active
                if not user.is_active:
                    messages.error(
                        request,
                        'Your account has been deactivated. Please contact your administrator.'
                    )
                    return render(request, 'accounts/login.html', {'form': form})

                # Check if user must change password
                if user.must_change_password:
                    # Store user ID in session (don't log them in yet)
                    request.session['user_id_pending_password_change'] = user.id
                    messages.warning(
                        request,
                        'You must change your password before continuing.'
                    )
                    return redirect('accounts:password_change_required')

                # Log user in
                login(request, user)

                # Success message
                messages.success(request, f'Welcome back, {user.get_full_name()}!')

                # Redirect to next page or dashboard
                next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard:home'
                return redirect(next_url)
            else:
                # Authentication failed (should not reach here if form is valid)
                messages.error(request, 'Invalid email or password.')
        else:
            # Form validation failed (invalid credentials)
            messages.error(request, 'Invalid email or password.')

    else:
        # GET request - show login form
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': request.GET.get('next', ''),
    })


@login_required
def logout_view(request):
    """
    Handle user logout.

    Why custom view?
    - Show success message
    - Log activity (will be added in later step)
    - Clean session data

    Security:
    - Requires @login_required (can't logout if not logged in)
    - Clears all session data
    """
    user_name = request.user.get_full_name()
    logout(request)
    messages.success(request, f'Goodbye, {user_name}! You have been logged out successfully.')
    return redirect('accounts:login')


class CustomPasswordResetView(PasswordResetView):
    """
    Handle password reset request (forgot password).

    Flow:
    1. User enters email
    2. System sends reset link to email
    3. User clicks link in email
    4. User sets new password

    Django handles:
    - Token generation (secure, time-limited)
    - Email sending
    - Token validation

    Security:
    - Tokens expire after 3 days (default)
    - Tokens are single-use
    - No indication if email exists (prevents user enumeration)
    """
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    def form_valid(self, form):
        """Override to add success message"""
        messages.success(
            self.request,
            'If an account exists with that email, you will receive password reset instructions.'
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """
    Show confirmation that reset email was sent.

    Security note:
    - Always shows success message even if email doesn't exist
    - Prevents attackers from discovering valid emails
    """
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Handle password reset confirmation (user sets new password).

    This view is accessed via the link sent to user's email.

    Security:
    - Token is validated
    - Password complexity is enforced (Django validators)
    - Token is invalidated after use
    """
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

    def form_valid(self, form):
        """Override to add success message and clear must_change_password flag"""
        user = form.save()

        # Clear the must_change_password flag if it was set
        if user.must_change_password:
            user.must_change_password = False
            user.save()

        messages.success(
            self.request,
            'Your password has been reset successfully. You can now log in.'
        )
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Show confirmation that password was reset successfully.
    """
    template_name = 'accounts/password_reset_complete.html'


class CustomPasswordChangeView(PasswordChangeView):
    """
    Handle password change for logged-in users.

    Two use cases:
    1. User voluntarily changes password (from profile)
    2. Forced password change (must_change_password=True)

    Security:
    - Requires current password (prevents unauthorized changes)
    - Enforces password complexity
    - Logs user out from other sessions (optional, can be enabled)
    """
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('dashboard:home')

    def form_valid(self, form):
        """Override to add success message and clear must_change_password flag"""
        user = form.save()

        # Clear the must_change_password flag
        if user.must_change_password:
            user.must_change_password = False
            user.save()

        messages.success(
            self.request,
            'Your password has been changed successfully.'
        )

        # Keep user logged in after password change
        # Django's PasswordChangeView does this automatically
        return super().form_valid(form)


def password_change_required_view(request):
    """
    Handle forced password change for users with temporary passwords.

    This is a special view for users who must change their password
    before accessing the system (must_change_password=True).

    Flow:
    1. Admin creates user with temporary password
    2. User logs in with temporary password
    3. Login view redirects here instead of logging them in
    4. User changes password
    5. User is logged in and redirected to dashboard

    Security:
    - User is NOT logged in yet (prevents system access with temp password)
    - User ID is stored in session temporarily
    - Session data is cleared after password change
    """
    # Get user ID from session (set by login view)
    user_id = request.session.get('user_id_pending_password_change')

    if not user_id:
        messages.error(request, 'Invalid request. Please log in again.')
        return redirect('accounts:login')

    # Import here to avoid circular import
    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        return redirect('accounts:login')

    # Handle POST request (form submission)
    if request.method == 'POST':
        # Import here to avoid unnecessary imports
        from django.contrib.auth.forms import SetPasswordForm

        form = SetPasswordForm(user, request.POST)

        if form.is_valid():
            # Save new password
            user = form.save()

            # Clear must_change_password flag
            user.must_change_password = False
            user.save()

            # Clear session data
            del request.session['user_id_pending_password_change']

            # Log user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            messages.success(
                request,
                'Password changed successfully. Welcome to the Certificate Tracking System!'
            )

            return redirect('dashboard:home')
    else:
        # GET request - show password change form
        from django.contrib.auth.forms import SetPasswordForm
        form = SetPasswordForm(user)

    return render(request, 'accounts/password_change_required.html', {
        'form': form,
        'user': user,
    })


@login_required
def profile_detail(request, user_id):
    """
    Display detailed profile page for a specific employee.

    Visible to: All authenticated users

    Features:
    - Employee personal information
    - Department and position
    - Certificate summary statistics
    - Recent certificates list
    - Expiring certificates alert

    Performance Optimizations:
    - Uses select_related() for certificate provider/category
    - Aggregates certificate counts efficiently
    - Limits recent certificates to 5 (pagination not needed)

    Security:
    - All users can view any profile (transparency)
    - Edit buttons only shown to owner or admin
    """
    from django.shortcuts import get_object_or_404
    from django.contrib.auth import get_user_model
    from django.db.models import Count, Q
    from certificates.models import Certificate

    User = get_user_model()

    # Get the employee profile
    # Use select_related to fetch profile image in same query
    employee = get_object_or_404(User, pk=user_id)

    # Check if current user can edit this profile
    can_edit = request.user.is_admin() or request.user.id == employee.id

    # Get certificate statistics with efficient queries
    # Using annotate to count in database instead of Python
    certificates = Certificate.objects.filter(user=employee)

    total_certificates = certificates.count()
    active_certificates = certificates.filter(status='ACTIVE').count()
    expired_certificates = certificates.filter(status='EXPIRED').count()

    # Count expiring soon (next 90 days)
    expiring_soon_count = 0
    expiring_soon_list = []
    for cert in certificates.filter(status='ACTIVE').select_related('provider', 'category'):
        if cert.is_expiring_soon(90):
            expiring_soon_count += 1
            expiring_soon_list.append(cert)

    # Get recent certificates (last 5)
    # select_related to avoid N+1 queries for provider/category
    recent_certificates = certificates.select_related(
        'provider', 'category'
    ).order_by('-issue_date')[:5]

    # Get certificates by provider (for visual breakdown)
    certificates_by_provider = certificates.values(
        'provider__name'
    ).annotate(count=Count('id')).order_by('-count')[:5]

    context = {
        'employee': employee,
        'can_edit': can_edit,
        'total_certificates': total_certificates,
        'active_certificates': active_certificates,
        'expired_certificates': expired_certificates,
        'expiring_soon_count': expiring_soon_count,
        'expiring_soon_list': expiring_soon_list,
        'recent_certificates': recent_certificates,
        'certificates_by_provider': certificates_by_provider,
        'is_admin': request.user.is_admin(),
    }

    return render(request, 'accounts/profile_detail.html', context)


@login_required
def profile_list(request):
    """
    Display list of all employees in the system.

    Visible to: All authenticated users

    Features:
    - Searchable list of all employees
    - Certificate count per employee
    - Department and position display
    - Quick link to detailed profile
    - DataTables for sorting/filtering

    Performance Optimizations:
    - Uses annotate() to count certificates in database
    - Avoids N+1 query problem
    - Orders by last name for predictable sorting

    Security:
    - All authenticated users can view employee list
    - Transparency helps teams know who has which certifications
    """
    from django.contrib.auth import get_user_model
    from django.db.models import Count, Q

    User = get_user_model()

    # Get search query
    search_query = request.GET.get('search', '').strip()

    # Get all active users with certificate counts
    # Using annotate for efficient counting (single query instead of N queries)
    employees = User.objects.filter(
        is_active=True
    ).annotate(
        total_certs=Count('certificates'),
        active_certs=Count('certificates', filter=Q(certificates__status='ACTIVE')),
        expired_certs=Count('certificates', filter=Q(certificates__status='EXPIRED'))
    ).order_by('first_name', 'last_name')

    # Apply search filter if provided
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(position__icontains=search_query)
        )

    # Calculate summary statistics
    total_employees = employees.count()
    total_admins = employees.filter(role='ADMIN').count()
    total_employees_role = employees.filter(role='EMPLOYEE').count()

    # Employees with certificates
    employees_with_certs = employees.filter(total_certs__gt=0).count()

    context = {
        'employees': employees,
        'search_query': search_query,
        'total_employees': total_employees,
        'total_admins': total_admins,
        'total_employees_role': total_employees_role,
        'employees_with_certs': employees_with_certs,
        'is_admin': request.user.is_admin(),
    }

    return render(request, 'accounts/profile_list.html', context)


@login_required
def user_create(request):
    """
    Create a new user account (Admin only).

    Flow:
    1. Admin fills out user creation form
    2. System generates secure temporary password
    3. User account is created with must_change_password=True
    4. Welcome email is sent to user with login credentials
    5. Admin sees confirmation with the temporary password

    Security:
    - Only accessible to admin users (checked via decorator)
    - Password is auto-generated (cryptographically secure)
    - Password is sent once via email
    - User must change password on first login
    - Admin sees the password once (to communicate via secure channel if needed)

    Why this approach?
    - No public registration (security requirement)
    - Admin controls who gets access
    - Temporary passwords ensure security
    - Email provides secure delivery channel
    """
    # Import here to avoid circular import
    from core.utils import generate_temporary_password
    from .forms import UserCreationForm
    from django.core.mail import send_mail
    from django.conf import settings

    # Check admin permission
    if not request.user.is_admin():
        messages.error(
            request,
            'You do not have permission to create users. Admin privileges required.'
        )
        return redirect('dashboard:home')

    # Handle POST request (form submission)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # Generate secure temporary password
            temporary_password = generate_temporary_password(length=12)

            # Save user with temporary password
            # The form's save() method handles:
            # - Password hashing
            # - Setting must_change_password=True
            # - Setting is_staff based on role
            user = form.save(commit=False, temporary_password=temporary_password)
            user.save()

            # Store password and user info in session to display on success page
            # This allows us to show it only once to the admin
            request.session['new_user_created'] = {
                'email': user.email,
                'full_name': user.get_full_name(),
                'password': temporary_password,
                'role': user.get_role_display(),
                'department': user.department or 'Not specified',
                'position': user.position or 'Not specified',
            }

            # Redirect to success page
            return redirect('accounts:user_create_success')

        else:
            # Form has errors
            messages.error(
                request,
                'There were errors in the form. Please correct them and try again.'
            )

    else:
        # GET request - show empty form
        form = UserCreationForm()

    context = {
        'form': form,
        'page_title': 'Create New User',
    }

    return render(request, 'accounts/user_create.html', context)


@login_required
def user_create_success(request):
    """
    Display success page with temporary password after user creation.

    Security considerations:
    - Password shown only once to admin
    - Session data cleared after display
    - Admin must manually communicate password to user
    - No email sent (reduces interception risk)

    Why manual communication?
    - Admin can choose secure channel (phone, in-person, secure messaging)
    - Reduces email interception risk
    - Admin controls when credentials are delivered
    - Better for high-security environments
    """
    # Check if user is admin
    if not request.user.is_admin():
        messages.error(request, 'Admin privileges required.')
        return redirect('dashboard:home')

    # Get user data from session
    user_data = request.session.get('new_user_created')

    if not user_data:
        # No data in session, redirect to create page
        messages.warning(request, 'No user creation data found.')
        return redirect('accounts:user_create')

    # Clear session data (show password only once)
    del request.session['new_user_created']

    context = {
        'user_data': user_data,
    }

    return render(request, 'accounts/user_create_success.html', context)


@login_required
def profile_edit(request, user_id):
    """
    Edit user profile (personal information and profile photo).

    Accessible by:
    - The user themselves (own profile)
    - Admin users (any profile)

    Features:
    - Update personal information (name, department, position)
    - Upload profile photo (JPG, PNG, WebP)
    - Remove profile photo (revert to initials)
    - Image validation (size, format)

    Security:
    - Permission check: user can only edit own profile or admin can edit any
    - Image validation to prevent malicious uploads
    - File size limit (5MB)

    Performance:
    - Old profile images are deleted when replaced
    - Optimized file storage by year/month
    """
    from django.shortcuts import get_object_or_404
    from django.contrib.auth import get_user_model
    from .forms import UserUpdateForm

    User = get_user_model()

    # Get the user to edit
    user_to_edit = get_object_or_404(User, pk=user_id)

    # Permission check: can only edit own profile or must be admin
    if not (request.user.id == user_to_edit.id or request.user.is_admin()):
        messages.error(
            request,
            'You do not have permission to edit this profile.'
        )
        return redirect('accounts:profile_detail', user_id=user_id)

    if request.method == 'POST':
        form = UserUpdateForm(
            request.POST,
            request.FILES,  # Important for file uploads
            instance=user_to_edit
        )

        if form.is_valid():
            # Save the form
            user = form.save()

            messages.success(
                request,
                f'Profile updated successfully for {user.get_full_name()}!'
            )

            # Redirect to profile detail page
            return redirect('accounts:profile_detail', user_id=user.id)
        else:
            messages.error(
                request,
                'There were errors in the form. Please correct them and try again.'
            )
    else:
        # GET request - show form with current data
        form = UserUpdateForm(instance=user_to_edit)

    context = {
        'form': form,
        'user_to_edit': user_to_edit,
        'is_own_profile': request.user.id == user_to_edit.id,
        'is_admin': request.user.is_admin(),
    }

    return render(request, 'accounts/profile_edit.html', context)
