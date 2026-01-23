"""
Pytest configuration and fixtures for Inventory Management System.
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from inventory.models import Branch, Department, Employee, EquipmentCategory, Equipment


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User"
    )


@pytest.fixture
def auth_client(api_client, user):
    """Return an authenticated API client."""
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client


@pytest.fixture
def branch(db):
    """Create and return a test branch."""
    return Branch.objects.create(
        code="TSK-001",
        name="Tashkent Office",
        address="Test Address",
        city="Tashkent",
        country="Uzbekistan"
    )


@pytest.fixture
def department(db, branch):
    """Create and return a test department."""
    return Department.objects.create(
        code="IT",
        name="Information Technology",
        branch=branch
    )


@pytest.fixture
def employee(db, branch, department):
    """Create and return a test employee."""
    return Employee.objects.create(
        employee_id="EMP001",
        first_name="John",
        last_name="Doe",
        branch=branch,
        department=department,
        position="Software Engineer"
    )


@pytest.fixture
def category(db):
    """Create and return a test equipment category."""
    return EquipmentCategory.objects.create(
        code="LAPTOP",
        name="Laptops"
    )


@pytest.fixture
def equipment(db, branch, category):
    """Create and return a test equipment."""
    return Equipment.objects.create(
        inventory_number="INV-001",
        name="Dell XPS 15",
        branch=branch,
        category=category
    )
