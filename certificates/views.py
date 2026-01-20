"""
Views for certificate CRUD operations.

This module provides views for:
- Listing certificates (with DataTables)
- Viewing certificate details
- Creating new certificates
- Updating existing certificates
- Deleting certificates

Permission Rules:
- All authenticated users can view certificates
- Employees can create certificates for themselves
- Employees can edit/delete only their own certificates
- Admins can create/edit/delete any certificate
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator

from core.permissions import check_object_permission
from .models import Certificate, CertificateProvider, CertificateCategory
from .forms import CertificateForm, CertificateFilterForm


@login_required
def certificate_list(request):
    """
    Display employee overview with certificate counts.

    Permissions:
    - All authenticated users can view
    - Shows list of all employees who have certificates
    - Displays certificate counts per employee

    Features:
    - Employee list with aggregate certificate counts
    - Statistics cards showing company-wide metrics
    - Search functionality for employee names
    - DataTables for sorting and pagination
    - Click to view individual employee's certificates
    """
    from accounts.models import User

    # Get search query
    search_query = request.GET.get('search', '').strip()

    # Get all users who have at least one certificate
    # Use annotate to add certificate counts efficiently (avoid N+1 queries)
    employees = User.objects.annotate(
        total_certs=Count('certificates'),
        active_certs=Count('certificates', filter=Q(certificates__status='ACTIVE')),
        expired_certs=Count('certificates', filter=Q(certificates__status='EXPIRED'))
    ).filter(total_certs__gt=0).order_by('first_name', 'last_name')

    # Apply search filter
    if search_query:
        employees = employees.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Calculate company-wide statistics
    all_certificates = Certificate.objects.all()
    total_certificates = all_certificates.count()
    active_certificates = all_certificates.filter(status='ACTIVE').count()
    expired_certificates = all_certificates.filter(status='EXPIRED').count()

    # Count expiring soon (certificates expiring in next 90 days)
    expiring_soon_count = 0
    for cert in all_certificates.filter(status='ACTIVE'):
        if cert.is_expiring_soon(90):
            expiring_soon_count += 1

    context = {
        'employees': employees,
        'search_query': search_query,
        'total_certificates': total_certificates,
        'active_certificates': active_certificates,
        'expired_certificates': expired_certificates,
        'expiring_soon_count': expiring_soon_count,
        'total_employees': employees.count(),
        'is_admin': request.user.is_admin(),
    }

    return render(request, 'certificates/employee_list.html', context)


@login_required
def employee_certificates(request, user_id):
    """
    Display all certificates for a specific employee.

    Permissions:
    - All authenticated users can view any employee's certificates
    - Shows edit/delete buttons based on permissions

    Features:
    - List of all certificates for one employee
    - DataTables for sorting and searching
    - Employee statistics (active, expired, expiring soon)
    - Permission-based action buttons
    - Breadcrumb navigation back to employee list
    """
    from accounts.models import User

    # Get the employee
    employee = get_object_or_404(User, pk=user_id)

    # Get all certificates for this employee
    certificates = Certificate.objects.filter(
        user=employee
    ).select_related('provider', 'category').order_by('-issue_date')

    # Calculate statistics for this employee
    total_certificates = certificates.count()
    active_certificates = certificates.filter(status='ACTIVE').count()
    expired_certificates = certificates.filter(status='EXPIRED').count()

    # Count expiring soon (certificates expiring in next 90 days)
    expiring_soon_count = 0
    expiring_soon_list = []
    for cert in certificates.filter(status='ACTIVE'):
        if cert.is_expiring_soon(90):
            expiring_soon_count += 1
            expiring_soon_list.append(cert)

    context = {
        'employee': employee,
        'certificates': certificates,
        'total_certificates': total_certificates,
        'active_certificates': active_certificates,
        'expired_certificates': expired_certificates,
        'expiring_soon_count': expiring_soon_count,
        'expiring_soon_list': expiring_soon_list,
        'is_admin': request.user.is_admin(),
    }

    return render(request, 'certificates/employee_certificates.html', context)


@login_required
def certificate_detail(request, pk):
    """
    Display detailed view of a single certificate.

    Permissions:
    - All authenticated users can view any certificate
    - Shows edit/delete buttons only if user has permission

    Features:
    - Full certificate information
    - File download link
    - Verification URL link
    - Expiry status with color coding
    - Days until expiry calculation
    - Related certificates from same provider
    """

    certificate = get_object_or_404(
        Certificate.objects.select_related('user', 'provider', 'category'),
        pk=pk
    )

    # Check if current user can edit this certificate
    can_edit = check_object_permission(request, certificate, 'user')

    # Get related certificates from same provider (exclude current)
    related_certificates = Certificate.objects.filter(
        provider=certificate.provider
    ).exclude(pk=certificate.pk).select_related('user')[:5]

    # Calculate days for display (handle negative values)
    days_until_expiry = certificate.days_until_expiry()
    days_expired = None
    if days_until_expiry is not None and days_until_expiry < 0:
        days_expired = abs(days_until_expiry)

    context = {
        'certificate': certificate,
        'can_edit': can_edit,
        'related_certificates': related_certificates,
        'is_admin': request.user.is_admin(),
        'days_expired': days_expired,
    }

    return render(request, 'certificates/certificate_detail.html', context)


@login_required
def certificate_create(request):
    """
    Create a new certificate.

    Permissions:
    - All authenticated users can create certificates
    - Employees can only create for themselves
    - Admins can create for any user

    Flow:
    1. Display empty form
    2. User fills in certificate details
    3. Validate and save
    4. Redirect to certificate detail page
    """

    is_admin = request.user.is_admin()

    if request.method == 'POST':
        form = CertificateForm(
            request.POST,
            request.FILES,
            current_user=request.user,
            is_admin=is_admin
        )

        if form.is_valid():
            certificate = form.save(commit=False)

            # If not admin, ensure user is set to current user
            if not is_admin:
                certificate.user = request.user

            certificate.save()

            messages.success(
                request,
                f'Certificate "{certificate.name}" has been created successfully!'
            )

            return redirect('certificates:detail', pk=certificate.pk)
        else:
            messages.error(
                request,
                'There were errors in the form. Please correct them and try again.'
            )
    else:
        # GET request - show empty form
        form = CertificateForm(
            current_user=request.user,
            is_admin=is_admin
        )

    # Get all active providers for autocomplete
    all_providers = CertificateProvider.objects.filter(is_active=True).order_by('name')

    context = {
        'form': form,
        'is_admin': is_admin,
        'page_title': 'Add New Certificate',
        'all_providers': all_providers,
    }

    return render(request, 'certificates/certificate_form.html', context)


@login_required
def certificate_update(request, pk):
    """
    Update an existing certificate.

    Permissions:
    - User must own the certificate OR be an admin
    - Redirects with error if no permission

    Flow:
    1. Check permission
    2. Display form with current data
    3. User updates fields
    4. Validate and save
    5. Redirect to certificate detail page
    """

    certificate = get_object_or_404(Certificate, pk=pk)
    is_admin = request.user.is_admin()

    # Check permission
    if not check_object_permission(request, certificate, 'user'):
        messages.error(
            request,
            'You do not have permission to edit this certificate. '
            'You can only edit your own certificates.'
        )
        return redirect('certificates:list')

    if request.method == 'POST':
        form = CertificateForm(
            request.POST,
            request.FILES,
            instance=certificate,
            current_user=request.user,
            is_admin=is_admin
        )

        if form.is_valid():
            updated_certificate = form.save()

            messages.success(
                request,
                f'Certificate "{updated_certificate.name}" has been updated successfully!'
            )

            return redirect('certificates:detail', pk=updated_certificate.pk)
        else:
            messages.error(
                request,
                'There were errors in the form. Please correct them and try again.'
            )
    else:
        # GET request - show form with current data
        form = CertificateForm(
            instance=certificate,
            current_user=request.user,
            is_admin=is_admin
        )

    # Get all active providers for autocomplete
    all_providers = CertificateProvider.objects.filter(is_active=True).order_by('name')

    context = {
        'form': form,
        'certificate': certificate,
        'is_admin': is_admin,
        'page_title': f'Edit Certificate: {certificate.name}',
        'all_providers': all_providers,
    }

    return render(request, 'certificates/certificate_form.html', context)


@login_required
def certificate_delete(request, pk):
    """
    Delete a certificate.

    Permissions:
    - User must own the certificate OR be an admin
    - Requires POST request for safety

    Flow:
    1. Check permission
    2. Show confirmation page (GET)
    3. Delete on confirmation (POST)
    4. Redirect to certificate list
    """

    certificate = get_object_or_404(Certificate, pk=pk)

    # Check permission
    if not check_object_permission(request, certificate, 'user'):
        messages.error(
            request,
            'You do not have permission to delete this certificate. '
            'You can only delete your own certificates.'
        )
        return redirect('certificates:list')

    if request.method == 'POST':
        # User confirmed deletion
        certificate_name = certificate.name
        certificate.delete()

        messages.success(
            request,
            f'Certificate "{certificate_name}" has been deleted successfully.'
        )

        return redirect('certificates:list')

    # GET request - show confirmation page
    context = {
        'certificate': certificate,
    }

    return render(request, 'certificates/certificate_confirm_delete.html', context)


@login_required
def my_certificates(request):
    """
    Show only the current user's certificates.

    This is a convenience view for employees to see their own certificates.
    Different from certificate_list which shows all certificates.

    Features:
    - Filtered to current user only
    - Statistics specific to user
    - Quick access to add new certificate
    """

    # Get user's certificates
    certificates = Certificate.objects.filter(
        user=request.user
    ).select_related('provider', 'category')

    # Get statistics
    total_certificates = certificates.count()
    active_certificates = certificates.filter(status='ACTIVE').count()
    expired_certificates = certificates.filter(status='EXPIRED').count()

    # Count expiring soon
    expiring_soon_count = 0
    expiring_soon_list = []
    for cert in certificates.filter(status='ACTIVE'):
        if cert.is_expiring_soon(90):
            expiring_soon_count += 1
            expiring_soon_list.append(cert)

    context = {
        'certificates': certificates,
        'total_certificates': total_certificates,
        'active_certificates': active_certificates,
        'expired_certificates': expired_certificates,
        'expiring_soon_count': expiring_soon_count,
        'expiring_soon_list': expiring_soon_list,
    }

    return render(request, 'certificates/my_certificates.html', context)


@login_required
def certificate_statistics(request):
    """
    Show certificate statistics and analytics.

    Permissions:
    - Admins see company-wide statistics
    - Employees see only their own statistics

    Features:
    - Certificates by provider (chart data)
    - Certificates by category (chart data)
    - Expiry timeline
    - Top certified employees (admin only)
    """

    is_admin = request.user.is_admin()

    if is_admin:
        # Admin sees all certificates
        certificates = Certificate.objects.all()
    else:
        # Employee sees only their certificates
        certificates = Certificate.objects.filter(user=request.user)

    # Certificates by provider
    provider_stats = certificates.values('provider__name').annotate(
        count=Count('id')
    ).order_by('-count')

    # Certificates by category
    category_stats = certificates.values('category__name', 'category__color').annotate(
        count=Count('id')
    ).order_by('-count')

    # Certificates by status
    status_stats = certificates.values('status').annotate(
        count=Count('id')
    )

    # Expiring soon
    expiring_soon = []
    for cert in certificates.filter(status='ACTIVE'):
        if cert.is_expiring_soon(90):
            expiring_soon.append(cert)

    # Top certified employees (admin only)
    top_employees = None
    if is_admin:
        from accounts.models import User
        top_employees = User.objects.annotate(
            cert_count=Count('certificates')
        ).filter(cert_count__gt=0).order_by('-cert_count')[:10]

    context = {
        'is_admin': is_admin,
        'total_certificates': certificates.count(),
        'provider_stats': provider_stats,
        'category_stats': category_stats,
        'status_stats': status_stats,
        'expiring_soon': expiring_soon,
        'top_employees': top_employees,
    }

    return render(request, 'certificates/certificate_statistics.html', context)
