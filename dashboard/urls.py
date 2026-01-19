"""
URL configuration for dashboard app (placeholder for Step 9).
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
]
