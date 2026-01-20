"""
URL configuration for certificates app.

Routes:
- Employee overview (list of employees with certificate counts)
- Employee certificates (all certificates for one employee)
- View certificate details
- Create new certificates
- Edit existing certificates
- Delete certificates
- My certificates (user-specific view)
- Statistics dashboard
"""

from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    # Employee overview (main list page)
    path('', views.certificate_list, name='list'),

    # Employee's certificates (detail view for one employee)
    path('employee/<int:user_id>/', views.employee_certificates, name='employee_certificates'),

    # My certificates (user-specific)
    path('my/', views.my_certificates, name='my_certificates'),

    # Statistics
    path('statistics/', views.certificate_statistics, name='statistics'),

    # Create
    path('create/', views.certificate_create, name='create'),

    # Detail, Update, Delete (pk-based)
    path('<int:pk>/', views.certificate_detail, name='detail'),
    path('<int:pk>/edit/', views.certificate_update, name='update'),
    path('<int:pk>/delete/', views.certificate_delete, name='delete'),
]
