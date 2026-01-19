from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_home(request):
    """
    Company dashboard homepage (placeholder for Step 9).

    This will show:
    - Total employees
    - Total certificates
    - Certificates by provider
    - Certificates by category
    - Recently added certificates
    - Certificates expiring soon
    - Skill distribution charts
    """
    context = {
        'page_title': 'Dashboard',
    }
    return render(request, 'dashboard/home.html', context)
