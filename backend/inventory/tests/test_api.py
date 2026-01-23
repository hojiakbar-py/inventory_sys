"""
API endpoint tests for Inventory Management System.

Tests CRUD operations for all main API endpoints.
"""

from decimal import Decimal
from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

from inventory.models import (
    Branch, Department, Employee, EquipmentCategory,
    Equipment, Assignment
)
from inventory.constants import EquipmentStatus


class BranchAPITest(APITestCase):
    """Tests for Branch API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test Address",
            city="Tashkent"
        )

    def test_list_branches(self):
        """Test listing branches."""
        url = reverse('branch-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_branch(self):
        """Test creating a branch."""
        url = reverse('branch-list')
        data = {
            "code": "SAM-001",
            "name": "Samarkand Office",
            "address": "Registan 1",
            "city": "Samarkand"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Branch.objects.filter(code="SAM-001").exists())

    def test_retrieve_branch(self):
        """Test retrieving a branch."""
        url = reverse('branch-detail', kwargs={'pk': self.branch.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'TSK-001')

    def test_update_branch(self):
        """Test updating a branch."""
        url = reverse('branch-detail', kwargs={'pk': self.branch.pk})
        data = {
            "code": "TSK-001",
            "name": "Updated Tashkent Office",
            "address": "New Address",
            "city": "Tashkent"
        }
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.branch.refresh_from_db()
        self.assertEqual(self.branch.name, "Updated Tashkent Office")

    def test_delete_branch(self):
        """Test deleting a branch."""
        url = reverse('branch-detail', kwargs={'pk': self.branch.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Branch.objects.filter(pk=self.branch.pk).exists())


class DepartmentAPITest(APITestCase):
    """Tests for Department API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.department = Department.objects.create(
            code="IT",
            name="Information Technology",
            branch=self.branch
        )

    def test_list_departments(self):
        """Test listing departments."""
        url = reverse('department-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_department(self):
        """Test creating a department."""
        url = reverse('department-list')
        data = {
            "code": "HR",
            "name": "Human Resources",
            "branch": self.branch.pk
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Department.objects.filter(code="HR").exists())


class EmployeeAPITest(APITestCase):
    """Tests for Employee API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.department = Department.objects.create(
            code="IT",
            name="IT",
            branch=self.branch
        )
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            branch=self.branch,
            department=self.department,
            position="Engineer"
        )

    def test_list_employees(self):
        """Test listing employees."""
        url = reverse('employee-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_employee(self):
        """Test creating an employee."""
        url = reverse('employee-list')
        data = {
            "employee_id": "EMP002",
            "first_name": "Jane",
            "last_name": "Smith",
            "branch": self.branch.pk,
            "department": self.department.pk,
            "position": "Manager"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Employee.objects.filter(employee_id="EMP002").exists())

    def test_retrieve_employee(self):
        """Test retrieving an employee."""
        url = reverse('employee-detail', kwargs={'pk': self.employee.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['employee_id'], 'EMP001')

    def test_search_employees(self):
        """Test searching employees."""
        url = reverse('employee-list')
        response = self.client.get(url, {'search': 'John'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EquipmentCategoryAPITest(APITestCase):
    """Tests for EquipmentCategory API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.category = EquipmentCategory.objects.create(
            code="COMP",
            name="Computers"
        )

    def test_list_categories(self):
        """Test listing categories."""
        url = reverse('equipmentcategory-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category(self):
        """Test creating a category."""
        url = reverse('equipmentcategory-list')
        data = {
            "code": "FURN",
            "name": "Furniture"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EquipmentAPITest(APITestCase):
    """Tests for Equipment API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.category = EquipmentCategory.objects.create(
            code="LAPTOP",
            name="Laptops"
        )
        self.department = Department.objects.create(
            code="IT",
            name="IT",
            branch=self.branch
        )
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            branch=self.branch,
            department=self.department,
            position="Engineer"
        )
        self.equipment = Equipment.objects.create(
            inventory_number="INV-001",
            name="Dell XPS 15",
            branch=self.branch,
            category=self.category,
            status=EquipmentStatus.AVAILABLE
        )

    def test_list_equipment(self):
        """Test listing equipment."""
        url = reverse('equipment-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_equipment(self):
        """Test creating equipment."""
        url = reverse('equipment-list')
        data = {
            "inventory_number": "INV-002",
            "name": "HP ProBook",
            "branch": self.branch.pk,
            "category": self.category.pk
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Equipment.objects.filter(inventory_number="INV-002").exists())

    def test_retrieve_equipment(self):
        """Test retrieving equipment."""
        url = reverse('equipment-detail', kwargs={'pk': self.equipment.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['inventory_number'], 'INV-001')

    def test_filter_equipment_by_status(self):
        """Test filtering equipment by status."""
        url = reverse('equipment-list')
        response = self.client.get(url, {'status': EquipmentStatus.AVAILABLE})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_assign_equipment(self):
        """Test assigning equipment to employee."""
        url = reverse('equipment-assign', kwargs={'pk': self.equipment.pk})
        data = {
            "employee": self.employee.pk,
            "condition_on_assignment": "Good condition",
            "purpose": "Work from home"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.status, EquipmentStatus.ASSIGNED)

    def test_return_equipment(self):
        """Test returning equipment."""
        # First assign the equipment
        Assignment.objects.create(
            equipment=self.equipment,
            employee=self.employee,
            assigned_by=self.user
        )
        self.equipment.status = EquipmentStatus.ASSIGNED
        self.equipment.save()

        url = reverse('equipment-return-equipment', kwargs={'pk': self.equipment.pk})
        data = {
            "condition_on_return": "Good condition",
            "return_notes": "All accessories included"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.status, EquipmentStatus.AVAILABLE)


class AssignmentAPITest(APITestCase):
    """Tests for Assignment API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.branch = Branch.objects.create(
            code="TSK-001",
            name="Tashkent Office",
            address="Test",
            city="Tashkent"
        )
        self.department = Department.objects.create(
            code="IT",
            name="IT",
            branch=self.branch
        )
        self.employee = Employee.objects.create(
            employee_id="EMP001",
            first_name="John",
            last_name="Doe",
            branch=self.branch,
            department=self.department,
            position="Engineer"
        )
        self.equipment = Equipment.objects.create(
            inventory_number="INV-001",
            name="Dell XPS 15",
            branch=self.branch,
            status=EquipmentStatus.AVAILABLE
        )
        self.assignment = Assignment.objects.create(
            equipment=self.equipment,
            employee=self.employee,
            assigned_by=self.user
        )

    def test_list_assignments(self):
        """Test listing assignments."""
        url = reverse('assignment-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_assignment(self):
        """Test retrieving an assignment."""
        url = reverse('assignment-detail', kwargs={'pk': self.assignment.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint."""
        url = reverse('assignment-dashboard-stats')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_equipment', response.data)
        self.assertIn('total_employees', response.data)


class HealthCheckAPITest(APITestCase):
    """Tests for health check endpoint."""

    def test_health_check(self):
        """Test health check endpoint."""
        url = reverse('health_check')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('database', response.data)
        self.assertIn('version', response.data)
