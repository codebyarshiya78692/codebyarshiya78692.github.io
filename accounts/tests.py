from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class AccountsTests(TestCase):

    def test_login_page_loads(self):
        response = self.client.get(
            reverse("accounts:login")
        )

        self.assertEqual(response.status_code, 200)

    def test_user_can_login(self):
        User.objects.create_user(
            username="testuser",
            password="TestPassword123",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "testuser",
                "password": "TestPassword123",
            },
        )

        self.assertEqual(response.status_code, 302)

    def test_invalid_login_is_rejected(self):
        User.objects.create_user(
            username="testuser",
            password="TestPassword123",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "testuser",
                "password": "WrongPassword",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)