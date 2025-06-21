"""Test User APIs"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:register')
TOKEN_URL = reverse('user:login')
ME_URL = reverse('user:me')
UPDATE_PASSWORD_URL = reverse('user:update-password')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


def payload(**params):
    """Test Payload"""
    payload = {
        'email': 'test@example.com',
        'password': 'testpass123',
        'name': 'Test Name'
    }
    payload.update(**params)
    return payload


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful"""
        pLoad = payload()
        res = self.client.post(CREATE_USER_URL, pLoad)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=pLoad['email'])
        self.assertTrue(user.check_password(pLoad['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        pLoad = payload()
        create_user(**pLoad)
        res = self.client.post(CREATE_USER_URL, pLoad)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 6 chars."""
        pLoad = payload(password='pw')
        res = self.client.post(CREATE_USER_URL, pLoad)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=pLoad['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = payload()
        create_user(**user_details)
        pLoad = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, pLoad)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid"""
        user_details = payload()
        create_user(**user_details)
        pLoad = {'email': 'test@example.com', 'password': 'badpass'}
        res = self.client.post(TOKEN_URL, pLoad)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test posting a blank password returns an error."""
        pLoad = payload(password='')
        res = self.client.post(TOKEN_URL, pLoad)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        pLoad = payload()
        self.user = create_user(**pLoad)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], self.user.email)
        self.assertEqual(res.data['name'], self.user.name)

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the me endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        pLoad = {'name': 'Updated Name'}
        res = self.client.patch(ME_URL, pLoad)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, pLoad['name'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_update_password_success(self):
        """Test successfully updating the user's password."""
        payload = {
            'old_password': 'testpass123',
            'new_password': 'newpassword123'
        }
        res = self.client.patch(UPDATE_PASSWORD_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(payload['new_password']))
        self.assertEqual(res.data['message'], 'Password updated successfully.')

    def test_update_password_invalid_old_password(self):
        """Test updating with an incorrect old password fails."""
        payload = {
            'old_password': 'wrongpassword123',
            'new_password': 'newpassword123'
        }
        res = self.client.patch(UPDATE_PASSWORD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', res.data)

    def test_update_password_too_short(self):
        """Test updating with a too-short new password fails."""
        payload = {
            'old_password': 'testpass123',
            'new_password': 'short'
        }
        res = self.client.patch(UPDATE_PASSWORD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', res.data)

    def test_update_password_missing_fields(self):
        """Test updating without providing required fields fails."""
        payload = {'old_password': 'testpass123'}
        res = self.client.patch(UPDATE_PASSWORD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        payload = {'new_password': 'newpassword123'}
        res = self.client.patch(UPDATE_PASSWORD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_password_not_authenticated(self):
        """Test updating password fails if the user is not authenticated."""
        self.client.force_authenticate(user=None)
        payload = {
            'old_password': 'testpass123',
            'new_password': 'newpassword123'
        }
        res = self.client.patch(UPDATE_PASSWORD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_email_read_only_on_update(self):
    #     """Test that email cannot be updated via the API."""
    #     old_email = self.user.email
    #     res = self.client.patch(ME_URL, {'email': 'newemail@example.com'})
    #     self.user.refresh_from_db()
    #     self.assertEqual(self.user.email, old_email)
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertNotEqual(self.user.email, 'newemail@example.com')
