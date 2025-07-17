from django.db import models


class Organization(models.Model):
    """
    Represents an organization entity.

    Fields:
        - name: Name of the organization.
        - config: JSON field that stores configuration related to which employee fields should be visible.
    """
    name = models.CharField(max_length=255)
    config = models.JSONField(help_text="List of visible fields for employees in this org", default=dict, blank=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    """
    Represents an employee within an organization.

    Fields:
        - organization: ForeignKey to the related organization.
        - first_name, last_name: Personal identification fields.
        - contact_email, contact_phone: Contact information.
        - department, position, location: Work-related metadata.
        - status: Current status of the employee (active, not_started, terminated).
    """

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        NOT_STARTED = 'not_started', 'Not Started'
        TERMINATED = 'terminated', 'Terminated'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='employees')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    contact_email = models.EmailField(default="", blank=True)
    contact_phone = models.CharField(max_length=15, default="", blank=True)
    department = models.CharField(max_length=255, default="", blank=True)
    position = models.CharField(max_length=255, default="", blank=True)
    location = models.CharField(max_length=255, default="", blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
