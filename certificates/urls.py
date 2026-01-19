"""
URL configuration for certificates app (placeholder for Step 7).
"""

from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

app_name = 'certificates'

urlpatterns = [
    # Placeholder - will be implemented in Step 7
    path('', login_required(TemplateView.as_view(template_name='certificates/placeholder.html')), name='list'),
]
