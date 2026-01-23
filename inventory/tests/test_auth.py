"""
Authentication tests for Inventory Management System.

Tests login, logout, registration, and password change functionality.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token


class AuthenticationAPITest(APITestCase):
    """Tests for authentication API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User"
        )
        self.token = Token.objects.create(user=self.user)

    def test_login_success(self):
        """Test successful login."""
        url = reverse('login')
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('login')
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        url = reverse('login')
        data = {
            "username": "testuser"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_success(self):
        """Test successful logout."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('logout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify token is deleted
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_without_auth(self):
        """Test logout without authentication."""
        url = reverse('logout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_register_success(self):
        """Test successful registration."""
        url = reverse('register')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_password_mismatch(self):
        """Test registration with password mismatch."""
        url = reverse('register')
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "differentpass",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_duplicate_username(self):
        """Test registration with existing username."""
        url = reverse('register')
        data = {
            "username": "testuser",  # Already exists
            "email": "another@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_current_user(self):
        """Test getting current user info."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('me')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_get_current_user_without_auth(self):
        """Test getting current user without authentication."""
        url = reverse('me')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """Test updating user profile."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('update_profile')
        data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")

    def test_change_password(self):
        """Test changing password."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('change_password')
        data = {
            "old_password": "testpass123",
            "new_password": "newpass456",
            "new_password_confirm": "newpass456"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify old password no longer works
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password("testpass123"))
        self.assertTrue(self.user.check_password("newpass456"))

    def test_change_password_wrong_old_password(self):
        """Test changing password with wrong old password."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('change_password')
        data = {
            "old_password": "wrongpass",
            "new_password": "newpass456",
            "new_password_confirm": "newpass456"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenAuthenticationTest(APITestCase):
    """Tests for token authentication."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.token = Token.objects.create(user=self.user)

    def test_access_protected_endpoint_with_token(self):
        """Test accessing protected endpoint with valid token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        url = reverse('me')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token."""
        url = reverse('me')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token."""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        url = reverse('me')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_created_on_login(self):
        """Test that token is created/returned on login."""
        # Delete existing token
        self.token.delete()

        url = reverse('login')
        data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertTrue(Token.objects.filter(user=self.user).exists())
