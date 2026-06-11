from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile

class AccountsTestCase(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'securepassword123'
        self.email = 'test@example.com'

    def test_user_registration_creates_profile(self):
        """Registering a new user should automatically create a UserProfile via Django signals."""
        user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.currency, 'USD')
        self.assertEqual(user.profile.monthly_budget_limit, 0.0)

    def test_login_redirect(self):
        """An unauthenticated request to the dashboard should redirect to the login page."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_login_success(self):
        """Logging in with valid credentials should successfully authenticate and redirect."""
        User.objects.create_user(
            username=self.username,
            password=self.password,
            email=self.email
        )
        response = self.client.post(
            reverse('login'),
            {'username': self.username, 'password': self.password}
        )
        # Redirects to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))
