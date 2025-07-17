from django.urls import path
from .views import (
    OrganizationListCreateView,
    EmployeeListCreateView,
)

urlpatterns = [
    path('organizations/', OrganizationListCreateView.as_view(), name='organization-list-create'),
    path('organizations/<int:organization_id>/employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
]
