from rest_framework import generics
from .models import Organization, Employee
from .serializers import OrganizationSerializer, DynamicEmployeeSerializer
from utils.rate_limiter import is_rate_limited
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from django.db.models import Q


class OrganizationListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to create and list organizations.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class EmployeeListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to create and list employees under a given organization.

    Supports:
        - Filtering by employee status via `?status=active,terminated`
        - Searching across fields using `?search=some_name`
        - IP-based rate limiting for list endpoint
    """
    serializer_class = DynamicEmployeeSerializer

    def get_serializer_context(self):
        """
        Pass dynamic config to serializer to control visible fields.
        """
        context = super().get_serializer_context()
        try:
            org = Organization.objects.get(id=self.kwargs["organization_id"])
            context["org_config"] = org.config or {}
        except Organization.DoesNotExist:
            context["org_config"] = {}
        return context

    def get_queryset(self):
        """
        Return employees belonging to the organization, optionally filtered by status and search.
        """
        org_id = self.kwargs.get("organization_id")

        try:
            organization = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found.")

        queryset = Employee.objects.filter(organization=organization)

        # Filter by status
        status = self.request.query_params.get("status")
        if status:
            statuses = status.split(',')
            if not all(status in Employee.Status.values for status in statuses):
                raise ValidationError("Invalid status value.")
            queryset = queryset.filter(status__in=statuses)

        # Simple full-text search across key fields
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(department__icontains=search) |
                Q(location__icontains=search) |
                Q(position__icontains=search)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Apply basic IP rate limiting before returning the list response.
        """
        ip = request.META.get('REMOTE_ADDR')
        if is_rate_limited(ip):
            return Response(
                {"error": "Too many requests. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Attach organization before saving employee.
        """
        org_id = self.kwargs.get("organization_id")
        serializer.save(organization_id=org_id)
