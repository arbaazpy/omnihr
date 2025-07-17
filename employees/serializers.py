from rest_framework import serializers
from .models import Organization, Employee

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name", "config"]
        read_only_fields = ["config"]


class DynamicEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id", "first_name", "last_name",
            "contact_email", "contact_phone",
            "department", "location", "position",
            "status"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        org_config = self.context.get("org_config", {})
        hide_columns = org_config.get("hide_columns", [])

        for field in hide_columns:
            if field in self.fields:
                self.fields.pop(field)
