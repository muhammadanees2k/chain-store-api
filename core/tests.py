# core/tests.py
import re
from django.core import mail
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class AuthEndpointsTests(APITestCase):
    
    def setUp(self):
        """This runs before every single test to set up a clean environment."""
        self.user_data = {
            "username": "tester",
            "password": "StrongPassword123!",
            "email": "tester@test.com",
            "first_name": "Test",
            "last_name": "User"
        }
        # Pre-create a user for endpoints that require login
        self.user = User.objects.create_user(**self.user_data)
        
        # Helper variable for URLs
        self.users_url = '/auth/users/'
        self.me_url = '/auth/users/me/'
        self.jwt_create_url = '/auth/jwt/create/'
        self.jwt_refresh_url = '/auth/jwt/refresh/'
        self.jwt_verify_url = '/auth/jwt/verify/'

    def authenticate_client(self):
        """Helper method to log in and attach the JWT token to the test client."""
        response = self.client.post(self.jwt_create_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        return response.data['refresh']

    # --- 1. REGISTRATION TESTS ---
    def test_user_registration(self):
        new_user_data = {
            "username": "newuser",
            "password": "NewPassword123!",
            "email": "new@test.com",
        }
        response = self.client.post(self.users_url, new_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    # --- 2. JWT TOKEN TESTS ---
    def test_jwt_lifecycle(self):
        # A. Create Token
        response = self.client.post(self.jwt_create_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        refresh_token = response.data['refresh']

        # B. Verify Token
        verify_response = self.client.post(self.jwt_verify_url, {"token": access_token})
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

        # C. Refresh Token
        refresh_response = self.client.post(self.jwt_refresh_url, {"refresh": refresh_token})
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    # --- 3. PROFILE MANAGEMENT TESTS (/me/) ---
    def test_retrieve_and_update_profile(self):
        self.authenticate_client()

        # A. GET /me/
        get_response = self.client.get(self.me_url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['username'], self.user_data['username'])

        # B. PATCH /me/ (Partial Update with nested customer profile)
        patch_data = {
            "first_name": "UpdatedName",
            "customer_profile": {
                "phone": "555-9999"
            }
        }
        patch_response = self.client.patch(self.me_url, patch_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['first_name'], "UpdatedName")
        self.assertEqual(patch_response.data['customer_profile']['phone'], "555-9999")

    # --- 4. PASSWORD MANAGEMENT TESTS ---
    def test_set_password(self):
        self.authenticate_client()
        
        # Change password via /set_password/
        data = {
            "new_password": "NewStrongPassword123!",
            "current_password": self.user_data["password"]
        }
        response = self.client.post(self.users_url + 'set_password/', data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify old password no longer works
        fail_login = self.client.post(self.jwt_create_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })
        self.assertEqual(fail_login.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_flow(self):
        """Advanced Test: Intercepts the email to test the reset token."""
        # A. Request Password Reset
        response = self.client.post(self.users_url + 'reset_password/', {"email": self.user_data["email"]})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify an email was placed in the Django outbox
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body

        # Extract UID and Token from the email using Regex
        # Matches the format: password/reset/confirm/{uid}/{token}
        match = re.search(r'password/reset/confirm/(?P<uid>[\w-]+)/(?P<token>[\w-]+)', email_body)
        self.assertIsNotNone(match, "Could not find reset link in email.")
        
        uid = match.group('uid')
        token = match.group('token')

        # B. Confirm Password Reset
        reset_data = {
            "uid": uid,
            "token": token,
            "new_password": "CompletelyNewPassword123!"
        }
        confirm_response = self.client.post(self.users_url + 'reset_password_confirm/', reset_data)
        self.assertEqual(confirm_response.status_code, status.HTTP_204_NO_CONTENT)

    # --- 5. ACCOUNT DELETION TEST ---
    def test_delete_account(self):
        self.authenticate_client()
        
        # Djoser requires the current password to delete an account to prevent accidental deletion
        response = self.client.delete(self.me_url, {"current_password": self.user_data["password"]})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify user is gone from the database
        self.assertFalse(User.objects.filter(username=self.user_data["username"]).exists())