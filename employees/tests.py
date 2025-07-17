from django.test import TestCase
from rest_framework.test import APIClient
from employees.models import Organization, Employee


class EmployeeAPITestCase(TestCase):
    """
    Test suite for the Employee API endpoints.

    Covers:
    - Listing employees
    - Searching employees by name
    - Filtering employees by status
    - Validating invalid filters
    - Creating a new employee
    """

    def setUp(self):
        """
        Set up a test organization and sample employees.
        """
        self.client = APIClient()
        self.organization = Organization.objects.create(name="TestOrg", config={})
        self.base_url = f"/api/organizations/{self.organization.id}/employees/"

        self.emp1 = Employee.objects.create(
            organization=self.organization,
            first_name="Alice",
            last_name="Smith",
            department="HR",
            location="Pune",
            position="Manager",
            status=Employee.Status.ACTIVE,
        )
        self.emp2 = Employee.objects.create(
            organization=self.organization,
            first_name="Bob",
            last_name="Johnson",
            department="Tech",
            location="Bangalore",
            position="Developer",
            status=Employee.Status.TERMINATED,
        )

    def test_list_employees(self):
        """
        Test retrieving the list of employees for an organization.
        """
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_search_employee(self):
        """
        Test searching employees by first name.
        """
        response = self.client.get(self.base_url + "?search=alice")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["first_name"].lower(), "alice")

    def test_filter_by_status(self):
        """
        Test filtering employees by valid status (e.g., active).
        """
        response = self.client.get(self.base_url + "?status=active")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "active")

    def test_invalid_status_filter(self):
        """
        Test filtering employees with an invalid status value.
        Should return a 400 error.
        """
        response = self.client.get(self.base_url + "?status=invalidstatus")
        self.assertEqual(response.status_code, 400)

    def test_create_employee(self):
        """
        Test creating a new employee under an organization.
        """
        payload = {
            "first_name": "Charlie",
            "last_name": "Brown",
            "department": "Finance",
            "location": "Delhi",
            "position": "Analyst",
            "status": "active"
        }
        response = self.client.post(self.base_url, data=payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["first_name"], "Charlie")
