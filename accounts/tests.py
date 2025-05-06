# accounts/tests.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url    = reverse("token_obtain_pair")
        self.dashboard_url = reverse("dashboard")

    def test_registration_and_login_flow(self):
        # 1) Registration
        data = {
            "fullname":        "Test User",
            "email":           "test@example.com",
            "password":        "pass1234",
            "confirmPassword": "pass1234",
            "is_instructor":   False
        }
        resp = self.client.post(self.register_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)
        self.assertIn("user", resp.data)

        # 2) Login
        resp2 = self.client.post(self.login_url, {
            "username": "test@example.com",
            "password": "pass1234"
        }, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        token = resp2.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # 3) Access dashboard
        resp3 = self.client.get(self.dashboard_url)
        self.assertEqual(resp3.status_code, status.HTTP_200_OK)
        self.assertEqual(resp3.data["role"], "student")

    def test_invalid_registration(self):
        # missing confirmPassword
        data = {
            "fullname": "Test User",
            "email":    "test2@example.com",
            "password": "pass1234"
        }
        resp = self.client.post(self.register_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirmPassword", resp.data)
